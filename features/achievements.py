"""
Achievement badge system for DevBuddy AI.
Shows a premium popup overlay when a milestone is reached.
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint
from PyQt6.QtGui import QColor, QPainter, QFont, QLinearGradient, QBrush

ACHIEVEMENTS = {
    "first_task":       ("🏅 First Task Done!",      "You completed your very first task. Keep it up!"),
    "water_streak":     ("💧 Hydration Hero",         "You've been drinking water consistently. Amazing!"),
    "docker_master":    ("🐳 Docker Master",          "Docker progress > 80%. Interview-ready!"),
    "k8s_explorer":     ("☸️ Kubernetes Explorer",    "Kubernetes progress > 50%. You're getting there!"),
    "github_sync":      ("🐙 GitHub Connected",       "GitHub synced! Your commits are being tracked."),
    "devops_beginner":  ("🚀 DevOps Beginner",        "Average DevOps progress > 25%. Great start!"),
    "devops_pro":       ("⚡ DevOps Pro",              "Average DevOps progress > 75%. You're crushing it!"),
    "study_marathon":   ("📚 Study Marathon",         "5+ hours of study logged. Phenomenal dedication!"),
    "task_champion":    ("🏆 Task Champion",          "10 tasks completed! You're unstoppable!"),
    "daily_complete":   ("✅ Day Complete",            "All today's tasks done! Enjoy your evening."),
}


class AchievementPopup(QWidget):
    """
    A frameless, transparent toast-style achievement popup that slides in
    from the top-right, stays for 5 seconds, then fades out.
    """

    def __init__(self, title: str, description: str, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(360, 100)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 12, 18, 12)
        layout.setSpacing(4)

        # Title row
        title_row = QHBoxLayout()
        badge_lbl = QLabel("🏆")
        badge_lbl.setStyleSheet("font-size: 26px; background: transparent; border: none;")
        title_row.addWidget(badge_lbl)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #ffffff;"
            " background: transparent; border: none;"
        )
        title_row.addWidget(title_lbl)
        title_row.addStretch()
        layout.addLayout(title_row)

        # Description
        desc_lbl = QLabel(description)
        desc_lbl.setStyleSheet(
            "font-size: 11px; color: #c8d8ff; background: transparent; border: none;"
        )
        desc_lbl.setWordWrap(True)
        layout.addWidget(desc_lbl)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Glassmorphic dark-blue gradient background
        grad = QLinearGradient(0, 0, self.width(), self.height())
        grad.setColorAt(0.0, QColor(10, 40, 90, 230))
        grad.setColorAt(1.0, QColor(0, 80, 160, 210))
        painter.setBrush(QBrush(grad))
        painter.setPen(QColor(0, 150, 255, 120))
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 14, 14)

        # Subtle top highlight
        painter.setPen(QColor(120, 180, 255, 80))
        painter.drawLine(14, 1, self.width() - 14, 1)


def show_achievement(achievement_key: str, parent=None):
    """Look up an achievement by key and display the popup."""
    if achievement_key not in ACHIEVEMENTS:
        return
    title, desc = ACHIEVEMENTS[achievement_key]
    _show_popup(title, desc, parent)


def show_custom_achievement(title: str, desc: str, parent=None):
    """Show an achievement popup with a custom title and description."""
    _show_popup(title, desc, parent)


def _show_popup(title: str, desc: str, parent=None):
    popup = AchievementPopup(title, desc, parent)

    # Position: top-right corner
    from PyQt6.QtWidgets import QApplication
    screen = QApplication.primaryScreen().availableGeometry()
    start_x = screen.width() - popup.width() - 20
    start_y = -popup.height()          # start above screen
    end_y   = 20                       # slide down to here

    popup.move(start_x, start_y)
    popup.show()

    # Slide-in animation
    anim = QPropertyAnimation(popup, b"pos", popup)
    anim.setDuration(500)
    anim.setStartValue(QPoint(start_x, start_y))
    anim.setEndValue(QPoint(start_x, end_y))
    anim.setEasingCurve(QEasingCurve.Type.OutCubic)
    anim.start()

    # Auto-dismiss after 5 seconds with slide-out
    def _dismiss():
        out = QPropertyAnimation(popup, b"pos", popup)
        out.setDuration(400)
        out.setStartValue(QPoint(start_x, end_y))
        out.setEndValue(QPoint(start_x, -popup.height()))
        out.setEasingCurve(QEasingCurve.Type.InCubic)
        out.finished.connect(popup.deleteLater)
        out.start()

    QTimer.singleShot(5000, _dismiss)

    # Keep animation objects alive
    popup._anim = anim
