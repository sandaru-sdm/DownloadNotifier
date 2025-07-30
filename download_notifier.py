import tkinter as tk
from tkinter import filedialog, messagebox
import os
import time
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import pygame # Used for playing alarm sounds
import pystray # For system tray functionality
from PIL import Image, ImageDraw # For creating tray icon

# --- Configuration ---
# Default download directory (can be changed by user)
# This is a common path for Windows downloads.
DEFAULT_DOWNLOAD_DIR = os.path.join(os.path.expanduser("~"), "Downloads")
# Pygame supports both WAV and MP3.
# Make sure you have an alarm.wav or alarm.mp3 file in the same directory as this script.
ALARM_SOUND_FILE = "alarm.wav" # You can change this to "alarm.mp3" if you prefer

# --- Theme Configuration ---
LIGHT_THEME = {
    "bg": "#f0f0f0",  # Light grey background
    "fg": "#333333",  # Dark grey foreground
    "button_bg": "#4CAF50", # Green for start
    "button_fg": "white",
    "stop_button_bg": "#f44336", # Red for stop
    "stop_button_fg": "white", # White text for stop button in light theme
    "text_bg": "white",
    "text_fg": "#333333",
    "entry_bg": "white",
    "entry_fg": "#333333",
    "browse_button_bg": "#2196F3", # Blue for browse
    "browse_button_fg": "white",
    "toggle_button_bg": "#607D8B", # Grey-blue for toggle
    "toggle_button_fg": "white",
    "stop_alarm_button_bg": "#FFC107", # Amber for stop alarm
    "stop_alarm_button_fg": "black",
    "about_link_fg": "#0000EE", # Standard blue for links
    "footer_fg": "#666666" # Darker grey for footer in light theme
}

DARK_THEME = {
    "bg": "#1e1e1e",  # Very dark background, almost black
    "fg": "#e0e0e0",  # Light grey foreground for general text
    "button_bg": "#28a745", # Slightly brighter green for start
    "button_fg": "white",
    "stop_button_bg": "#dc3545", # Slightly brighter red for stop
    "stop_button_fg": "white", # White text for stop button in dark theme (as requested)
    "text_bg": "#2a2a2a", # Slightly lighter dark grey for text areas
    "text_fg": "#f8f8f8", # Near white for text area content
    "entry_bg": "#3a3a3a", # Distinct dark grey for entry fields
    "entry_fg": "#f8f8f8", # Near white for entry text
    "browse_button_bg": "#007bff", # Brighter blue for browse
    "browse_button_fg": "white",
    "toggle_button_bg": "#6c757d", # Medium grey for toggle
    "toggle_button_fg": "white",
    "stop_alarm_button_bg": "#ffc107", # Amber for stop alarm
    "stop_alarm_button_fg": "black", # Black text for contrast on amber
    "about_link_fg": "#87CEEB", # Sky blue for links in dark theme
    "footer_fg": "#999999" # Lighter grey for footer in dark theme
}

