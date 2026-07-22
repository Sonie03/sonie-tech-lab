"""
System tray manager for DevBuddy AI.
Creates a pystray icon with a full context menu.
"""
import os
import pystray
from pystray import MenuItem as item, Menu
from PIL import Image

ICON_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "tray_icon.png")


def _load_icon() -> Image.Image:
    """Load the tray icon, falling back to a solid-color square if missing."""
    if os.path.exists(ICON_PATH):
        return Image.open(ICON_PATH).resize((64, 64))
    # Fallback: blue square
    return Image.new("RGB", (64, 64), color=(0, 120, 215))


class TrayManager:
    def __init__(self, app_manager):
        self.app_manager = app_manager
        self.icon: pystray.Icon | None = None
        self._reminders_paused = False

    def setup_tray(self):
        image = _load_icon()

        menu = Menu(
            item("🚀 Open Dashboard",        self._on_open_dashboard),
            Menu.SEPARATOR,
            item("💧 Drink Water Now",        self._on_drink_water),
            item("📅 Today's Tasks",          self._on_open_tasks),
            item("🐙 GitHub Status",          self._on_open_github),
            Menu.SEPARATOR,
            item(
                lambda _: "▶ Resume Reminders" if self._reminders_paused else "⏸ Pause Reminders",
                self._on_toggle_reminders,
            ),
            Menu.SEPARATOR,
            item("⚙️ Settings",               self._on_open_settings),
            item("❌ Exit",                   self._on_exit),
        )

        self.icon = pystray.Icon(
            name="DevBuddy AI",
            icon=image,
            title="DevBuddy AI",
            menu=menu,
        )

    def run(self):
        if self.icon:
            self.icon.run()

    # --- Menu Callbacks ---
    def _on_open_dashboard(self, icon, menu_item):
        self.app_manager.show_dashboard()

    def _on_drink_water(self, icon, menu_item):
        self.app_manager.trigger_water_reminder()

    def _on_open_tasks(self, icon, menu_item):
        self.app_manager.show_dashboard(tab="tasks")

    def _on_open_github(self, icon, menu_item):
        self.app_manager.show_dashboard(tab="github")

    def _on_toggle_reminders(self, icon, menu_item):
        self._reminders_paused = not self._reminders_paused
        if self._reminders_paused:
            self.app_manager.scheduler.stop()
            self.app_manager.show_companion_message("⏸ Reminders paused.")
        else:
            self.app_manager.scheduler.start()
            self.app_manager.show_companion_message("▶ Reminders resumed!")

    def _on_open_settings(self, icon, menu_item):
        self.app_manager.show_dashboard(tab="settings")

    def _on_exit(self, icon, menu_item):
        self.icon.stop()
        self.app_manager.quit_app()
