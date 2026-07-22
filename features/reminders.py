"""
Background reminder scheduler for DevBuddy AI.
Runs in a daemon thread and fires reminders based on
intervals stored in the SQLite database.
"""
import time
import random
import threading
from core.database import db
from features.notifications import send_notification

# --- DevOps Motivational Coaching Quotes ---
DEVOPS_QUOTES = [
    ("🚀 Keep Going!", "Great work! Keep building your DevOps skills."),
    ("💼 Career Goals", "You're one project closer to your dream job."),
    ("📈 Stay Consistent", "Consistency beats intensity. Show up every day."),
    ("🐳 Docker Master", "Today's Docker practice will help tomorrow's interview."),
    ("🏗️ CI/CD Builder", "Every pipeline you build makes you a better engineer."),
    ("☸️ K8s Journey", "Kubernetes is complex — but you're getting it. Keep going!"),
    ("☁️ Cloud Career", "AWS skills are in demand. Your effort is an investment."),
    ("🔧 Terraform Pro", "Infrastructure as Code is the future. You're on the right track."),
    ("🐧 Linux Power", "Master the terminal. Every command you learn counts."),
    ("📊 Monitoring Wins", "Prometheus + Grafana skills will set you apart. You've got this!"),
]

# --- Wellness Reminders ---
WELLNESS_REMINDERS = {
    "Water":          ("💧 Hydration Reminder", "Hey! Time to drink a glass of water. Stay hydrated!"),
    "Stretch":        ("🧘 Stretch Break",       "Take 2 minutes to stretch. Your back will thank you!"),
    "Eye (20-20-20)": ("👁️ Eye Care",           "Look at something 20 feet away for 20 seconds."),
    "Stand":          ("🦵 Stand Up",            "You've been sitting too long. Stand up and walk around!"),
    "Break":          ("☕ Short Break",         "Step away from the screen for 5 minutes. Rest helps focus."),
}


class ReminderScheduler:
    def __init__(self, app_manager):
        self.app_manager = app_manager
        self.running = False
        self._thread: threading.Thread | None = None
        # Per-type elapsed minute counters
        self._timers: dict[str, int] = {}

    def start(self):
        if self.running:
            return
        self.running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self.running = False

    # ------------------------------------------------------------------
    def _get_intervals(self) -> dict[str, int]:
        """Read all active reminder intervals from SQLite."""
        intervals = {}
        with db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT type, interval_minutes FROM reminder_settings WHERE enabled = 1"
            )
            for row in cursor.fetchall():
                intervals[row[0]] = row[1]
        # Always add DevOps coaching (60 minutes, internal only)
        intervals["_devops_coach"] = 60
        return intervals

    def _run_loop(self):
        while self.running:
            time.sleep(60)  # tick every real minute
            if not self.running:
                break

            intervals = self._get_intervals()

            for rem_type, interval in intervals.items():
                self._timers[rem_type] = self._timers.get(rem_type, 0) + 1
                if self._timers[rem_type] >= interval:
                    self._timers[rem_type] = 0
                    self._fire_reminder(rem_type)

    # ------------------------------------------------------------------
    def _fire_reminder(self, rem_type: str):
        if rem_type == "_devops_coach":
            self._trigger_devops_coaching()
        elif rem_type in WELLNESS_REMINDERS:
            notif_title, notif_body = WELLNESS_REMINDERS[rem_type]
            # Windows Toast
            send_notification(notif_title, notif_body)
            # In-app companion
            if rem_type == "Water":
                self.app_manager.trigger_water_reminder()
            else:
                self.app_manager.show_companion_message(f"{notif_title}\n{notif_body}")

    def _trigger_devops_coaching(self):
        title, body = random.choice(DEVOPS_QUOTES)
        send_notification(title, body)
        self.app_manager.show_companion_message(f"{title}\n{body}")

    # ------------------------------------------------------------------
    # Public helper called from tray menu "Drink Water Now"
    def force_water_reminder(self):
        self._fire_reminder("Water")
