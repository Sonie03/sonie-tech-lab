"""
GitHub API client for DevBuddy AI.
Fetches profile stats, contribution data, and calculates
commit streaks from the GitHub GraphQL + REST APIs.
"""
import requests
from datetime import datetime, timedelta


class GitHubClient:
    REST_URL    = "https://api.github.com"
    GRAPHQL_URL = "https://api.github.com/graphql"

    def __init__(self, username: str, token: str = ""):
        self.username = username
        self.token    = token
        self._headers = {"Accept": "application/vnd.github.v3+json"}
        if token:
            self._headers["Authorization"] = f"token {token}"

    # ------------------------------------------------------------------
    # REST – basic profile stats
    # ------------------------------------------------------------------
    def fetch_profile_stats(self) -> dict | None:
        if not self.username:
            return None
        try:
            r = requests.get(
                f"{self.REST_URL}/users/{self.username}",
                headers=self._headers, timeout=8
            )
            if r.status_code != 200:
                return None
            u = r.json()

            # Star count: sum across all repos
            stars = 0
            page  = 1
            while True:
                rr = requests.get(
                    f"{self.REST_URL}/users/{self.username}/repos",
                    headers=self._headers,
                    params={"per_page": 100, "page": page},
                    timeout=8,
                )
                if rr.status_code != 200 or not rr.json():
                    break
                for repo in rr.json():
                    stars += repo.get("stargazers_count", 0)
                page += 1

            return {
                "name":      u.get("name", self.username),
                "bio":       u.get("bio", ""),
                "repos":     u.get("public_repos", 0),
                "followers": u.get("followers", 0),
                "following": u.get("following", 0),
                "stars":     stars,
                "avatar_url": u.get("avatar_url", ""),
            }
        except Exception as e:
            print(f"[GitHub] profile error: {e}")
            return None

    # ------------------------------------------------------------------
    # REST – recent events for streak calculation
    # ------------------------------------------------------------------
    def fetch_streak(self) -> dict:
        """
        Returns {"current_streak": N, "longest_streak": N, "today_commits": N}
        by scanning the last 90 days of push events.
        """
        result = {"current_streak": 0, "longest_streak": 0, "today_commits": 0}
        if not self.username:
            return result
        try:
            commit_days: set[str] = set()
            today_str = datetime.utcnow().strftime("%Y-%m-%d")

            for page in range(1, 4):          # max 3 pages = 300 events
                r = requests.get(
                    f"{self.REST_URL}/users/{self.username}/events/public",
                    headers=self._headers,
                    params={"per_page": 100, "page": page},
                    timeout=8,
                )
                if r.status_code != 200:
                    break
                events = r.json()
                if not events:
                    break
                for ev in events:
                    if ev.get("type") != "PushEvent":
                        continue
                    day = ev["created_at"][:10]
                    commit_days.add(day)
                    if day == today_str:
                        result["today_commits"] += len(
                            ev.get("payload", {}).get("commits", [])
                        )

            # Calculate streaks
            current = 0
            longest = 0
            streak  = 0
            check   = datetime.utcnow().date()
            for _ in range(365):
                if check.isoformat() in commit_days:
                    streak += 1
                    longest = max(longest, streak)
                    if _ == 0 or streak > 0:
                        current = streak
                else:
                    if streak > 0 and _ > 0:
                        break        # streak broken
                    streak = 0
                check -= timedelta(days=1)

            result["current_streak"] = current
            result["longest_streak"] = longest
        except Exception as e:
            print(f"[GitHub] streak error: {e}")
        return result

    # ------------------------------------------------------------------
    # GraphQL – 52-week contribution grid
    # ------------------------------------------------------------------
    def fetch_contribution_grid(self) -> list[list[int]] | None:
        """
        Returns a list of 52 weeks, each a list of 7 day contribution counts.
        Requires a token with read:user scope.
        """
        if not self.token or not self.username:
            return None
        query = """
        query($login: String!) {
          user(login: $login) {
            contributionsCollection {
              contributionCalendar {
                weeks {
                  contributionDays {
                    contributionCount
                  }
                }
              }
            }
          }
        }
        """
        try:
            r = requests.post(
                self.GRAPHQL_URL,
                json={"query": query, "variables": {"login": self.username}},
                headers={**self._headers, "Authorization": f"bearer {self.token}"},
                timeout=10,
            )
            if r.status_code != 200:
                return None
            weeks_raw = (
                r.json()["data"]["user"]["contributionsCollection"]
                ["contributionCalendar"]["weeks"]
            )
            return [
                [day["contributionCount"] for day in week["contributionDays"]]
                for week in weeks_raw
            ]
        except Exception as e:
            print(f"[GitHub] contribution grid error: {e}")
            return None
