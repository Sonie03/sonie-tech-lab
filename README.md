# DevBuddy AI 🚀

An intelligent, interactive desktop companion and productivity suite tailored specifically for DevOps engineers and developers. Built entirely in Python using PyQt6, DevBuddy AI sits transparently on your desktop to coach you, track your learning, manage your tasks, and celebrate your GitHub milestones!

## ✨ Features

* **Desktop Companion Widget**: A fully transparent, Live2D-style animated mascot that lives on your desktop. It breathes, blinks, and walks natively using PyQt6's rendering engine.
* **DevOps Learning Tracker**: A dedicated dashboard to track your progress across 12 core DevOps topics (e.g., Docker, Kubernetes, CI/CD, AWS) with revision tracking and project counts.
* **GitHub Integration**: Connect your GitHub account to visualize your 52-week contribution heatmap, current/longest streaks, and repository statistics natively in the app using GraphQL and REST APIs.
* **Gamified Achievements**: Unlock milestone badges (with animated confetti and applause sounds!) for completing tasks and hitting learning goals.
* **Smart Reminders**: Stay healthy and productive with customizable interval reminders (hydration, posture, eye breaks) delivered via native Windows Toast Notifications and the companion widget.
* **Customizable Dashboard**: Dark/Light mode, custom motivational quotes, and a central hub for all your daily tasks.

## 🛠️ Tech Stack & Architecture

* **Frontend**: PyQt6 for building a fast, native Windows GUI with complex custom widgets (like the GitHub Heatmap and transparent frameless window).
* **Backend**: Python 3.x
* **Database**: SQLite3 for lightweight, local, and persistent storage of tasks, habits, and stats.
* **Concurrency**: Multi-threading (`QThread`) ensures that background polling (like GitHub API syncing and reminder scheduling) never blocks or freezes the GUI.
* **Integrations**: Uses `requests` for GitHub API calls and PowerShell `WinRT` bridges for native Windows 11 notifications. 

## 🚀 Getting Started

### Prerequisites
* Python 3.10+
* Git

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Sonie03/sonie-tech-lab.git
   cd sonie-tech-lab
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python main.py
   ```

### Building the Executable
You can compile DevBuddy AI into a single `.exe` file so you don't need to launch it from a terminal.
```bash
pyinstaller devbuddy.spec
```
The compiled application will be available in the `dist` folder!

## 📸 Screenshots
*(Add your beautiful UI screenshots here!)*
* Dashboard View
* Desktop Companion Walking
* GitHub Heatmap integration

## 🤝 Contributing
Contributions, issues, and feature requests are welcome! 

## 📝 License
This project is open-source.
