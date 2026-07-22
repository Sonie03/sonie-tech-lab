"""
GitHub Heatmap Widget for DevBuddy AI.
Renders a 52-week contribution graph (like GitHub's profile grid).
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen
from PyQt6.QtCore import Qt

class GitHubHeatmapWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(150)
        self.setMinimumWidth(800)
        self.grid_data = None  # Expected: list of 52 weeks, each a list of 7 integers (counts)

    def set_data(self, grid_data):
        self.grid_data = grid_data
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Background
        painter.fillRect(self.rect(), QColor(30, 30, 35, 200))

        if not self.grid_data:
            painter.setPen(QColor(150, 150, 150))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "No contribution data available.\nSync with a valid Personal Access Token (with 'read:user' scope).")
            return

        # Metrics for the grid
        cell_size = 12
        cell_margin = 3
        start_x = 30
        start_y = 20

        # Draw Day Labels (Mon, Wed, Fri)
        painter.setPen(QColor(150, 150, 150))
        painter.drawText(5, start_y + 1 * (cell_size + cell_margin) + 10, "Mon")
        painter.drawText(5, start_y + 3 * (cell_size + cell_margin) + 10, "Wed")
        painter.drawText(5, start_y + 5 * (cell_size + cell_margin) + 10, "Fri")

        # GitHub Contribution Colors (Dark Mode)
        colors = [
            QColor(22, 27, 34),    # 0 contributions
            QColor(14, 68, 41),    # 1-3 contributions
            QColor(0, 109, 50),    # 4-6 contributions
            QColor(38, 166, 65),   # 7-9 contributions
            QColor(57, 211, 83)    # 10+ contributions
        ]

        painter.setPen(Qt.PenStyle.NoPen)

        # Draw Grid
        for week_idx, week in enumerate(self.grid_data):
            x = start_x + week_idx * (cell_size + cell_margin)
            for day_idx, count in enumerate(week):
                y = start_y + day_idx * (cell_size + cell_margin)
                
                # Determine color tier
                if count == 0:
                    color = colors[0]
                elif count <= 3:
                    color = colors[1]
                elif count <= 6:
                    color = colors[2]
                elif count <= 9:
                    color = colors[3]
                else:
                    color = colors[4]
                
                painter.setBrush(QBrush(color))
                painter.drawRoundedRect(x, y, cell_size, cell_size, 2, 2)
