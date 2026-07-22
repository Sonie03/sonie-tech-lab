"""
Desktop Companion Widget for DevBuddy AI.

A frameless, transparent, always-on-top window that sits in the
bottom-right corner of the screen. Features:
  - Idle breathing animation
  - Interactive speech bubble with water-reminder action buttons
  - Physics-based confetti particle celebration system
  - Draggable via left-click-drag
"""
import os
import random

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import QPixmap, QPainter, QColor, QMouseEvent, QBrush

from core.database import db
from features.notifications import send_notification
from features.sounds import play_applause
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve


# ---------------------------------------------------------------------------
# Confetti Particle
# ---------------------------------------------------------------------------
class ConfettiParticle:
    COLORS = [
        QColor(0, 120, 215, 230),    # blue
        QColor(46, 204, 113, 230),   # green
        QColor(255, 193, 7, 230),    # amber
        QColor(231, 76, 60, 230),    # red
        QColor(155, 89, 182, 230),   # purple
        QColor(26, 188, 156, 230),   # teal
        QColor(241, 196, 15, 230),   # yellow
    ]

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.vx = random.uniform(-4, 4)
        self.vy = random.uniform(-8, -2)   # shoot upwards
        self.gravity = 0.25
        self.color = random.choice(self.COLORS)
        self.size = random.randint(6, 11)
        self.shape = random.choice(["circle", "rect"])
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-5, 5)

    def update(self):
        self.vy += self.gravity
        self.x += self.vx
        self.y += self.vy
        self.rotation += self.rot_speed


