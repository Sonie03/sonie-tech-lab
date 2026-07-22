import os
# Tab indices

_TAB_TASKS    = 0
_TAB_LEARNING = 1
_TAB_STATS    = 2
_TAB_GITHUB   = 3
_TAB_AVATAR   = 4
_TAB_SETTINGS = 5
_TAB_MAP = {
    "tasks": _TAB_TASKS, "learning": _TAB_LEARNING, "stats": _TAB_STATS,
    "github": _TAB_GITHUB, "avatar": _TAB_AVATAR, "settings": _TAB_SETTINGS,
}
import shutil
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QTabWidget, QLineEdit, 
                             QComboBox, QDateEdit, QListWidget, QListWidgetItem, 
                             QSlider, QSpinBox, QFileDialog, QFormLayout, QGroupBox, 
                             QCheckBox, QProgressBar, QScrollArea, QFrame, QDoubleSpinBox)
from PyQt6.QtCore import Qt, QDate, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont, QPen, QBrush
from ui.styles import get_stylesheet
from core.database import db
from core.config import config, save_config
from features.avatar_engine import AvatarEngine
from core.github_client import GitHubClient
from features.avatar_uploader import AvatarUploadWidget
from features.quotes_widget import QuotesWidget
from features.reminders_widget import RemindersWidget
from features.github_heatmap import GitHubHeatmapWidget

class GitHubSyncThread(QThread):
    sync_finished = pyqtSignal(dict)

    def __init__(self, username, token):
        super().__init__()
        self.username = username
        self.token = token

    def run(self):
        client = GitHubClient(self.username, self.token)
        stats = client.fetch_profile_stats()
        streak = client.fetch_streak()
        grid = client.fetch_contribution_grid()
        if stats:
            self.sync_finished.emit({"stats": stats, "streak": streak, "grid": grid})
        else:
            self.sync_finished.emit({})

class BarChartWidget(QWidget):
    def __init__(self, title, data_type="water"):
        super().__init__()
        self.title = title
        self.data_type = data_type # "water", "tasks", "study"
        self.setMinimumHeight(180)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Background
        painter.fillRect(self.rect(), QColor(35, 35, 45, 120) if config.get("theme", "dark") == "dark" else QColor(240, 240, 245, 240))
        
        # Query stats history from SQLite
        history = db.get_stats_history(limit=7) # [(date, water, tasks, study)]
        history.reverse() # show oldest to newest (left to right)
        
        if not history:
            painter.setPen(QColor(150, 150, 150))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "No stats logged yet. Go DevBuddy!")
            return
            
        margin = 35
        graph_width = self.width() - (margin * 2)
        graph_height = self.height() - (margin * 2)
        
        # Max value for scaling
        max_val = 1
        for row in history:
            if self.data_type == "water":
                val = row[1] or 0
            elif self.data_type == "tasks":
                val = row[2] or 0
            else:
                val = row[3] or 0.0
            if val > max_val:
                max_val = val
                
        # Draw Title
        painter.setPen(QColor(220, 220, 220) if config.get("theme", "dark") == "dark" else QColor(30, 30, 30))
        painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        painter.drawText(15, 20, self.title)
        
        # Draw Bars
        bar_gap = 10
        num_bars = len(history)
        bar_width = int((graph_width - (bar_gap * (num_bars - 1))) / num_bars)
        
        accent_color = QColor(0, 120, 215, 200) # DevBuddy Blue
        if self.data_type == "tasks":
            accent_color = QColor(46, 204, 113, 200) # Green
        elif self.data_type == "study":
            accent_color = QColor(155, 89, 182, 200) # Purple

        for i, row in enumerate(history):
            date_str = row[0][-5:] # get MM-DD
            if self.data_type == "water":
                val = row[1] or 0
            elif self.data_type == "tasks":
                val = row[2] or 0
            else:
                val = row[3] or 0.0
                
            # Scale height
            bar_height = int((val / max_val) * graph_height)
            
            x = margin + i * (bar_width + bar_gap)
            y = self.height() - margin - bar_height
            
            # Draw bar
            painter.fillRect(x, y, bar_width, bar_height, accent_color)
            
            # Draw value text label
            painter.setPen(QColor(200, 200, 200) if config.get("theme", "dark") == "dark" else QColor(50, 50, 50))
            painter.setFont(QFont("Segoe UI", 8))
            painter.drawText(x, y - 5, bar_width, 15, Qt.AlignmentFlag.AlignCenter, str(val))
            
            # Draw Date label
            painter.drawText(x, self.height() - margin + 5, bar_width, 15, Qt.AlignmentFlag.AlignCenter, date_str)


