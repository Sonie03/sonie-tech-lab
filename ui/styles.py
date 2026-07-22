DARK_THEME = """
QMainWindow {
    background-color: #1e1e24;
}
QWidget {
    font-family: 'Segoe UI', 'Outfit', sans-serif;
    color: #e0e0e6;
}
QTabWidget::pane {
    border: 1px solid rgba(255, 255, 255, 0.1);
    background: rgba(30, 30, 40, 0.6);
    border-radius: 12px;
}
QTabBar::tab {
    background: rgba(45, 45, 60, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-bottom: none;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    padding: 10px 20px;
    margin-right: 4px;
}
QTabBar::tab:selected, QTabBar::tab:hover {
    background: rgba(0, 120, 215, 0.8);
    color: white;
}
QLineEdit, QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox {
    background: rgba(40, 40, 50, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 6px;
    padding: 6px;
    color: #ffffff;
}
QLineEdit:focus, QComboBox:focus {
    border: 1px solid #0078d7;
}
QPushButton {
    background-color: #0078d7;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    color: white;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #0086f0;
}
QPushButton:pressed {
    background-color: #005a9e;
}
QPushButton#secondaryBtn {
    background-color: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
}
QPushButton#secondaryBtn:hover {
    background-color: rgba(255, 255, 255, 0.15);
}
QListWidget {
    background: rgba(25, 25, 35, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 5px;
}
QSlider::groove:horizontal {
    border: 1px solid #999999;
    height: 8px;
    background: #333;
    margin: 2px 0;
    border-radius: 4px;
}
QSlider::handle:horizontal {
    background: #0078d7;
    border: 1px solid #5c5c5c;
    width: 18px;
    margin: -2px 0;
    border-radius: 9px;
}
"""

LIGHT_THEME = """
QMainWindow {
    background-color: #f3f3f9;
}
QWidget {
    font-family: 'Segoe UI', 'Outfit', sans-serif;
    color: #202020;
}
QTabWidget::pane {
    border: 1px solid rgba(0, 0, 0, 0.1);
    background: rgba(255, 255, 255, 0.95);
    border-radius: 12px;
}
QTabBar::tab {
    background: rgba(230, 230, 240, 0.8);
    border: 1px solid rgba(0, 0, 0, 0.05);
    border-bottom: none;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    padding: 10px 20px;
    margin-right: 4px;
}
QTabBar::tab:selected, QTabBar::tab:hover {
    background: #0078d7;
    color: white;
}
QLineEdit, QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox {
    background: #ffffff;
    border: 1px solid rgba(0, 0, 0, 0.15);
    border-radius: 6px;
    padding: 6px;
    color: #202020;
}
QLineEdit:focus, QComboBox:focus {
    border: 1px solid #0078d7;
}
QPushButton {
    background-color: #0078d7;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    color: white;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #0086f0;
}
QPushButton:pressed {
    background-color: #005a9e;
}
QPushButton#secondaryBtn {
    background-color: rgba(0, 0, 0, 0.05);
    border: 1px solid rgba(0, 0, 0, 0.1);
    color: #202020;
}
QPushButton#secondaryBtn:hover {
    background-color: rgba(0, 0, 0, 0.1);
}
QListWidget {
    background: #ffffff;
    border: 1px solid rgba(0, 0, 0, 0.1);
    border-radius: 8px;
    padding: 5px;
}
QSlider::groove:horizontal {
    border: 1px solid #cccccc;
    height: 8px;
    background: #e5e5e5;
    margin: 2px 0;
    border-radius: 4px;
}
QSlider::handle:horizontal {
    background: #0078d7;
    border: 1px solid #005a9e;
    width: 18px;
    margin: -2px 0;
    border-radius: 9px;
}
"""

def get_stylesheet(theme="dark"):
    return DARK_THEME if theme == "dark" else LIGHT_THEME
