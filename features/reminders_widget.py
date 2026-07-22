"""
Widget to manage all reminder intervals and toggles.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QSpinBox, QCheckBox, QGroupBox, QGridLayout, QScrollArea)
from PyQt6.QtCore import Qt
from core.database import db

class RemindersWidget(QGroupBox):
    def __init__(self, app_manager=None, parent=None):
        super().__init__("Reminder Settings", parent)
        self.app_manager = app_manager
        
        main_layout = QVBoxLayout(self)
        
        # We need a scroll area because there are many reminders
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent;")
        
        content = QWidget()
        self.grid = QGridLayout(content)
        
        self.rem_controls = {}
        
        self._load_reminders()
        
        scroll.setWidget(content)
        main_layout.addWidget(scroll)
        
        save_btn = QPushButton("Save Reminder Settings")
        save_btn.clicked.connect(self._save_reminders)
        main_layout.addWidget(save_btn)

    def _load_reminders(self):
        reminders = db.get_reminder_settings()
        
        # Headers
        self.grid.addWidget(QLabel("<b>Type</b>"), 0, 0)
        self.grid.addWidget(QLabel("<b>Enabled</b>"), 0, 1)
        self.grid.addWidget(QLabel("<b>Interval (min)</b>"), 0, 2)
        
        row = 1
        for rem_type, interval, enabled in reminders:
            lbl = QLabel(rem_type)
            
            chk = QCheckBox()
            chk.setChecked(bool(enabled))
            
            spin = QSpinBox()
            spin.setRange(0, 1440)
            spin.setValue(interval)
            
            self.grid.addWidget(lbl, row, 0)
            self.grid.addWidget(chk, row, 1)
            self.grid.addWidget(spin, row, 2)
            
            self.rem_controls[rem_type] = (chk, spin)
            row += 1

    def _save_reminders(self):
        for rem_type, (chk, spin) in self.rem_controls.items():
            db.update_reminder(rem_type, spin.value(), chk.isChecked())
            
        if self.app_manager:
            self.app_manager.show_companion_message("Reminder settings saved!")
            # Restart scheduler to pick up new intervals
            self.app_manager.scheduler.stop()
            self.app_manager.scheduler.start()