# --- File System Event Handler ---
class DownloadHandler(FileSystemEventHandler):
    """
    Handles file system events, specifically file creation and movement,
    to detect completed downloads.
    """
    def __init__(self, app_instance):
        super().__init__()
        self.app = app_instance
        self.download_queue = [] # To store paths of newly created files
        self.processing_thread = None
        self.stop_processing_event = threading.Event()

    def _is_file_temporary(self, file_path):
        """
        Checks if a file path indicates a temporary download file.
        """
        file_name_lower = os.path.basename(file_path).lower()
        temp_extensions = (
            ".tmp", ".crdownload", ".part", ".download", ".filepart",
            ".idm", ".idm.tmp", ".idm.bak", ".dwnl", ".inprogress",
            ".downloading", ".temp", ".partial", ".resume",
            ".rar", ".zip", # Sometimes archives are created as temp files (though less common for direct temp)
            "~", # Files starting with ~ are often temporary
        )
        for ext in temp_extensions:
            if ext.startswith("."): # Check for extensions
                if file_name_lower.endswith(ext):
                    return True
            else: # Check for patterns in file name
                if ext in file_name_lower:
                    return True
        # Also check if the file name contains common temporary markers
        if "temp" in file_name_lower or "tmp" in file_name_lower:
            return True
        return False

    def _add_to_queue_if_not_temp(self, file_path):
        """Adds a file to the processing queue if it's not a temporary file."""
        if not self._is_file_temporary(file_path):
            self.download_queue.append(file_path)
            self.app.update_status(f"Detected new file: {os.path.basename(file_path)}")
            # Start a processing thread if not already running
            if not self.processing_thread or not self.processing_thread.is_alive():
                self.stop_processing_event.clear()
                self.processing_thread = threading.Thread(target=self._process_downloads)
                self.processing_thread.daemon = True # Allow thread to exit with main app
                self.processing_thread.start()
        else:
            self.app.update_status(f"Skipped temporary file: {os.path.basename(file_path)}")
            self.app._log_message(f"Skipped temporary file: {os.path.basename(file_path)}", "info")


    def on_created(self, event):
        """Called when a file or directory is created."""
        if not event.is_directory:
            self._add_to_queue_if_not_temp(event.src_path)

    def on_moved(self, event):
        """
        Called when a file or directory is moved/renamed.
        This is crucial for detecting completed browser downloads.
        """
        if not event.is_directory:
            # When a file is moved/renamed, the destination path is the final, completed file.
            self._add_to_queue_if_not_temp(event.dest_path)

    def _process_downloads(self):
        """
        Processes files in the download queue to determine if they are complete.
        This runs in a separate thread to avoid blocking the GUI.
        """
        while self.download_queue and not self.stop_processing_event.is_set():
            file_path = self.download_queue.pop(0) # Get the first file in queue
            self.app.update_status(f"Checking download status for: {os.path.basename(file_path)}")
            if self._is_download_complete(file_path):
                self.app.notify_download_complete(file_path)
            else:
                # If not complete, put it back to re-check later
                self.download_queue.append(file_path)
                time.sleep(1) # Wait a bit before re-checking

    def _is_download_complete(self, file_path, check_interval=1, stable_checks=3):
        """
        Heuristic to determine if a download is complete.
        Checks if the file size remains stable over several intervals.
        """
        if not os.path.exists(file_path):
            return False # File might have been moved or deleted

        last_size = -1
        for i in range(stable_checks):
            try:
                current_size = os.path.getsize(file_path)
                if current_size == last_size and current_size > 0:
                    # Size is stable and not zero, likely complete
                    # Add a small delay after confirming stability to be extra sure
                    time.sleep(0.5)
                    return True
                last_size = current_size
                time.sleep(check_interval)
            except FileNotFoundError:
                # File might have been moved/deleted during checks, consider it complete if it existed before
                if i > 0: # If it existed for at least one check
                    return True # Assume it was moved/completed
                return False # Otherwise, it just didn't exist
            except Exception as e:
                self.app.update_status(f"Error checking file size for {os.path.basename(file_path)}: {e}")
                return False # Other error, assume not complete or problematic

        # If after several checks, size is still changing or zero, assume not complete
        return False

    def stop_processing(self):
        """Signals the processing thread to stop."""
        self.stop_processing_event.set()
        if self.processing_thread and self.processing_thread.is_alive():
            # Give it a moment to finish current task, then join
            self.processing_thread.join(timeout=2)

