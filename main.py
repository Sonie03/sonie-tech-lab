"""
DevBuddy AI – Main Entry Point
================================
Initialises the PyQt6 QApplication, spawns the:
  - Dashboard window        (ui/dashboard.py)
  - Desktop Companion       (ui/companion.py)
  - System Tray icon        (ui/tray_menu.py)
  - Background Reminder scheduler (features/reminders.py)

Run with:  python main.py
"""

import sys
import os
import threading

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from ui.dashboard import DashboardWindow
from ui.companion import CompanionWidget
from ui.tray_menu import TrayManager
from features.reminders import ReminderScheduler

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
ICON_PATH  = os.path.join(ASSETS_DIR, "tray_icon.png")


class DevBuddyApp:
    """Central application manager – all subsystems talk through here."""

    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)   # keep alive in tray
        self.app.setApplicationName("DevBuddy AI")
        self.app.setOrganizationName("DevBuddy")

        if os.path.exists(ICON_PATH):
            self.app.setWindowIcon(QIcon(ICON_PATH))

        # Build subsystems (pass self so they can call back)
        self.dashboard  = DashboardWindow(self)
        self.companion  = CompanionWidget(self)
        self.tray       = TrayManager(self)
        self.scheduler  = ReminderScheduler(self)

    # ------------------------------------------------------------------
    def start(self):
        """Wire everything up and enter the Qt event loop."""
        # Generate initial composited avatar if not yet created
        comp_path = os.path.join(ASSETS_DIR, "avatar_composited.png")
        if not os.path.exists(comp_path):
            self.dashboard.apply_avatar_settings()

        # System tray (runs in its own daemon thread via pystray)
        self.tray.setup_tray()
        tray_thread = threading.Thread(target=self.tray.run, daemon=True)
        tray_thread.start()

        # Background reminder scheduler
        self.scheduler.start()

        # Show the always-on-top companion
        self.companion.show()

        # Greet the user
        self.companion.show_message(
            "👋 Welcome back! Ready to crush today's DevOps goals?", 7000
        )

        sys.exit(self.app.exec())

    # ------------------------------------------------------------------
    # Public API used by all subsystems
    # ------------------------------------------------------------------
    def show_dashboard(self, tab: str = ""):
        """Show the dashboard, optionally jumping to a named tab."""
        self.dashboard.show()
        self.dashboard.activateWindow()
        self.dashboard.raise_()
        if tab:
            self.dashboard.switch_to_tab(tab)

    def trigger_water_reminder(self):
        """Show the water-reminder speech bubble with action buttons."""
        self.companion.show_message(
            "💧 Hey! Time to drink water.\nStay hydrated – your brain needs it!",
            has_buttons=True,
        )

    def show_companion_message(self, msg: str, duration: int = 7000):
        """Show a plain informational message in the companion bubble."""
        self.companion.show_message(msg, duration)

    def reload_companion_avatar(self):
        """Reload the composited avatar image into the companion widget."""
        self.companion.reload_avatar()

    def trigger_celebration(self, msg: str):
        """Trigger confetti + toast for a milestone."""
        self.companion.trigger_celebration(msg)
        self.dashboard.refresh_stats_charts()

    def quit_app(self):
        self.scheduler.stop()
        self.app.quit()


# ------------------------------------------------------------------
if __name__ == "__main__":
    app = DevBuddyApp()
    app.start()
