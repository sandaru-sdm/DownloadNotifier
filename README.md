# Python Download Notifier

A simple yet effective desktop application built with **Python** and **Tkinter** that monitors specified download directories and notifies you with an alarm sound and a pop-up message when a new file finishes downloading. It features system tray integration for background operation, a customizable UI with light/dark themes, and a "Stop Alarm" button.

---

## ✨ Features

* **Real-time Monitoring:** Watches one or more specified directories (including subdirectories) for new file creations and movements.

* **Intelligent Download Detection:** Employs a robust heuristic to determine when a file has truly finished downloading, filtering out common temporary download files.

* **Audible Alarm:** Plays a customizable sound file (WAV or MP3) to grab your attention when a download completes.

* **Instant Notification:** Displays a pop-up message simultaneously with the alarm sound.

* **System Tray Integration:** Minimizes to the system tray instead of closing, allowing it to run silently in the background while still monitoring and notifying.

* **Restore/Exit from Tray:** Easily restore the main window or completely exit the application via the system tray icon's context menu.

* **Stop Alarm Button:** Provides a dedicated button to quickly silence the alarm at any time.

* **Themable UI:** Toggle between beautiful light and dark themes for a personalized visual experience.

* **Download Log:** Maintains a running log of detected downloads and status updates within the application window.

---

## 🚀 Getting Started

Follow these steps to get your Download Notifier up and running on your Windows PC.

### Prerequisites

Ensure you have **Python 3.x** installed on your system. You can download the latest version from the official Python website:

