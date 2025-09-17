import tkinter as tk
from tkinter import messagebox, ttk
import time
import threading
import sys
import os
from datetime import datetime
import winreg as reg
import ctypes
from ctypes import wintypes

class EyeHealthReminder:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Completely hide main window
        self.root.overrideredirect(True)  # Remove window decorations
        self.running = True
        self.paused = False
        self.reminder_interval = 20 * 60  # 20 minutes in seconds
        self.setup_system_tray()
        
    def setup_system_tray(self):
        """Create system tray icon and menu"""
        try:
            # Create a simple tray icon using tkinter
            self.tray_menu = tk.Menu(self.root, tearoff=0)
            self.tray_menu.add_command(label="Show Settings", command=self.show_settings)
            self.tray_menu.add_separator()
            self.tray_menu.add_command(label="Pause Reminders", command=self.toggle_pause)
            self.tray_menu.add_command(label="Exit", command=self.quit_app)
            
            # Start reminder thread
            self.reminder_thread = threading.Thread(target=self.reminder_loop, daemon=True)
            self.reminder_thread.start()
            
            print("Eye Health Reminder started successfully!")
            print("The application is running in the background.")
            
        except Exception as e:
            print(f"Error setting up system tray: {e}")

    def reminder_loop(self):
        """Main reminder loop that runs in background"""
        while self.running:
            if not self.paused:
                time.sleep(self.reminder_interval)
                if self.running and not self.paused:
                    self.show_reminder()
            else:
                time.sleep(1)  # Check every second when paused

    def show_reminder(self):
        """Display the eye health reminder"""
        # Create standalone reminder window (not using root)
        reminder_window = tk.Toplevel()
        reminder_window.title("👁️ Eye Health Reminder")
        reminder_window.geometry("520x450")
        reminder_window.configure(bg='#e8f4fd')
        reminder_window.attributes('-topmost', True)
        reminder_window.resizable(False, False)
        
        # Center the window on screen
        screen_width = reminder_window.winfo_screenwidth()
        screen_height = reminder_window.winfo_screenheight()
        x = (screen_width - 520) // 2
        y = (screen_height - 450) // 2
        reminder_window.geometry(f"520x450+{x}+{y}")
        
        # Main container with consistent padding
        main_container = tk.Frame(reminder_window, bg='#e8f4fd')
        main_container.pack(fill='both', expand=True, padx=35, pady=35)
        
        # Header section
        header_frame = tk.Frame(main_container, bg='#e8f4fd')
        header_frame.pack(fill='x', pady=(0, 25))
        
        # Title with icon
        title_label = tk.Label(header_frame, text="👁️ Time for Eye Care!", 
                              font=('Segoe UI', 20, 'bold'), bg='#e8f4fd', fg='#2c5282')
        title_label.pack()
        
        # Content section
        content_frame = tk.Frame(main_container, bg='#e8f4fd')
        content_frame.pack(fill='both', expand=True, pady=(0, 25))
        
        # Main message
        main_message = "It's been 20 minutes of screen time!"
        main_label = tk.Label(content_frame, text=main_message, 
                             font=('Segoe UI', 14), bg='#e8f4fd', fg='#1a202c')
        main_label.pack(pady=(0, 20))
        
        # Rule explanation box
        rule_frame = tk.Frame(content_frame, bg='#ffffff', relief='solid', bd=2)
        rule_frame.pack(fill='x', pady=(0, 20))
        
        rule_title = tk.Label(rule_frame, text="Follow the 20-20-20 Rule:", 
                             font=('Segoe UI', 13, 'bold'), bg='#ffffff', fg='#2d3748')
        rule_title.pack(pady=(20, 10))
        
        rules = [
            "• Look at something 20 feet away",
            "• For at least 20 seconds", 
            "• Every 20 minutes"
        ]
        
        for rule in rules:
            rule_label = tk.Label(rule_frame, text=rule, font=('Segoe UI', 12), 
                                 bg='#ffffff', fg='#4a5568', anchor='w')
            rule_label.pack(pady=4, padx=25, fill='x')
        
        # Benefits text
        benefit_text = "This helps reduce eye strain and keeps your eyes healthy."
        benefit_label = tk.Label(rule_frame, text=benefit_text, 
                                font=('Segoe UI', 11, 'italic'), bg='#ffffff', fg='#718096')
        benefit_label.pack(pady=(10, 20))
        
        # Timer section
        timer_frame = tk.Frame(content_frame, bg='#fff3cd', relief='solid', bd=1)
        timer_frame.pack(fill='x', pady=(0, 15))
        
        self.timer_var = tk.StringVar()
        timer_label = tk.Label(timer_frame, textvariable=self.timer_var, 
                              font=('Segoe UI', 13, 'bold'), bg='#fff3cd', fg='#856404')
        timer_label.pack(pady=12)
        
        # Button section
        button_frame = tk.Frame(main_container, bg='#e8f4fd')
        button_frame.pack(fill='x')
        
        # Create button container for centering
        button_container = tk.Frame(button_frame, bg='#e8f4fd')
        button_container.pack()
        
        # Style buttons consistently
        button_style = {
            'font': ('Segoe UI', 12, 'bold'),
            'relief': 'flat',
            'cursor': 'hand2',
            'padx': 30,
            'pady': 10
        }
        
        # Done button
        done_button = tk.Button(button_container, text="✓ I took a break", 
                               command=lambda: self.close_reminder(reminder_window),
                               bg='#48bb78', fg='white', **button_style)
        done_button.pack(side='left', padx=(0, 20))
        
        # Snooze button  
        snooze_button = tk.Button(button_container, text="⏰ Snooze 5 min", 
                                 command=lambda: self.snooze_reminder(reminder_window),
                                 bg='#ed8936', fg='white', **button_style)
        snooze_button.pack(side='left')
        
        # Start countdown timer
        self.countdown_timer(reminder_window, 30)  # 30 second timer
        
        # Play system sound
        try:
            ctypes.windll.user32.MessageBeep(0x40)  # MB_ICONASTERISK
        except:
            pass
            
        # Handle window closing
        reminder_window.protocol("WM_DELETE_WINDOW", lambda: self.close_reminder(reminder_window))

    def countdown_timer(self, window, seconds):
        """Countdown timer for auto-close"""
        if seconds > 0:
            self.timer_var.set(f"Auto-close in {seconds}s")
            window.after(1000, lambda: self.countdown_timer(window, seconds-1))
        else:
            self.close_reminder(window)

    def close_reminder(self, window):
        """Close reminder window"""
        try:
            window.destroy()
        except:
            pass

    def snooze_reminder(self, window):
        """Snooze reminder for 5 minutes"""
        self.close_reminder(window)
        # Start snooze timer
        threading.Thread(target=self.snooze_timer, daemon=True).start()

    def snooze_timer(self):
        """5-minute snooze timer"""
        time.sleep(5 * 60)  # 5 minutes
        if self.running and not self.paused:
            self.show_reminder()

    def show_settings(self):
        """Show settings window"""
        settings_window = tk.Toplevel()
        settings_window.title("Eye Health Reminder - Settings")
        settings_window.geometry("400x300")
        settings_window.configure(bg='#f7fafc')
        settings_window.resizable(False, False)
        settings_window.attributes('-topmost', True)
        
        # Center window
        screen_width = settings_window.winfo_screenwidth()
        screen_height = settings_window.winfo_screenheight()
        x = (screen_width - 400) // 2
        y = (screen_height - 300) // 2
        settings_window.geometry(f"400x300+{x}+{y}")
        
        # Main container with consistent padding
        main_container = tk.Frame(settings_window, bg='#f7fafc')
        main_container.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Title
        title_label = tk.Label(main_container, text="⚙️ Settings", font=('Segoe UI', 16, 'bold'), 
                              bg='#f7fafc', fg='#2d3748')
        title_label.pack(pady=(0, 25))
        
        # Interval setting section
        interval_section = tk.Frame(main_container, bg='#ffffff', relief='solid', bd=1)
        interval_section.pack(fill='x', pady=(0, 20))
        
        # Interval header
        interval_header = tk.Frame(interval_section, bg='#ffffff')
        interval_header.pack(fill='x', padx=20, pady=(15, 10))
        
        tk.Label(interval_header, text="Reminder Interval", 
                font=('Segoe UI', 12, 'bold'), bg='#ffffff', fg='#2d3748').pack(anchor='w')
        
        # Interval controls
        interval_controls = tk.Frame(interval_section, bg='#ffffff')
        interval_controls.pack(fill='x', padx=20, pady=(0, 15))
        
        tk.Label(interval_controls, text="Minutes:", 
                bg='#ffffff', fg='#4a5568', font=('Segoe UI', 10)).pack(anchor='w')
        
        interval_var = tk.StringVar(value=str(self.reminder_interval // 60))
        interval_frame = tk.Frame(interval_controls, bg='#ffffff')
        interval_frame.pack(anchor='w', pady=(5, 0))
        
        interval_spin = tk.Spinbox(interval_frame, from_=5, to=60, textvariable=interval_var, 
                                  width=8, font=('Segoe UI', 10), relief='solid', bd=1)
        interval_spin.pack(side='left')
        
        tk.Label(interval_frame, text="(5-60 minutes)", 
                bg='#ffffff', fg='#718096', font=('Segoe UI', 9)).pack(side='left', padx=(10, 0))
        
        # Auto-start section
        autostart_section = tk.Frame(main_container, bg='#ffffff', relief='solid', bd=1)
        autostart_section.pack(fill='x', pady=(0, 25))
        
        autostart_container = tk.Frame(autostart_section, bg='#ffffff')
        autostart_container.pack(fill='x', padx=20, pady=15)
        
        autostart_var = tk.BooleanVar()
        autostart_check = tk.Checkbutton(autostart_container, text="Start automatically with Windows", 
                                        variable=autostart_var, bg='#ffffff', 
                                        font=('Segoe UI', 11), fg='#2d3748')
        autostart_check.pack(anchor='w')
        
        # Check current autostart status
        autostart_var.set(self.is_autostart_enabled())
        
        # Button section
        button_container = tk.Frame(main_container, bg='#f7fafc')
        button_container.pack()
        
        button_style = {
            'font': ('Segoe UI', 11, 'bold'),
            'relief': 'flat',
            'cursor': 'hand2',
            'padx': 20,
            'pady': 8
        }
        
        def save_settings():
            # Update interval
            try:
                new_interval = int(interval_var.get()) * 60
                if 5 <= new_interval // 60 <= 60:
                    self.reminder_interval = new_interval
                else:
                    messagebox.showerror("Error", "Please enter a value between 5 and 60 minutes")
                    return
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number for interval")
                return
            
            # Update autostart
            if autostart_var.get():
                if self.enable_autostart():
                    messagebox.showinfo("Settings", "Settings saved successfully!\nThe app will now start with Windows.")
                else:
                    messagebox.showwarning("Warning", "Settings saved, but autostart setup failed.\nYou may need administrator privileges.")
            else:
                if self.disable_autostart():
                    messagebox.showinfo("Settings", "Settings saved successfully!\nAutostart disabled.")
                else:
                    messagebox.showwarning("Warning", "Settings saved, but autostart removal failed.")
            
            settings_window.destroy()
        
        # Buttons
        save_btn = tk.Button(button_container, text="💾 Save Settings", command=save_settings,
                            bg='#48bb78', fg='white', **button_style)
        save_btn.pack(side='left', padx=(0, 15))
        
        cancel_btn = tk.Button(button_container, text="✕ Cancel", command=settings_window.destroy,
                              bg='#a0aec0', fg='white', **button_style)
        cancel_btn.pack(side='left')
        
        # Handle window closing
        settings_window.protocol("WM_DELETE_WINDOW", settings_window.destroy)

    def toggle_pause(self):
        """Toggle pause/resume reminders"""
        self.paused = not self.paused
        status = "paused" if self.paused else "resumed"
        print(f"Reminders {status}")

    def is_autostart_enabled(self):
        """Check if autostart is enabled"""
        try:
            key = reg.OpenKey(reg.HKEY_CURRENT_USER, 
                            r"Software\Microsoft\Windows\CurrentVersion\Run")
            reg.QueryValueEx(key, "EyeHealthReminder")
            reg.CloseKey(key)
            return True
        except FileNotFoundError:
            return False
        except Exception:
            return False

    def enable_autostart(self):
        """Enable autostart with Windows"""
        try:
            key = reg.OpenKey(reg.HKEY_CURRENT_USER, 
                            r"Software\Microsoft\Windows\CurrentVersion\Run", 0, reg.KEY_SET_VALUE)
            script_path = os.path.abspath(__file__)
            python_path = sys.executable
            command = f'"{python_path}" "{script_path}"'
            reg.SetValueEx(key, "EyeHealthReminder", 0, reg.REG_SZ, command)
            reg.CloseKey(key)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to enable autostart: {e}")
            return False

    def disable_autostart(self):
        """Disable autostart with Windows"""
        try:
            key = reg.OpenKey(reg.HKEY_CURRENT_USER, 
                            r"Software\Microsoft\Windows\CurrentVersion\Run", 0, reg.KEY_SET_VALUE)
            reg.DeleteValue(key, "EyeHealthReminder")
            reg.CloseKey(key)
            return True
        except FileNotFoundError:
            return True  # Already disabled
        except Exception as e:
            messagebox.showerror("Error", f"Failed to disable autostart: {e}")
            return False

    def quit_app(self):
        """Exit the application"""
        self.running = False
        self.root.quit()

    def run(self):
        """Start the application"""
        # Create a hidden system tray simulation
        def show_context_menu(event=None):
            try:
                menu = tk.Menu(self.root, tearoff=0)
                menu.add_command(label="⚙️ Settings", command=self.show_settings)
                menu.add_separator()
                pause_text = "▶️ Resume" if self.paused else "⏸️ Pause"
                menu.add_command(label=pause_text, command=self.toggle_pause)
                menu.add_command(label="❌ Exit", command=self.quit_app)
                
                # Show menu at cursor position or center of screen
                x = event.x_root if event else self.root.winfo_screenwidth() // 2
                y = event.y_root if event else self.root.winfo_screenheight() // 2
                menu.tk_popup(x, y)
            finally:
                menu.grab_release()
        
        # Bind right-click to show menu (for testing purposes)
        self.root.bind("<Button-3>", show_context_menu)
        
        # Create keyboard shortcut to show menu (Ctrl+Shift+E)
        def show_menu_shortcut(event=None):
            show_context_menu()
        
        self.root.bind_all("<Control-Shift-E>", show_menu_shortcut)
        
        # Run the application
        # For testing, show reminder after 10 seconds (uncomment next line for testing)
        self.root.after(10000, self.show_reminder)
        
        try:
            self.root.mainloop()
        except Exception as e:
            print(f"Error running application: {e}")

if __name__ == "__main__":
    import sys
    
    # Hide console window if running on Windows
    if sys.platform == "win32":
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    
    # Check if running in console mode or GUI mode
    console_mode = len(sys.argv) > 1 and sys.argv[1] == "--console"
    
    if console_mode:
        print("Starting Eye Health Reminder...")
        print("This tool will remind you to take eye breaks every 20 minutes.")
        print("Right-click the window for options or press Ctrl+C to exit.")
    
    try:
        app = EyeHealthReminder()
        app.run()
    except KeyboardInterrupt:
        if console_mode:
            print("\nExiting Eye Health Reminder...")
        sys.exit(0)
    except Exception as e:
        if console_mode:
            print(f"Error: {e}")
            input("Press Enter to exit...")
        else:
            # Show error dialog for GUI mode
            import tkinter.messagebox as mb
            mb.showerror("Error", f"Eye Health Reminder Error: {e}")
            
            
            
            
        
        
        # Computer\HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run
        # Add or remove the entry "EyeHealthReminder" with the command to run this script on startup
        # Example command: "C:\Path\To\python.exe" "C:\Path\To\eye_reminder.py"
        # Ensure paths
        ############################################################################