class DashboardWindow(QMainWindow):
    def __init__(self, app_manager=None):
        super().__init__()
        self.app_manager = app_manager
        self.setWindowTitle("🚀 DevBuddy AI Dashboard")
        self.setMinimumSize(950, 700)
        self.setStyleSheet(get_stylesheet(config.get("theme", "dark")))
        
        # Init avatar engine
        self.avatar_engine = AvatarEngine(os.path.join(os.path.dirname(__file__), "..", "assets"))
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)
        
        # Top Stats Banner
        self._init_stats_banner()
        
        # Tab Widget
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)
        
        self._setup_tasks_tab()
        self._setup_learning_tab()
        self._setup_stats_tab()
        self._setup_github_tab()
        self._setup_avatar_tab()
        self._setup_settings_tab()
        
        # Load initial values
        self.load_tasks()
        
    def _init_stats_banner(self):
        banner = QFrameSelfStyled()
        layout = QHBoxLayout(banner)
        layout.setContentsMargins(15, 10, 15, 10)
        
        self.stats_title = QLabel("DevBuddy Workspace")
        self.stats_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #0078d7;")
        layout.addWidget(self.stats_title)
        layout.addStretch()
        
        # Tasks Stats
        self.pending_tasks_label = QLabel("Pending Tasks: 0")
        self.pending_tasks_label.setStyleSheet("font-size: 14px; font-weight: 500;")
        layout.addWidget(self.pending_tasks_label)
        
        layout.addSpacing(15)
        
        # Productivity Score
        self.productivity_score_label = QLabel("Weekly Score: 0")
        self.productivity_score_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #f1c40f;")
        layout.addWidget(self.productivity_score_label)
        
        layout.addSpacing(30)
        
        # Theme Toggle Button
        self.theme_btn = QPushButton("🌓 Toggle Theme")
        self.theme_btn.setObjectName("secondaryBtn")
        self.theme_btn.clicked.connect(self.toggle_theme)
        layout.addWidget(self.theme_btn)
        
        self.main_layout.addWidget(banner)
        
    def toggle_theme(self):
        current = config.get("theme", "dark")
        new_theme = "light" if current == "dark" else "dark"
        config["theme"] = new_theme
        save_config(config)
        self.setStyleSheet(get_stylesheet(new_theme))
        
    # --- Tasks Tab ---
    def _setup_tasks_tab(self):
        tab = QWidget()
        layout = QHBoxLayout(tab)
        
        # Left Panel - Add Task
        form_panel = QGroupBox("Add New Task")
        form_layout = QFormLayout(form_panel)
        
        self.task_title_input = QLineEdit()
        self.task_priority_combo = QComboBox()
        self.task_priority_combo.addItems(["Low", "Medium", "High"])
        self.task_category_input = QLineEdit("DevOps")
        self.task_date_input = QDateEdit(QDate.currentDate())
        self.task_date_input.setCalendarPopup(True)
        
        form_layout.addRow("Task Name:", self.task_title_input)
        form_layout.addRow("Priority:", self.task_priority_combo)
        form_layout.addRow("Category:", self.task_category_input)
        form_layout.addRow("Due Date:", self.task_date_input)
        
        add_btn = QPushButton("Create Task")
        add_btn.clicked.connect(self.add_task)
        form_layout.addRow(add_btn)
        
        layout.addWidget(form_panel, 1)
        
        # Right Panel - Task List
        list_panel = QWidget()
        list_layout = QVBoxLayout(list_panel)
        list_layout.addWidget(QLabel("Today's Action Items"))
        
        self.task_list_widget = QListWidget()
        list_layout.addWidget(self.task_list_widget)
        
        complete_btn = QPushButton("Mark Completed")
        complete_btn.clicked.connect(self.complete_task)
        list_layout.addWidget(complete_btn)
        
        layout.addWidget(list_panel, 2)
        self.tabs.addTab(tab, "📅 Tasks")

    def add_task(self):
        title = self.task_title_input.text().strip()
        if not title:
            return
        priority = self.task_priority_combo.currentText()
        category = self.task_category_input.text().strip()
        due_date = self.task_date_input.date().toString("yyyy-MM-dd")
        
        db.add_task(title, priority, due_date, category)
        self.task_title_input.clear()
        self.load_tasks()
        if self.app_manager:
            self.app_manager.show_companion_message(f"Added task: {title}")

    def load_tasks(self):
        self.task_list_widget.clear()
        pending = db.get_pending_tasks()
        self.pending_tasks_label.setText(f"Pending Tasks: {len(pending)}")
        
        score = db.get_weekly_productivity_score()
        self.productivity_score_label.setText(f"Weekly Score: {score}/100 🎯")
        
        for task in pending:
            item_text = f"[{task[4]}] {task[1]} - Due: {task[3]} ({task[2]} Priority)"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, task[0])
            self.task_list_widget.addItem(item)

    def complete_task(self):
        selected = self.task_list_widget.currentItem()
        if not selected:
            return
        task_id = selected.data(Qt.ItemDataRole.UserRole)
        db.mark_task_completed(task_id)
        self.load_tasks()
        
        # Trigger celebration animation
        if self.app_manager:
            self.app_manager.trigger_celebration("Task Completed!")
            
        completed = db.get_completed_count()
        if completed == 1 and db.unlock_achievement("first_task"):
            from features.achievements import show_achievement
            show_achievement("first_task", self)
        elif completed == 10 and db.unlock_achievement("task_champion"):
            from features.achievements import show_achievement
            show_achievement("task_champion", self)

    # --- Learning Tracker Tab ---
    def _setup_learning_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Scrollable area for 12 DevOps Topics
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        self.learning_widgets = {} # {topic: (slider, spin_hours, spin_projects)}
        
        topics_data = db.get_all_learning_progress()
        for topic_row in topics_data:
            # topic_row format: (topic, percentage, hours_studied, projects_completed, last_revised)
            topic, pct, hours, projs, last_rev = topic_row
            
            box = QGroupBox(topic)
            box_layout = QHBoxLayout(box)
            
            # Slider
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setRange(0, 100)
            slider.setValue(pct)
            slider_label = QLabel(f"{pct}%")
            slider.valueChanged.connect(lambda val, lbl=slider_label: lbl.setText(f"{val}%"))
            box_layout.addWidget(QLabel("Progress:"))
            box_layout.addWidget(slider)
            box_layout.addWidget(slider_label)
            
            # Hours studied
            hours_spin = QDoubleSpinBox()
            hours_spin.setRange(0.0, 999.0)
            hours_spin.setValue(hours)
            box_layout.addWidget(QLabel("Hours Studied:"))
            box_layout.addWidget(hours_spin)
            
            # Projects completed
            proj_spin = QSpinBox()
            proj_spin.setRange(0, 99)
            proj_spin.setValue(projs)
            box_layout.addWidget(QLabel("Projects:"))
            box_layout.addWidget(proj_spin)
            
            if last_rev:
                date_str = last_rev[:10]
                rev_label = QLabel(f"<i>Last Revised: {date_str}</i>")
                rev_label.setStyleSheet("color: #a0a0a0; font-size: 11px;")
                box_layout.addWidget(rev_label)
            
            self.learning_widgets[topic] = (slider, hours_spin, proj_spin)
            scroll_layout.addWidget(box)
            
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        save_progress_btn = QPushButton("Save All Learning Progress")
        save_progress_btn.clicked.connect(self.save_learning_progress)
        layout.addWidget(save_progress_btn)
        
        self.tabs.addTab(tab, "🎓 DevOps Tracker")

    def save_learning_progress(self):
        for topic, (slider, hours_spin, proj_spin) in self.learning_widgets.items():
            db.update_learning_progress(
                topic, 
                slider.value(), 
                hours_spin.value(), 
                proj_spin.value()
            )
        if self.app_manager:
            self.app_manager.show_companion_message("DevOps learning progress updated!")
        self.refresh_stats_charts()

    # --- Statistics Tab ---
    def _setup_stats_tab(self):
        self.stats_tab = QWidget()
        self.stats_layout = QVBoxLayout(self.stats_tab)
        
        self.stats_layout.addWidget(QLabel("📊 Daily Habits & Study Hours History"))
        
        self.chart_water = BarChartWidget("Water Intake History (glasses)", "water")
        self.chart_tasks = BarChartWidget("Completed Tasks History", "tasks")
        self.chart_study = BarChartWidget("Study Time History (hours)", "study")
        
        self.stats_layout.addWidget(self.chart_water)
        self.stats_layout.addWidget(self.chart_tasks)
        self.stats_layout.addWidget(self.chart_study)
        
        self.tabs.addTab(self.stats_tab, "📈 Statistics")

    def refresh_stats_charts(self):
        self.chart_water.update()
        self.chart_tasks.update()
        self.chart_study.update()

    # --- GitHub Tab ---
    def _setup_github_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Credentials Form
        form_group = QGroupBox("GitHub Connection Settings")
        form_layout = QFormLayout(form_group)
        self.github_user = QLineEdit(config.get("github_username", ""))
        self.github_token = QLineEdit(config.get("github_token", ""))
        self.github_token.setEchoMode(QLineEdit.EchoMode.Password)
        
        form_layout.addRow("GitHub Username:", self.github_user)
        form_layout.addRow("Personal Access Token (PAT):", self.github_token)
        
        layout.addWidget(form_group)
        
        # Stats Display Panel
        self.git_stats_box = QGroupBox("Active Developer Profile")
        self.git_stats_layout = QFormLayout(self.git_stats_box)
        
        self.git_name_lbl = QLabel("-")
        self.git_repos_lbl = QLabel("-")
        self.git_stars_lbl = QLabel("-")
        self.git_followers_lbl = QLabel("-")
        self.git_streak_lbl = QLabel("-")
        
        self.git_stats_layout.addRow("Full Name:", self.git_name_lbl)
        self.git_stats_layout.addRow("Public Repositories:", self.git_repos_lbl)
        self.git_stats_layout.addRow("Total Star Count:", self.git_stars_lbl)
        self.git_stats_layout.addRow("Followers Count:", self.git_followers_lbl)
        self.git_stats_layout.addRow("Current Streak:", self.git_streak_lbl)
        
        layout.addWidget(self.git_stats_box)
        
        # Heatmap
        self.heatmap = GitHubHeatmapWidget()
        layout.addWidget(QLabel("<b>Contribution Heatmap (52 weeks)</b>"))
        layout.addWidget(self.heatmap)
        
        # Action Buttons
        btn_layout = QHBoxLayout()
        self.sync_git_btn = QPushButton("🔄 Sync GitHub Data")
        self.sync_git_btn.clicked.connect(self.sync_github)
        btn_layout.addWidget(self.sync_git_btn)
        
        layout.addLayout(btn_layout)
        layout.addStretch()
        self.tabs.addTab(tab, "🐙 GitHub")

    def sync_github(self):
        username = self.github_user.text().strip()
        token = self.github_token.text().strip()
        
        # Save credentials first
        config["github_username"] = username
        config["github_token"] = token
        save_config(config)
        
        self.sync_git_btn.setEnabled(False)
        self.sync_git_btn.setText("Syncing...")
        
        # Run sync thread to avoid GUI freezing
        self.sync_thread = GitHubSyncThread(username, token)
        self.sync_thread.sync_finished.connect(self.on_github_sync_finished)
        self.sync_thread.start()

    def on_github_sync_finished(self, data):
        self.sync_git_btn.setEnabled(True)
        self.sync_git_btn.setText("🔄 Sync GitHub Data")
        
        if data and "stats" in data:
            stats = data["stats"]
            streak = data.get("streak", {})
            grid = data.get("grid")
            
            self.git_name_lbl.setText(stats.get("name", ""))
            self.git_repos_lbl.setText(str(stats.get("repos", 0)))
            self.git_stars_lbl.setText(str(stats.get("stars", 0)))
            self.git_followers_lbl.setText(str(stats.get("followers", 0)))
            
            s_cur = streak.get("current_streak", 0)
            s_long = streak.get("longest_streak", 0)
            self.git_streak_lbl.setText(f"{s_cur} days 🔥 (Longest: {s_long})")
            
            if grid:
                self.heatmap.set_data(grid)
            
            if self.app_manager:
                self.app_manager.trigger_celebration(f"GitHub Synced! {stats.get('repos', 0)} repos found.")
                
            if db.unlock_achievement("github_sync"):
                from features.achievements import show_achievement
                show_achievement("github_sync", self)
        else:
            self.git_name_lbl.setText("Failed to sync profile.")

    # --- Custom Avatar Customizer Tab ---
    def _setup_avatar_tab(self):
        tab = QWidget()
        layout = QHBoxLayout(tab)
        
        # Control Panel
        controls = QWidget()
        c_layout = QVBoxLayout(controls)
        
        c_layout.addWidget(QLabel("Avatar Customizer"))
        
        # Hair selection
        self.hair_combo = QComboBox()
        self.hair_combo.addItems(["none", "spiky", "curly", "cap"])
        self.hair_combo.setCurrentText(config.get("avatar_hair", "none"))
        c_layout.addWidget(QLabel("Hairstyle:"))
        c_layout.addWidget(self.hair_combo)
        
        # Clothes selection
        self.clothes_combo = QComboBox()
        self.clothes_combo.addItems(["none", "devops_hoodie", "tshirt", "suit"])
        self.clothes_combo.setCurrentText(config.get("avatar_clothes", "none"))
        c_layout.addWidget(QLabel("Clothing:"))
        c_layout.addWidget(self.clothes_combo)
        
        # Accessories selection
        self.acc_combo = QComboBox()
        self.acc_combo.addItems(["none", "glasses", "headphones"])
        self.acc_combo.setCurrentText(config.get("avatar_acc", "none"))
        c_layout.addWidget(QLabel("Accessory:"))
        c_layout.addWidget(self.acc_combo)
        
        # Adjust Offsets
        c_layout.addWidget(QLabel("Face Overlay Offsets (X / Y)"))
        self.face_x_slider = QSlider(Qt.Orientation.Horizontal)
        self.face_x_slider.setRange(-100, 100)
        self.face_x_slider.setValue(int(config.get("face_x", 0)))
        
        self.face_y_slider = QSlider(Qt.Orientation.Horizontal)
        self.face_y_slider.setRange(-100, 100)
        self.face_y_slider.setValue(int(config.get("face_y", 0)))
        
        c_layout.addWidget(self.face_x_slider)
        c_layout.addWidget(self.face_y_slider)
        
        upload_btn = QPushButton("Upload New Photo")
        upload_btn.clicked.connect(self.upload_photo)
        c_layout.addWidget(upload_btn)
        
        apply_btn = QPushButton("Apply & Regenerate Avatar")
        apply_btn.clicked.connect(self.apply_avatar_settings)
        c_layout.addWidget(apply_btn)
        
        layout.addWidget(controls, 1)
        
        # Preview Image Panel
        preview_panel = QWidget()
        p_layout = QVBoxLayout(preview_panel)
        p_layout.addWidget(QLabel("Avatar Live Preview"))
        
        self.avatar_preview = QLabel()
        self.avatar_preview.setFixedSize(250, 250)
        self.avatar_preview.setStyleSheet("border: 2px dashed rgba(255, 255, 255, 0.2); border-radius: 10px;")
        self.avatar_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        p_layout.addWidget(self.avatar_preview)
        
        self.update_preview_display()
        layout.addWidget(preview_panel, 1)
        
        self.tabs.addTab(tab, "👤 Customize Avatar")

    def upload_photo(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Profile Photo", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            dest = os.path.join(os.path.dirname(__file__), "..", "assets", "avatar_transparent.png")
            shutil.copy(file_path, dest)
            if self.app_manager:
                self.app_manager.show_companion_message("Processing background removal...")
            self.avatar_engine.process_avatar(dest, dest)
            self.apply_avatar_settings()

    def apply_avatar_settings(self):
        # Gather config
        config["avatar_hair"] = self.hair_combo.currentText()
        config["avatar_clothes"] = self.clothes_combo.currentText()
        config["avatar_acc"] = self.acc_combo.currentText()
        config["face_x"] = self.face_x_slider.value()
        config["face_y"] = self.face_y_slider.value()
        save_config(config)
        
        # Generate composited image
        gen_config = {
            "hairstyle": config["avatar_hair"],
            "clothes": config["avatar_clothes"],
            "accessory": config["avatar_acc"],
            "face_x": config["face_x"],
            "face_y": config["face_y"],
        }
        self.avatar_engine.generate_custom_avatar(gen_config)
        self.update_preview_display()
        
        if self.app_manager:
            self.app_manager.reload_companion_avatar()

    def update_preview_display(self):
        comp_path = os.path.join(os.path.dirname(__file__), "..", "assets", "avatar_composited.png")
        if os.path.exists(comp_path):
            pix = QPixmap(comp_path)
            self.avatar_preview.setPixmap(pix.scaled(230, 230, Qt.AspectRatioMode.KeepAspectRatio))
        else:
            self.avatar_preview.setText("No Avatar Composited Yet")

    # --- Settings Tab ---
    def _setup_settings_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # General Settings Box
        gen_box = QGroupBox("General & Notifications")
        form_layout = QFormLayout(gen_box)
        
        self.voice_enabled_chk = QCheckBox("Voice Assistant Enabled")
        self.voice_enabled_chk.setChecked(config.get("voice_enabled", True))
        form_layout.addRow(self.voice_enabled_chk)
        
        save_settings_btn = QPushButton("Save General Settings")
        save_settings_btn.clicked.connect(self.save_general_settings)
        form_layout.addRow(save_settings_btn)
        scroll_layout.addWidget(gen_box)
        
        # Extended Reminder Settings Widget
        self.reminders_widget = RemindersWidget(self.app_manager)
        scroll_layout.addWidget(self.reminders_widget)
        
        # Custom Quotes Widget
        self.quotes_widget = QuotesWidget()
        scroll_layout.addWidget(self.quotes_widget)
        
        # Avatar Uploader
        self.avatar_uploader = AvatarUploadWidget(self.app_manager)
        scroll_layout.addWidget(self.avatar_uploader)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        self.tabs.addTab(tab, "⚙️ Settings")

    def save_general_settings(self):
        config["voice_enabled"] = self.voice_enabled_chk.isChecked()
        save_config(config)
        if self.app_manager:
            self.app_manager.show_companion_message("General settings updated!")


    def switch_to_tab(self, name: str):
        idx = _TAB_MAP.get(name.lower())
        if idx is not None:
            self.tabs.setCurrentIndex(idx)


class QFrameSelfStyled(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet('''
            background: rgba(45, 45, 60, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 10px;
        ''')