* [Download Python](https://www.python.org/downloads/)

**Important:** During Python installation, make sure to check the box that says **"Add Python to PATH"** (or similar). This makes it much easier to run Python commands from your terminal.

### Installation (From Source)

1.  **Clone or Download the Repository:** Open your Git Bash, PowerShell, or Command Prompt. Navigate to the directory where you want to save your project.

    If you're using Git, clone the repository:

    ```bash
    git clone https://github.com/sandaru-sdm/DownloadNotifier.git
    cd DownloadNotifier
    ```

    (Ensure you replace `sandaru-sdm` with your actual GitHub username if you forked the repository).

    Alternatively, you can download the project as a ZIP file from GitHub and extract it to a folder on your computer.

2.  **Install Required Python Libraries:** Navigate into your `DownloadNotifier` project folder (e.g., `cd C:\Users\YourUser\Downloads\DownloadNotifier`) in your terminal and run the following commands:

    ```bash
    pip install watchdog
    pip install pygame
    pip install pystray Pillow
    ```

### Setting Up the Alarm Sound

The application needs an alarm sound file to play when a download finishes.

1.  **Choose Your Sound:** Find a `.wav` or `.mp3` sound file that you'd like to use as your alarm.

2.  **Rename the File:** Rename this sound file to `alarm.wav` (or `alarm.mp3` if you prefer MP3 and update the `ALARM_SOUND_FILE` variable in `download_notifier.py`).

3.  **Place the File:** Put the `alarm.wav` (or `alarm.mp3`) file directly into the **root of your `DownloadNotifier` project folder**, alongside `download_notifier.py`.

    **Important:** If the `alarm.wav` (or `alarm.mp3`) file is not found, the application will create an empty dummy file, but no sound will play. Ensure you replace it with a real audio file for the alarm to function correctly.

---

## 💻 How to Run

You have two ways to run the Download Notifier:

### 1. Running from Source (Requires Python Installation)

1.  **Navigate to the Project Directory:** Open your terminal or Command Prompt and change your current directory to the `DownloadNotifier` folder:

    ```bash
    cd path\to\your\DownloadNotifier
    ```

    (e.g., `C:\Users\maduh\Downloads\DownloadNotifier`).

2.  **Execute the Script:** Run the Python script:

    ```bash
    python download_notifier.py
    ```

### 2. Running the Executable (.exe) (No Python Installation Needed)

If you've created the standalone executable (as described in the "Creating the Executable" section below), you can run it directly:

1.  **Locate the Executable:** Navigate to the `dist` folder within your `DownloadNotifier` project directory.

    ```
    DownloadNotifier/
    └── dist/
        └── download_notifier.exe  <-- This is your executable!
    ```

2.  **Run the Executable:** Double-click `download_notifier.exe`.

    **Note:** When running the `.exe`, you **do not need Python or any of the libraries installed** on your PC. PyInstaller has bundled everything necessary into this single file, making it portable.

---

## ⚙️ Usage

Once the application window appears:

1.  **Monitor Directories:**

    * The "Monitor Directories" field will default to your system's standard Downloads folder.

    * You can change this path by typing in a new directory.

    * **To monitor multiple directories**, separate each path with a comma (e.g., `C:\Users\YourUser\Downloads, D:\MyIDMDownloads, E:\TelegramFiles`). The application will monitor all valid paths you provide, including their subdirectories.

    * Click the **"Browse"** button to easily select a directory using a file dialog.

2.  **Start Monitoring:**

    * Click the **"Start Monitoring"** button. The status label will update, indicating that monitoring has begun.

3.  **Download Files:**

    * Start downloading files using your web browser, Internet Download Manager (IDM), Telegram, or any other application that saves files to the monitored directory(ies).

4.  **Notifications & Alarm:**

    * When a download completes, you will simultaneously see a **"Download Complete" pop-up message** and hear the **alarm sound**.

5.  **Stop Alarm:**

    * If the alarm is playing, the **"Stop Alarm"** button will become active. Click it to immediately silence the alarm.

6.  **Minimize to System Tray:**

    * Click the **'X' (close) button** on the window. The window will hide, and the application will minimize to your system tray (near the clock). It will continue monitoring in the background.

    * **To restore the window:** Left-click the tray icon, or right-click and select "Show Window."

7.  **Stop Monitoring:**

    * Click the **"Stop Monitoring"** button to stop watching the directories for new downloads.

8.  **Theme Toggle:**

    * Use the **"Switch to Dark Theme"** (or "Switch to Light Theme") button in the top-right corner to change the application's appearance.

9.  **About Section:**

    * Click the **"About" link** at the bottom of the window to view application version and credit information.

---

## 📦 Creating the Executable (For Developers/Distribution)

If you want to distribute your application as a single executable file that doesn't require Python installation, you can use **PyInstaller**.

1.  **Install PyInstaller:**

    ```bash
    pip install pyinstaller
    ```

2.  **Navigate to Your Project Directory:** Open your terminal and go to your `DownloadNotifier` project folder.

3.  **Run PyInstaller Command:** Use the following command, ensuring you specify your alarm sound file correctly:

    If your alarm file is `alarm.wav`:

    ```bash
    pyinstaller --onefile --windowed --add-data "alarm.wav;." --icon "app_icon.ico" download_notifier.py
    ```

    If your alarm file is `alarm.mp3`:

    ```bash
    pyinstaller --onefile --windowed --add-data "alarm.mp3;." --icon "app_icon.ico" download_notifier.py
    ```

    * `--onefile`: Bundles everything into a single `.exe` file.

    * `--windowed`: Prevents a console window from appearing.

    * `--add-data "alarm.wav;."`: Includes your `alarm.wav` (or `alarm.mp3`) file in the executable.

    * `--icon "app_icon.ico"`: (Optional) If you have a custom `.ico` file (e.g., `app_icon.ico`) for your application's icon, place it in your project folder and specify its name here. Otherwise, PyInstaller uses a default icon.

4.  **Find Your Executable:** After PyInstaller finishes, your `download_notifier.exe` will be located in the newly created `dist` folder:

    ```
    DownloadNotifier/
    ├── build/             # Intermediate build files
    ├── dist/              # Contains your executable!
    │   └── download_notifier.exe
    ├── download_notifier.py
    ├── alarm.wav          # Your alarm sound file
    └── download_notifier.spec # PyInstaller specification file
    ```

---

## ⚠️ Troubleshooting

* **`ModuleNotFoundError`:** If you see this error when running from source, ensure you've installed all required libraries using `pip install watchdog pygame pystray Pillow`.

* **`_tkinter.TclError`:** This indicates a UI configuration issue. Ensure your code matches the latest version provided in the Canvas.

* **No Sound Plays:**

    * Verify `alarm.wav` (or `alarm.mp3`) is in the correct location (same folder as `download_notifier.py` for source, or correctly bundled by PyInstaller for `.exe`).

    * Ensure the sound file is not corrupted and is a valid WAV or MP3 format.

    * Check your system's audio output.

* **Downloads Not Detected:**

    * Confirm that the "Monitor Directories" path(s) in the application are absolutely correct and match where your files are being saved.

    * Ensure "Monitoring started" is displayed.

    * Some download managers might use very unique temporary file extensions or subfolders. The current code includes robust handling, but if issues persist, you might need to inspect the exact temporary file names/locations your specific downloader uses.

* **Executable (`.exe`) Issues:**

    * If the `.exe` doesn't run, try running it from the Command Prompt to see if any error messages appear.

    * Antivirus software can sometimes block PyInstaller executables (false positives). You might need to add an exception.

---

## 🙏 Contributing

Contributions are welcome! If you have ideas for improvements, bug fixes, or new features, feel free to:

1.  **Fork** this repository.

2.  **Create a new branch** (`git checkout -b feature/your-feature-name`).

3.  **Make your changes** and commit them (`git commit -m "Add new feature"`).

4.  **Push your branch** (`git push origin feature/your-feature-name`).

5.  **Open a Pull Request** to the `main` branch of this repository.

**Created by: Sandaru Gunathilake**

**Happy Downloading!**
