import sqlite3
import os
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path="devbuddy.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._get_connection() as conn:
            c = conn.cursor()

            # Tasks
            c.execute('''CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                priority TEXT DEFAULT 'Medium',
                due_date TEXT,
                category TEXT,
                progress INTEGER DEFAULT 0,
                completed BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')

            # DevOps learning progress (12 topics)
            c.execute('''CREATE TABLE IF NOT EXISTS learning_progress (
                topic TEXT PRIMARY KEY,
                percentage INTEGER DEFAULT 0,
                hours_studied REAL DEFAULT 0.0,
                projects_completed INTEGER DEFAULT 0,
                last_revised TIMESTAMP
            )''')

            # Reminder settings
            c.execute('''CREATE TABLE IF NOT EXISTS reminder_settings (
                type TEXT PRIMARY KEY,
                interval_minutes INTEGER DEFAULT 30,
                enabled BOOLEAN DEFAULT 1
            )''')

            # Daily stats
            c.execute('''CREATE TABLE IF NOT EXISTS daily_stats (
                date TEXT PRIMARY KEY,
                water_glasses INTEGER DEFAULT 0,
                tasks_completed INTEGER DEFAULT 0,
                study_hours REAL DEFAULT 0.0
            )''')

            # Custom motivational quotes
            c.execute('''CREATE TABLE IF NOT EXISTS custom_quotes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quote TEXT NOT NULL,
                author TEXT DEFAULT 'Me',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')

            # Achievement log
            c.execute('''CREATE TABLE IF NOT EXISTS achievements (
                key TEXT PRIMARY KEY,
                unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')

            conn.commit()
            self._seed_defaults(c, conn)

    def _seed_defaults(self, c, conn):
        # Seed DevOps topics
        c.execute("SELECT COUNT(*) FROM learning_progress")
        if c.fetchone()[0] == 0:
            topics = [
                'Git', 'Linux', 'Docker', 'Kubernetes', 'Jenkins',
                'Terraform', 'AWS', 'GitHub Actions', 'Ansible',
                'Prometheus', 'Grafana', 'Shell Scripting'
            ]
            c.executemany(
                "INSERT INTO learning_progress (topic) VALUES (?)",
                [(t,) for t in topics]
            )

        # Seed all reminder types
        c.execute("SELECT COUNT(*) FROM reminder_settings")
        if c.fetchone()[0] == 0:
            defaults = [
                ('Water', 45), ('Stretch', 60), ('Eye (20-20-20)', 20),
                ('Stand', 60), ('Walk', 90), ('Workout', 480),
                ('Study', 120), ('Sleep', 0), ('Break', 60),
                ('Medicine', 720), ('Meeting', 0), ('Birthday', 0),
            ]
            c.executemany(
                "INSERT INTO reminder_settings (type, interval_minutes, enabled) VALUES (?, ?, ?)",
                [(t, i, 1 if i > 0 else 0) for t, i in defaults]
            )
        conn.commit()

    # ------------------------------------------------------------------ Tasks
    def add_task(self, title, priority="Medium", due_date=None, category="General"):
        with self._get_connection() as conn:
            c = conn.cursor()
            c.execute(
                "INSERT INTO tasks (title, priority, due_date, category) VALUES (?,?,?,?)",
                (title, priority, due_date, category)
            )
            conn.commit()
            return c.lastrowid

    def get_pending_tasks(self):
        with self._get_connection() as conn:
            return conn.execute(
                "SELECT * FROM tasks WHERE completed=0 ORDER BY created_at DESC"
            ).fetchall()

    def get_completed_count(self):
        with self._get_connection() as conn:
            return conn.execute(
                "SELECT COUNT(*) FROM tasks WHERE completed=1"
            ).fetchone()[0]

    def mark_task_completed(self, task_id):
        today = datetime.now().strftime('%Y-%m-%d')
        with self._get_connection() as conn:
            c = conn.cursor()
            c.execute("UPDATE tasks SET completed=1, progress=100 WHERE id=?", (task_id,))
            c.execute(
                "INSERT INTO daily_stats(date,tasks_completed) VALUES(?,1) "
                "ON CONFLICT(date) DO UPDATE SET tasks_completed=tasks_completed+1",
                (today,)
            )
            conn.commit()

    def delete_task(self, task_id):
        with self._get_connection() as conn:
            conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))
            conn.commit()

    # -------------------------------------------------------- Learning progress
    def get_all_learning_progress(self):
        with self._get_connection() as conn:
            return conn.execute("SELECT * FROM learning_progress").fetchall()

    def update_learning_progress(self, topic, percentage, hours, projects):
        today = datetime.now().strftime('%Y-%m-%d')
        with self._get_connection() as conn:
            c = conn.cursor()
            c.execute(
                "UPDATE learning_progress "
                "SET percentage=?, hours_studied=?, projects_completed=?, last_revised=CURRENT_TIMESTAMP "
                "WHERE topic=?",
                (percentage, hours, projects, topic)
            )
            c.execute(
                "INSERT INTO daily_stats(date,study_hours) VALUES(?,?) "
                "ON CONFLICT(date) DO UPDATE SET study_hours=study_hours+?",
                (today, hours, hours)
            )
            conn.commit()

    def get_average_devops_progress(self) -> float:
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT AVG(percentage) FROM learning_progress"
            ).fetchone()
            return row[0] or 0.0

    # -------------------------------------------------------- Reminder settings
    def get_reminder_settings(self):
        with self._get_connection() as conn:
            return conn.execute(
                "SELECT type, interval_minutes, enabled FROM reminder_settings ORDER BY type"
            ).fetchall()

    def update_reminder(self, rem_type, interval, enabled):
        with self._get_connection() as conn:
            conn.execute(
                "UPDATE reminder_settings SET interval_minutes=?, enabled=? WHERE type=?",
                (interval, int(enabled), rem_type)
            )
            conn.commit()

    # ------------------------------------------------------------------ Stats
    def increment_water(self):
        today = datetime.now().strftime('%Y-%m-%d')
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO daily_stats(date,water_glasses) VALUES(?,1) "
                "ON CONFLICT(date) DO UPDATE SET water_glasses=water_glasses+1",
                (today,)
            )
            conn.commit()

    def get_today_water(self) -> int:
        today = datetime.now().strftime('%Y-%m-%d')
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT water_glasses FROM daily_stats WHERE date=?", (today,)
            ).fetchone()
            return row[0] if row else 0

    def get_stats_history(self, limit=7):
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT date, water_glasses, tasks_completed, study_hours "
                "FROM daily_stats ORDER BY date DESC LIMIT ?",
                (limit,)
            ).fetchall()
        return list(reversed(rows))

    def get_weekly_productivity_score(self) -> int:
        """Score 0-100 based on water, tasks, study in last 7 days."""
        history = self.get_stats_history(7)
        if not history:
            return 0
        total_water  = sum(r[1] or 0 for r in history)
        total_tasks  = sum(r[2] or 0 for r in history)
        total_study  = sum(r[3] or 0.0 for r in history)
        # Targets: 8 glasses/day, 3 tasks/day, 1 hr study/day → per week ×7
        score = min(100, int(
            (total_water / 56) * 33 +
            (total_tasks / 21) * 34 +
            (total_study /  7) * 33
        ))
        return score

    # -------------------------------------------------- Custom motivational quotes
    def add_custom_quote(self, quote: str, author: str = "Me"):
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO custom_quotes(quote, author) VALUES(?,?)",
                (quote, author)
            )
            conn.commit()

    def get_all_quotes(self):
        with self._get_connection() as conn:
            return conn.execute(
                "SELECT id, quote, author FROM custom_quotes ORDER BY id DESC"
            ).fetchall()

    def delete_quote(self, quote_id: int):
        with self._get_connection() as conn:
            conn.execute("DELETE FROM custom_quotes WHERE id=?", (quote_id,))
            conn.commit()

    # --------------------------------------------------------- Achievement log
    def unlock_achievement(self, key: str) -> bool:
        """Unlock achievement. Returns True if newly unlocked, False if already had."""
        with self._get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT key FROM achievements WHERE key=?", (key,))
            if c.fetchone():
                return False
            c.execute("INSERT INTO achievements(key) VALUES(?)", (key,))
            conn.commit()
            return True

    def get_unlocked_achievements(self):
        with self._get_connection() as conn:
            return conn.execute(
                "SELECT key, unlocked_at FROM achievements ORDER BY unlocked_at DESC"
            ).fetchall()


db = DatabaseManager()
