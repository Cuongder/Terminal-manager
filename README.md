# 🖥️ Terminal Manager

**Terminal Manager** is a powerful desktop application that helps developers manage and execute command line tasks intuitively, efficiently, and aesthetically. Built with Python and CustomTkinter, it brings a modern terminal experience right to Windows.

![Banner](https://via.placeholder.com/800x400?text=Terminal+Manager+Screenshot)
*(Please replace this image with an actual screenshot of the application)*

## ✨ Key Features

*   **📁 Smart Project Management**: 
    *   Easily switch between project folders.
    *   Automatically remembers and provides quick access to recent projects.
    *   Displays detailed path and Git status.

*   **⚡ Flexible Command System**:
    *   **Built-in Commands**: Integrated with popular commands for Web Dev (NPM, Prisma, Docker...).
    *   **Custom Commands**: Freely add, edit, and delete your own custom commands with an intuitive interface.
    *   **Auto Port Kill**: Automatically detects and releases occupied ports (like 3000, 5555) before running a new command.

*   **📑 Multi-tasking Tabbed Interface**:
    *   Run multiple workflows (worker, server, build) in separate tabs.
    *   No more cluttered terminal windows.

*   **🎨 Modern Interface**:
    *   Default Dark Mode, easy on the eyes for programmers.
    *   Clean, minimalist design focused on performance.

## 🚀 Installation

Before starting, ensure your computer has [Python 3.10+](https://www.python.org/downloads/) installed.

1.  **Clone the repository**
    ```bash
    git clone https://github.com/username/terminal-manager.git
    cd terminal-manager
    ```

2.  **Install dependencies**
    Use `pip` to install the necessary packages from `requirements.txt`:
    ```bash
    pip install -r requirements.txt
    ```

## 📖 Usage Guide

1.  **Launch the application**
    ```bash
    python main.py
    ```

2.  **Select Project**
    *   Click **"📂 Browse Folder..."** to select your project directory.
    *   The app will automatically detect if it's a Git repository and verify the current branch.

3.  **Execute Commands**
    *   **Quick Commands**: Click on the available command buttons in the sidebar (e.g., *Build, Worker, Prisma Studio*).
    *   **Custom Commands**: 
        *   Click **"➕ Add Custom Command"**.
        *   Enter the display name (Label) and the command string (Command).
        *   The new command will appear with an **❌** button next to it for easy deletion.
    *   **Manual Run**: Enter a command in the input bar at the bottom and press `Enter` or the `Run` button.

4.  **Tips**
    *   Long-running commands (like `npm run dev`) will automatically open in a new Tab to avoid interrupting your workflow.
    *   You can type `GIT_COMMIT` to quickly open the code commit dialog.

## 🛠️ Technologies Used

*   **Python**: Main language.
*   **CustomTkinter**: Modern UI library based on Tkinter.
*   **Subprocess**: System process management.

## 🤝 Contribution

All contributions are welcome! If you find a bug or want to add a new feature:
1.  Fork the project.
2.  Create a feature branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

## 📄 License

This project is distributed under the MIT license. See the `LICENSE` file for more details.

---
*Developed with ❤️ by [Your Name]*