# --- Main Application Class ---
class DownloadNotifierApp:
    def __init__(self, master):
        self.master = master
        master.title("Download Notifier")
        # Set initial geometry to calculate center later
        master.geometry("600x450")
        master.resizable(False, False)

        self.monitor_path = tk.StringVar(value=DEFAULT_DOWNLOAD_DIR)
        self.observers = [] # List to hold multiple Observer instances
        self.event_handler = None
        self.is_monitoring = False
        self.current_theme = "light" # Initial theme
        self.tray_icon = None # For pystray icon

        # Initialize Pygame mixer here as well, in case it wasn't done in __main__
        # This ensures mixer is ready for the sound thread.
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init()
            except Exception as e:
                print(f"Could not initialize Pygame mixer in app: {e}")


        self._create_widgets()
        self._apply_theme(LIGHT_THEME) # Apply initial theme
        self._center_window() # Center the window after widgets are created and theme applied

        # Set up window close protocol to minimize to tray
        self.master.protocol("WM_DELETE_WINDOW", self._minimize_to_tray)
        self._setup_tray_icon() # Setup tray icon immediately

    def _center_window(self):
        """Centers the Tkinter window on the screen."""
        self.master.update_idletasks() # Update window to get accurate dimensions
        width = self.master.winfo_width()
        height = self.master.winfo_height()
        x = (self.master.winfo_screenwidth() // 2) - (width // 2)
        y = (self.master.winfo_screenheight() // 2) - (height // 2)
        self.master.geometry(f'{width}x{height}+{x}+{y}')

    def _create_widgets(self):
        """Initializes and places all GUI elements."""
        # Configure a consistent font
        self.default_font = ("Segoe UI", 10)
        self.title_font = ("Segoe UI", 12, "bold")
        self.app_title_font = ("Segoe UI", 16, "bold") # Larger font for app title
        self.footer_font = ("Segoe UI", 8) # Smaller font for footer

        # Header frame for title and theme toggle
        header_frame = tk.Frame(self.master, padx=15, pady=10)
        header_frame.pack(fill="x")

        self.app_title_label = tk.Label(header_frame, text="Download Notifier", font=self.app_title_font)
        self.app_title_label.pack(side="left", expand=True, anchor="w") # Align left

        self.theme_toggle_button = tk.Button(
            header_frame,
            text="Switch to Dark Theme",
            command=self._toggle_theme,
            font=self.default_font,
            relief="raised",
            bd=2,
            padx=10,
            pady=5
        )
        self.theme_toggle_button.pack(side="right", anchor="e") # Align right

        # Main content frame with padding
        main_content_frame = tk.Frame(self.master, padx=15, pady=10)
        main_content_frame.pack(fill="both", expand=True)

        # Path selection frame
        path_frame = tk.Frame(main_content_frame, pady=5)
        path_frame.pack(fill="x")

        tk.Label(path_frame, text="Monitor Directories (comma-separated):", font=self.default_font).pack(side="left", padx=(0, 5))
        self.path_entry = tk.Entry(path_frame, textvariable=self.monitor_path, font=self.default_font, relief="flat", bd=2)
        self.path_entry.pack(side="left", expand=True, fill="x", padx=(0, 5))
        self.browse_button = tk.Button(
            path_frame,
            text="Browse",
            command=self._browse_directory,
            font=self.default_font,
            relief="raised",
            bd=2,
            padx=10,
            pady=2
        )
        self.browse_button.pack(side="left")

        # Control buttons frame
        button_frame = tk.Frame(main_content_frame, pady=10)
        button_frame.pack(fill="x")

        self.start_button = tk.Button(
            button_frame,
            text="Start Monitoring",
            command=self.start_monitoring,
            font=self.title_font,
            relief="raised",
            bd=3,
            padx=15,
            pady=8
        )
        self.start_button.pack(side="left", expand=True, fill="x", padx=(0, 5))

        self.stop_button = tk.Button(
            button_frame,
            text="Stop Monitoring",
            command=self.stop_monitoring,
            font=self.title_font,
            relief="raised",
            bd=3,
            padx=15,
            pady=8,
            state="disabled"
        )
        self.stop_button.pack(side="left", expand=True, fill="x", padx=(5, 0))

        # Stop Alarm Button
        self.stop_alarm_button = tk.Button(
            main_content_frame,
            text="Stop Alarm",
            command=self.stop_alarm,
            font=self.title_font,
            relief="raised",
            bd=3,
            padx=15,
            pady=8,
            state="disabled" # Disabled by default
        )
        self.stop_alarm_button.pack(fill="x", pady=(5, 5)) # Adjusted pady for spacing

        # Status label
        self.status_label = tk.Label(main_content_frame, text="Ready to monitor...", wraplength=550, justify="left", font=self.default_font)
        self.status_label.pack(padx=5, pady=(0, 10), fill="x", expand=True)

        # Download history/log
        log_frame = tk.Frame(main_content_frame, bd=2, relief="sunken")
        log_frame.pack(fill="both", expand=True)

        self.log_text = tk.Text(log_frame, height=8, width=60, state="disabled", font=("Consolas", 9), wrap="word")
        self.log_text.pack(side="left", fill="both", expand=True)
        self.log_text.tag_config("download", foreground="blue")
        self.log_text.tag_config("error", foreground="red")
        self.log_text.tag_config("info", foreground="grey") # New tag for general info

        # Scrollbar for log text
        scrollbar = tk.Scrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.log_text.config(yscrollcommand=scrollbar.set)

        # Footer frame
        footer_frame = tk.Frame(self.master, padx=15, pady=5)
        footer_frame.pack(fill="x", side="bottom")

        # About link in footer (now the only element in the footer)
        self.about_link_label = tk.Label(
            footer_frame,
            text="About",
            font=self.footer_font,
            cursor="hand2", # Changes cursor to a hand on hover
            relief="flat" # No border
        )
        # Pack this label in the center of the footer frame
        self.about_link_label.pack(side="bottom", anchor="center", pady=(0,0)) # Centered horizontally
        self.about_link_label.bind("<Button-1>", lambda e: self._show_about())
        self.about_link_label.bind("<Enter>", self._on_about_link_enter)
        self.about_link_label.bind("<Leave>", self._on_about_link_leave)

        # List of widgets to apply theme to
        self.themable_widgets = [
            self.master, header_frame, main_content_frame, path_frame, button_frame, log_frame, footer_frame,
            self.app_title_label, self.status_label, self.log_text, self.path_entry,
            self.start_button, self.stop_button, self.browse_button,
            self.theme_toggle_button, self.stop_alarm_button,
            self.about_link_label # Only the about link label remains
        ]
        # Add labels in path_frame
        for widget in path_frame.winfo_children():
            if isinstance(widget, tk.Label):
                self.themable_widgets.append(widget)


    def _apply_theme(self, theme_colors):
        """Applies the specified theme colors to the widgets."""
        # The root window (self.master) only supports 'bg' for background
        self.master.config(bg=theme_colors["bg"])

        for widget in self.themable_widgets:
            # Skip the root window as it's handled above
            if widget == self.master:
                continue

            if isinstance(widget, tk.Text):
                widget.config(bg=theme_colors["text_bg"], fg=theme_colors["text_fg"])
                # Update tag colors for log text
                widget.tag_config("download", foreground=theme_colors["fg"] if self.current_theme == "dark" else "blue")
                widget.tag_config("error", foreground=theme_colors["fg"] if self.current_theme == "dark" else "red")
                widget.tag_config("info", foreground="grey" if self.current_theme == "light" else "#a0a0a0")
            elif isinstance(widget, tk.Entry):
                widget.config(bg=theme_colors["entry_bg"], fg=theme_colors["entry_fg"], insertbackground=theme_colors["fg"])
            elif isinstance(widget, tk.Button):
                # Specific button colors from theme
                if widget == self.start_button:
                    widget.config(bg=theme_colors["button_bg"], fg=theme_colors["button_fg"])
                elif widget == self.stop_button:
                    widget.config(bg=theme_colors["stop_button_bg"], fg=theme_colors["stop_button_fg"]) # Use specific stop button foreground
                elif widget == self.browse_button:
                    widget.config(bg=theme_colors["browse_button_bg"], fg=theme_colors["browse_button_fg"])
                elif widget == self.theme_toggle_button:
                    widget.config(bg=theme_colors["toggle_button_bg"], fg=theme_colors["toggle_button_fg"])
                elif widget == self.stop_alarm_button:
                    widget.config(bg=theme_colors["stop_alarm_button_bg"], fg=theme_colors["stop_alarm_button_fg"])
            elif isinstance(widget, tk.Label):
                # Apply foreground based on label type
                if widget == self.about_link_label:
                    widget.config(bg=theme_colors["bg"], fg=theme_colors["about_link_fg"])
                    # Reset font to default (not underlined) when applying theme
                    widget.config(font=self.footer_font)
                else: # General labels (including app_title_label and path_frame labels)
                    widget.config(bg=theme_colors["bg"], fg=theme_colors["fg"])
            elif isinstance(widget, tk.Frame):
                widget.config(bg=theme_colors["bg"])


    def _toggle_theme(self):
        """Switches between dark and light themes."""
        if self.current_theme == "light":
            self._apply_theme(DARK_THEME)
            self.current_theme = "dark"
            self.theme_toggle_button.config(text="Switch to Light Theme")
        else:
            self._apply_theme(LIGHT_THEME)
            self.current_theme = "light"
            self.theme_toggle_button.config(text="Switch to Dark Theme")

    def _browse_directory(self):
        """Opens a directory selection dialog."""
        selected_dir = filedialog.askdirectory(initialdir=self.monitor_path.get())
        if selected_dir:
            self.monitor_path.set(selected_dir)

    def start_monitoring(self):
        """Starts monitoring the selected directory."""
        paths_to_monitor_str = self.monitor_path.get()
        # Split by comma and clean up whitespace, filter out empty strings
        paths = [p.strip() for p in paths_to_monitor_str.split(',') if p.strip()]

        if not paths:
            messagebox.showerror("Error", "No directories specified for monitoring.")
            return

        if self.is_monitoring:
            self.update_status("Already monitoring.")
            return

        self.event_handler = DownloadHandler(self)
        self.observers = [] # Reset list of observers
        monitoring_successful_paths = []

        for path_to_monitor in paths:
            if not os.path.isdir(path_to_monitor):
                self._log_message(f"Warning: Invalid directory path skipped: {path_to_monitor}", "error")
                continue
            try:
                # Changed recursive to True to monitor subdirectories
                observer = Observer()
                observer.schedule(self.event_handler, path_to_monitor, recursive=True)
                observer.start()
                self.observers.append(observer)
                monitoring_successful_paths.append(path_to_monitor)
            except Exception as e:
                self._log_message(f"Failed to start monitoring for {path_to_monitor}: {e}", "error")

        if monitoring_successful_paths:
            self.is_monitoring = True
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
            self.update_status(f"Monitoring started for: {', '.join(monitoring_successful_paths)}")
            self._log_message(f"Monitoring started for: {', '.join(monitoring_successful_paths)}", "info")
        else:
            messagebox.showerror("Error", "No valid directories found to start monitoring.")
            self.update_status("Monitoring failed: No valid directories.")


    def stop_monitoring(self):
        """Stops monitoring the directory."""
        if not self.is_monitoring:
            self.update_status("Not currently monitoring.")
            return

        for observer in self.observers:
            observer.stop()
        for observer in self.observers:
            observer.join() # Wait for all observer threads to terminate
        self.observers = [] # Clear the list of observers

        if self.event_handler:
            self.event_handler.stop_processing() # Stop the download processing thread
            self.event_handler = None

        self.is_monitoring = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.update_status("Monitoring stopped.")
        self._log_message("Monitoring stopped.", "info")

    def stop_alarm(self):
        """Stops the currently playing alarm sound."""
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            self.stop_alarm_button.config(state="disabled")
            self.update_status("Alarm stopped.")
            self._log_message("Alarm manually stopped.", "info")
        else:
            self.update_status("No alarm is currently playing.")

    def update_status(self, message):
        """Updates the status label in the GUI."""
        self.master.after(0, lambda: self.status_label.config(text=message))

    def _log_message(self, message, tag=None):
        """Adds a message to the log text area."""
        self.master.after(0, lambda: self._insert_log_message(message, tag))

    def _insert_log_message(self, message, tag):
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {message}\n", tag)
        self.log_text.see(tk.END) # Scroll to the end
        self.log_text.config(state="disabled")

    def notify_download_complete(self, file_path):
        """
        Triggers the notification (sound and GUI update) when a download is complete.
        This method is called from the DownloadHandler thread, so it uses master.after()
        to safely update the GUI.
        """
        download_name = os.path.basename(file_path)
        self.master.after(0, lambda: self._show_notification_and_play_sound(download_name))
        self._log_message(f"Download complete: {download_name}", "download")

    def _play_alarm_sound(self):
        """Plays the alarm sound using pygame.mixer.music."""
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init() # Ensure mixer is initialized in this thread if it wasn't already

            pygame.mixer.music.load(ALARM_SOUND_FILE)
            pygame.mixer.music.play()
            self.master.after(0, lambda: self.stop_alarm_button.config(state="normal")) # Enable stop button
            # Wait for sound to finish, then disable stop button
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            self.master.after(0, lambda: self.stop_alarm_button.config(state="disabled")) # Disable stop button
        except pygame.error as e:
            self._log_message(f"Error playing sound with Pygame in thread: {e}. Check if '{ALARM_SOUND_FILE}' exists and is a valid audio file.", "error")
        except Exception as e:
            self._log_message(f"An unexpected error occurred in sound thread: {e}", "error")

    def _show_notification_and_play_sound(self, download_name):
        """Helper to show notification and play sound on the main thread."""
        self.update_status(f"Download Complete: {download_name}!")

        # Start a new thread to play the alarm sound
        sound_thread = threading.Thread(target=self._play_alarm_sound)
        sound_thread.daemon = True # Allow thread to exit with main app
        sound_thread.start()

        # Show the message box on the main thread (this will block until dismissed)
        messagebox.showinfo("Download Complete", f"File '{download_name}' has finished downloading!")

    def _show_about(self):
        """Displays an about message box."""
        messagebox.showinfo(
            "About Download Notifier",
            "Version: 1.0.0\n"
            "Created by: Sandaru Gunathilake\n\n"
            "This application monitors specified directories for completed downloads\n"
            "and notifies you with an alarm and a pop-up."
        )

    def _on_about_link_enter(self, event):
        """Changes about link appearance on mouse enter."""
        current_theme_colors = DARK_THEME if self.current_theme == "dark" else LIGHT_THEME
        self.about_link_label.config(fg=current_theme_colors["about_link_fg"], font=(self.footer_font[0], self.footer_font[1], "underline"))

    def _on_about_link_leave(self, event):
        """Resets about link appearance on mouse leave."""
        current_theme_colors = DARK_THEME if self.current_theme == "dark" else LIGHT_THEME
        self.about_link_label.config(fg=current_theme_colors["about_link_fg"], font=self.footer_font)

    def _create_tray_icon_image(self):
        """Creates a simple square icon image for the system tray."""
        # You can replace this with a path to a .ico file if you have one
        # For simplicity, we'll draw a small square
        width = 64
        height = 64
        image = Image.new('RGBA', (width, height), (0, 0, 0, 0)) # Transparent background
        draw = ImageDraw.Draw(image)
        # Draw a simple green square (or a notification icon)
        draw.ellipse((0, 0, width, height), fill='green') # A green circle
        return image

    def _setup_tray_icon(self):
        """Sets up the system tray icon and its menu."""
        # Create the tray icon image
        icon_image = self._create_tray_icon_image()

        # Define the tray menu
        menu = (
            pystray.MenuItem('Show Window', self._show_window_from_tray),
            pystray.MenuItem('Exit', self._exit_application)
        )

        # Create the tray icon
        self.tray_icon = pystray.Icon("Download Notifier", icon_image, "Download Notifier", menu)

        # Run the icon in a separate thread to avoid blocking Tkinter's main loop
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def _show_window_from_tray(self, icon, item):
        """Restores the main window from the system tray."""
        self.master.deiconify() # Show the window
        self.master.state('normal') # Restore it to normal state (not minimized)
        self.master.lift() # Bring to front
        self.master.focus_force() # Give focus
        # It's important to stop the icon thread when the window is shown,
        # otherwise, it might prevent clean exit later or cause issues.
        # The icon will be re-run if the window is minimized again.
        if self.tray_icon and self.tray_icon._thread.is_alive():
            self.tray_icon.stop()


    def _minimize_to_tray(self):
        """Hides the main window and moves the application to the system tray."""
        self.master.withdraw() # Hide the window
        # Ensure the tray icon is running when minimizing
        if self.tray_icon and not self.tray_icon._thread.is_alive():
             threading.Thread(target=self.tray_icon.run, daemon=True).start()


    def _exit_application(self, icon, item):
        """Exits the application completely from the system tray."""
        icon.stop() # Stop the tray icon
        self.master.quit() # Quit the Tkinter main loop

    def on_closing(self):
        """Handles graceful shutdown when the window is closed."""
        # This method is now primarily for full exit, but WM_DELETE_WINDOW
        # is redirected to _minimize_to_tray by default.
        # This path is taken if _exit_application is called.
        if self.is_monitoring:
            self.stop_monitoring()
        # Ensure any playing music is stopped before quitting mixer
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        if pygame.mixer.get_init():
            pygame.mixer.quit()
        pygame.quit() # Quit pygame modules
        self.master.destroy()

# --- Main Execution ---
if __name__ == "__main__":
    # Initialize Pygame mixer (must be done before loading any sounds)
    try:
        pygame.init()
        pygame.mixer.init()
    except Exception as e:
        print(f"Could not initialize Pygame mixer: {e}. Ensure necessary audio drivers are installed.")
        # Exit if mixer cannot be initialized, as sound won't work
        exit()

    # Create a dummy alarm sound file if it doesn't exist for testing
    if not os.path.exists(ALARM_SOUND_FILE):
        try:
            # Note: Creating a dummy MP3 or WAV from scratch is complex.
            # This will just create an empty file. You MUST replace this
            # with an actual sound file for the alarm to work.
            with open(ALARM_SOUND_FILE, 'wb') as f:
                f.write(b'') # Create an empty file
            print(f"Created an empty dummy file '{ALARM_SOUND_FILE}'. Please replace it with a real .wav or .mp3 sound file.")
        except Exception as e:
            print(f"Could not create dummy alarm file: {e}. Please ensure '{ALARM_SOUND_FILE}' exists and is a .wav or .mp3 file.")


    root = tk.Tk()
    app = DownloadNotifierApp(root)
    # The WM_DELETE_WINDOW protocol is set in __init__ now
    root.mainloop()