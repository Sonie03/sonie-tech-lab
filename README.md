# DevBuddy AI

DevBuddy AI is a premium Windows 11 desktop application designed to act as a personal AI desktop companion, productivity dashboard, and DevOps learning coach.

## Features
- **Always-on-top Desktop Companion:** Animated avatar tracking your productivity.
- **Custom Avatars:** Automatically processes uploaded photos into transparent desktop pets.
- **Water & Wellness Reminders:** Configurable reminders to keep you healthy.
- **DevOps Learning Tracker:** Stay motivated and track your skills (Docker, K8s, AWS).
- **GitHub Dashboard:** View your commits, streaks, and repository stats.
- **System Tray Integration:** Runs silently in the background with minimal RAM usage.

## Installation

1. Clone or download the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python main.py
   ```

## Packaging

To package the application as a standalone executable using PyInstaller:
```bash
pyinstaller --noconfirm --onedir --windowed --add-data "assets;assets" main.py
```
