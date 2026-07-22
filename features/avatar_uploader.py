"""
Widget for uploading a new avatar photo, cropping it to square,
and removing the background using the AvatarEngine.
"""
import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFileDialog, QMessageBox, QProgressBar)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QPixmap, QImage

from features.avatar_engine import AvatarEngine


class BackgroundRemovalWorker(QThread):
    finished = pyqtSignal(bool, str)

    def __init__(self, input_path, output_path, engine):
        super().__init__()
        self.input_path = input_path
        self.output_path = output_path
        self.engine = engine

    def run(self):
        success = self.engine.process_avatar(self.input_path, self.output_path)
        self.finished.emit(success, self.output_path)


class AvatarUploadWidget(QWidget):
    avatar_updated = pyqtSignal()

    def __init__(self, app_manager=None, parent=None):
        super().__init__(parent)
        self.app_manager = app_manager
        self.assets_dir = os.path.join(os.path.dirname(__file__), "..", "assets")
        self.engine = AvatarEngine(self.assets_dir)
        self.worker = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.lbl_title = QLabel("📸 Upload New Avatar")
        self.lbl_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffffff;")
        layout.addWidget(self.lbl_title)

        self.lbl_desc = QLabel("Select a photo of yourself. The AI will remove the background.")
        self.lbl_desc.setStyleSheet("color: #a0a0a0; font-size: 12px;")
        layout.addWidget(self.lbl_desc)

        self.preview_label = QLabel()
        self.preview_label.setFixedSize(120, 120)
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet("border: 2px dashed #444; border-radius: 8px;")
        layout.addWidget(self.preview_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0) # Indeterminate
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        row = QHBoxLayout()
        self.btn_select = QPushButton("Browse Photo...")
        self.btn_select.clicked.connect(self._select_photo)
        row.addWidget(self.btn_select)

        self.btn_process = QPushButton("Remove Background & Apply")
        self.btn_process.setEnabled(False)
        self.btn_process.clicked.connect(self._process_photo)
        row.addWidget(self.btn_process)
        
        layout.addLayout(row)
        
        self.selected_path = None
        self._load_current_avatar()

    def _load_current_avatar(self):
        path = self.engine.composited_avatar_path
        if os.path.exists(path):
            pix = QPixmap(path).scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.preview_label.setPixmap(pix)
            self.preview_label.setStyleSheet("border: 2px solid #0078d7; border-radius: 8px;")
        else:
            self.preview_label.setText("No Avatar")

    def _select_photo(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Avatar Photo", "", "Images (*.png *.jpg *.jpeg)"
        )
        if path:
            self.selected_path = path
            pix = QPixmap(path).scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.preview_label.setPixmap(pix)
            self.preview_label.setStyleSheet("border: 2px solid #ffa500; border-radius: 8px;") # Orange border indicating pending
            self.btn_process.setEnabled(True)

    def _process_photo(self):
        if not self.selected_path:
            return

        self.btn_select.setEnabled(False)
        self.btn_process.setEnabled(False)
        self.progress_bar.show()
        
        self.worker = BackgroundRemovalWorker(
            self.selected_path, 
            self.engine.base_avatar_path, 
            self.engine
        )
        self.worker.finished.connect(self._on_process_finished)
        self.worker.start()

    def _on_process_finished(self, success: bool, output_path: str):
        self.progress_bar.hide()
        self.btn_select.setEnabled(True)
        self.btn_process.setEnabled(False)

        if success:
            # Generate the composited version using the engine (adds accessories, scales, etc)
            from core.config import config
            self.engine.generate_custom_avatar(config)
            
            self._load_current_avatar()
            self.avatar_updated.emit()
            if self.app_manager:
                self.app_manager.reload_companion_avatar()
                self.app_manager.trigger_celebration("New avatar applied successfully! ✨")
        else:
            QMessageBox.critical(self, "Error", "Failed to process photo. Is rembg installed?")
            
