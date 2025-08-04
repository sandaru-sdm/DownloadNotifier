# Python Download Notifier

A simple yet effective desktop application built with **Python** and **Tkinter** that monitors specified download directories and notifies you with an alarm sound and a pop-up message when a new file finishes downloading.

---

## ✨ Features

* **Real-time Monitoring:** Watches one or more specified directories (including subdirectories) for new file creations and movements.

* **Intelligent Download Detection:** Employs a robust heuristic to determine when a file has truly finished downloading, filtering out common temporary download files and using file size-based checks when possible.

* **Audible Alarm:** Plays a customizable sound file (WAV or MP3) to grab your attention when a download completes.

* **Instant Notification:** Displays a pop-up message simultaneously with the alarm sound.

* **Stop Alarm Button:** Provides a dedicated button to quickly silence the alarm at any time.

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
    git clone [https://github.com/sandaru-sdm/DownloadNotifier.git](https://github.com/sandaru-sdm/DownloadNotifier.git)
    cd DownloadNotifier
    ```

    Alternatively, you can download the project as a ZIP file from GitHub and extract it to a folder on your computer.

2.  **Install Required Python Libraries:** Navigate into your `DownloadNotifier` project folder (e.g., `cd C:\Users\YourUser\Downloads\DownloadNotifier`) in your terminal and run the following commands:

    ```bash
    pip install watchdog
    pip install pygame
    pip install requests
    ```

### Setting Up the Alarm Sound

The application needs an alarm sound file to play when a download finishes.

1.  **Choose Your Sound:** Find a `.wav` or `.mp3` sound file that you'd like to use as your alarm.

2.  **Rename the File:** Rename this sound file to `alarm.wav` (or `alarm.mp3` if you prefer MP3 and update the `ALARM_SOUND_FILE` variable in the script).

3.  **Place the File:** Put the `alarm.wav` (or `alarm.mp3`) file directly into the **root of your `DownloadNotifier` project folder**, alongside `download_notifier.py`.

    **Important:** If the `alarm.wav` (or `alarm.mp3`) file is not found, the application will create an empty dummy file, but no sound will play. Ensure you replace it with a real audio file for the alarm to function correctly.

---

## 💻 How to Run

1.  **Navigate to the Project Directory:** Open your terminal or Command Prompt and change your current directory to the `DownloadNotifier` folder:

    ```bash
    cd path\to\your\DownloadNotifier
    ```

    (e.g., `C:\Users\maduh\Downloads\DownloadNotifier`).

2.  **Execute the Script:** Run the Python script:

    ```bash
    python download_notifier.py
    ```

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

6.  **Stop Monitoring:**

    * Click the **"Stop Monitoring"** button to stop watching the directories for new downloads.

7.  **Exit the Application:**

    * Click the **'X' (close) button** on the window to stop monitoring and completely exit the application.

8.  **About Section:**

    * Click the **"About" link** at the bottom of the window to view application version and credit information.

---

## ⚠️ Troubleshooting

* **`ModuleNotFoundError`:** If you see this error when running from source, ensure you've installed all required libraries using `pip install watchdog pygame requests`.

* **`_tkinter.TclError`:** This indicates a UI configuration issue. Ensure your code is up to date.

* **No Sound Plays:**

    * Verify `alarm.wav` (or `alarm.mp3`) is in the correct location (same folder as `download_notifier.py`).
    * Ensure the sound file is not corrupted and is a valid WAV or MP3 format.
    * Check your system's audio output.

* **Downloads Not Detected:**

    * Confirm that the "Monitor Directories" path(s) in the application are absolutely correct and match where your files are being saved.
    * Ensure "Monitoring started" is displayed.
    * Some download managers might use very unique temporary file extensions or subfolders. The current code includes robust handling, but if issues persist, you might need to inspect the exact temporary file names/locations your specific downloader uses.

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