# ---------------------------------------------------------------------------
# Companion Widget
# ---------------------------------------------------------------------------
class CompanionWidget(QWidget):
    def __init__(self, app_manager=None):
        super().__init__()
        self.app_manager = app_manager
        self.particles: list[ConfettiParticle] = []

        # Window flags: frameless, transparent, always-on-top, not in taskbar
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(300, 310)
        self.drag_position = QPoint()

        # ----- Layout -----
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(6)

        # 1. Speech Bubble
        self.speech_bubble = QWidget()
        self.speech_bubble.setStyleSheet("""
            background-color: rgba(20, 20, 32, 225);
            border: 1px solid rgba(0, 120, 215, 0.5);
            border-radius: 14px;
        """)
        bubble_layout = QVBoxLayout(self.speech_bubble)
        bubble_layout.setContentsMargins(12, 8, 12, 8)
        bubble_layout.setSpacing(6)

        self.speech_label = QLabel("Hi! I'm your DevBuddy. Let's build something great! 🚀")
        self.speech_label.setStyleSheet(
            "color: #e8f0fe; font-size: 12px; font-weight: 500; background: transparent; border: none;"
        )
        self.speech_label.setWordWrap(True)
        bubble_layout.addWidget(self.speech_label)

        # Action buttons (for water reminder)
        btn_row = QHBoxLayout()
        btn_row.setSpacing(6)

        self.drank_btn = QPushButton("✔  I Drank Water")
        self.drank_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d7; border: none; border-radius: 6px;
                padding: 5px 10px; color: white; font-size: 11px; font-weight: bold;
            }
            QPushButton:hover { background-color: #0086f0; }
        """)
        self.drank_btn.clicked.connect(self.on_drank_water)

        self.later_btn = QPushButton("⏰  Later")
        self.later_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,0.2);
                border-radius: 6px; padding: 5px 10px; color: #e0e0e0; font-size: 11px;
            }
            QPushButton:hover { background-color: rgba(255,255,255,0.2); }
        """)
        self.later_btn.clicked.connect(self.on_remind_later)

        btn_row.addWidget(self.drank_btn)
        btn_row.addWidget(self.later_btn)
        bubble_layout.addLayout(btn_row)

        self.speech_bubble.hide()
        main_layout.addWidget(self.speech_bubble)

        self.original_avatar_pixmap = None
        self.anim_time = 0.0
        self.is_talking = False

        # 2. Avatar Label (for GIFs)
        self.avatar_label = QLabel()
        self.avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.avatar_label.setStyleSheet("background: transparent; border: none;")
        self.avatar_label.hide() # Hidden by default, shown if GIF
        main_layout.addWidget(self.avatar_label)

        # Start the high-FPS render loop for the Live2D-like idle animation
        self.render_timer = QTimer()
        self.render_timer.timeout.connect(self._render_loop)
        self.render_timer.start(30) # ~33 FPS

        # ----- Init -----
        self.reload_avatar()
        self._position_bottom_right()

        # Confetti timer (fires every 30 ms while celebration active)
        self.confetti_timer = QTimer()
        self.confetti_timer.timeout.connect(self._tick_particles)

    # ------------------------------------------------------------------
    # Avatar
    # ------------------------------------------------------------------
    def reload_avatar(self):
        gif_path = os.path.normpath(
            os.path.join(os.path.dirname(__file__), "..", "assets", "avatar.gif")
        )
        comp_path = os.path.normpath(
            os.path.join(os.path.dirname(__file__), "..", "assets", "avatar_composited.png")
        )
        
        if os.path.exists(gif_path):
            from PyQt6.QtGui import QMovie
            from PyQt6.QtCore import QSize
            self.movie = QMovie(gif_path)
            self.movie.setScaledSize(QSize(200, 200))
            self.avatar_label.setMovie(self.movie)
            self.movie.start()
            self.avatar_label.show()
            self.original_avatar_pixmap = None
            self.render_timer.stop() # stop procedural drawing
        elif os.path.exists(comp_path):
            self.avatar_label.hide()
            if hasattr(self, 'movie') and self.movie:
                self.movie.stop()
            self.original_avatar_pixmap = QPixmap(comp_path).scaled(
                185, 185, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            )
            if not self.render_timer.isActive():
                self.render_timer.start(30)
        else:
            self.avatar_label.hide()
            self.original_avatar_pixmap = None

    def _render_loop(self):
        """Advances the animation time and triggers a repaint."""
        self.anim_time += 0.05
        self.update()

    # ------------------------------------------------------------------
    # Positioning & Animations
    # ------------------------------------------------------------------
    def _position_bottom_right(self):
        screen = self.screen().availableGeometry()
        self.move(screen.width() - self.width() - 20,
                  screen.height() - self.height() - 20)

    # ------------------------------------------------------------------
    # Speech Bubble
    # ------------------------------------------------------------------
    def show_message(self, text: str, duration: int = 6000, has_buttons: bool = False):
        self.speech_label.setText(text)
        if has_buttons:
            self.drank_btn.show()
            self.later_btn.show()
        else:
            self.drank_btn.hide()
            self.later_btn.hide()

        self.speech_bubble.show()

        # TTS (imported lazily to avoid circular imports)
        try:
            from features.voice import voice
            if self.app_manager: # Only speak if voice is enabled in general settings (already handled by voice module if configured, but we can just call it)
                voice.speak(text)
        except Exception:
            pass

        # Slide-in animation for the speech bubble
        self.speech_bubble.move(self.speech_bubble.x(), self.speech_bubble.y() + 20)
        self.speech_bubble.setWindowOpacity(0.0)
        self.bubble_anim = QPropertyAnimation(self.speech_bubble, b"pos")
        self.bubble_anim.setDuration(300)
        self.bubble_anim.setStartValue(QPoint(self.speech_bubble.x(), self.speech_bubble.y()))
        self.bubble_anim.setEndValue(QPoint(self.speech_bubble.x(), self.speech_bubble.y() - 20))
        self.bubble_anim.setEasingCurve(QEasingCurve.Type.OutBack)
        self.bubble_anim.start()

        # Talking animation state
        self.is_talking = True
        
        if not has_buttons:
            QTimer.singleShot(duration, self.speech_bubble.hide)
            QTimer.singleShot(duration, self._stop_talking)

    def _stop_talking(self):
        self.is_talking = False

    # ------------------------------------------------------------------
    # Water Reminder Interactions
    # ------------------------------------------------------------------
    def on_drank_water(self):
        db.increment_water()
        self.speech_bubble.hide()
        self.trigger_celebration("Great job! 💧 Keep taking care of yourself!")

    def on_remind_later(self):
        self.speech_bubble.hide()
        if self.app_manager:
            self.app_manager.show_companion_message("Okay! I'll remind you again soon. 🕐")

    # ------------------------------------------------------------------
    # Confetti Celebration
    # ------------------------------------------------------------------
    def trigger_celebration(self, msg: str = ""):
        if msg:
            self.show_message(msg, 5000)
        send_notification("🎉 DevBuddy Celebration!", msg or "You did it!")
        
        # Play applause sound
        play_applause()

        # Spawn 70 particles at the avatar centre
        cx = self.width() / 2
        cy = self.height() - 100
        self.particles = [ConfettiParticle(cx, cy) for _ in range(70)]
        self.confetti_timer.start(30)
        QTimer.singleShot(3500, self._stop_celebration)

    def _tick_particles(self):
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.y < self.height() + 20]
        self.update()

    def _stop_celebration(self):
        self.confetti_timer.stop()
        self.particles.clear()
        self.update()

    # ------------------------------------------------------------------
    # Drag Support
    # ------------------------------------------------------------------
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = (event.globalPosition().toPoint()
                                  - self.frameGeometry().topLeft())

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)

    # ------------------------------------------------------------------
    # Paint (Live2D Avatar Animation & Particles)
    # ------------------------------------------------------------------
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 0))

        # 1. Draw Animated Avatar
        if self.original_avatar_pixmap:
            import math
            painter.save()
            
            # Smooth walking motion
            # Bounce effect (footsteps)
            bounce_y = abs(math.sin(self.anim_time * 4.0)) * 10.0
            
            # Sway effect (shifting weight)
            angle = math.cos(self.anim_time * 4.0) * 3.0
            
            scale_y = 1.0
            
            # If talking, add rapid jitter
            if self.is_talking:
                scale_y += (random.random() * 0.05)
                
            # Random blink
            if random.random() < 0.015:
                scale_y *= 0.1
                
            # Set pivot point to bottom-center of where the avatar is drawn
            center_x = self.width() / 2.0
            center_y = float(self.height() - 20) - bounce_y
            
            painter.translate(center_x, center_y)
            painter.rotate(angle)
            painter.scale(1.0, scale_y)
            
            # Draw so the pivot is at the bottom-center
            painter.drawPixmap(-92, -185, 185, 185, self.original_avatar_pixmap)
            painter.restore()
        else:
            # Fallback robot emoji
            painter.save()
            painter.setFont(painter.font()) # use default font
            font = painter.font()
            font.setPointSize(72)
            painter.setFont(font)
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter, "🤖")
            painter.restore()

        # 2. Draw Confetti Particles
        for p in self.particles:
            painter.setBrush(QBrush(p.color))
            painter.setPen(Qt.PenStyle.NoPen)
            ix, iy = int(p.x), int(p.y)
            if p.shape == "circle":
                painter.drawEllipse(ix, iy, p.size, p.size)
            else:
                painter.save()
                painter.translate(ix + p.size / 2, iy + p.size / 2)
                painter.rotate(p.rotation)
                painter.drawRect(-p.size // 2, -p.size // 2, p.size, p.size)
                painter.restore()
