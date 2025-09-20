import tkinter as tk
import time
import threading
import ctypes

class SimpleEyeHealthReminder:
    def __init__(self):
        # Twilio configuration
        self.account_sid = 'AC50ea1edcf290a18a3e33804f0944300a'
        self.auth_token = 'bdaba9debb5f48c9f05146ef38daa48a'
        self.twilio_number = '+12272305923'
        self.recipient_numbers = ['############']  # enter the phone numbers
        
        # Reminder settings
        self.reminder_interval = 2 * 60  # 2 minutes for testing (change to 20*60 for production)
        self.running = True
        
        print("🔔 Eye Health Reminder started with SMS notifications!")
        print("✓ Using HTTP method for SMS (bypassing Twilio SDK issues)")
        print(f"Notifications will appear every {self.reminder_interval//60} minutes.")
        print("Press Ctrl+C to stop the program.")
        
        # Start reminder loop
        self.start_reminder_loop()

    def start_reminder_loop(self):
        """Start the main reminder loop in a separate thread"""
        reminder_thread = threading.Thread(target=self.reminder_loop, daemon=True)
        reminder_thread.start()
        
        # Keep the main thread alive
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping Eye Health Reminder...")
            self.running = False

    def reminder_loop(self):
        """Main loop that shows reminders every interval"""
        while self.running:
            time.sleep(self.reminder_interval)
            if self.running:
                print(f"\n📅 {time.strftime('%H:%M:%S')} - Showing reminder...")
                self.show_notification()
                self.send_sms_notifications()

    def show_notification(self):
        """Show eye health reminder notification on screen"""
        try:
            # Create a simple notification window
            root = tk.Tk()
            root.title("👁️ Eye Health Reminder")
            root.geometry("400x300")
            root.configure(bg='#e8f4fd')
            root.attributes('-topmost', True)
            root.resizable(False, False)
            
            # Center the window
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()
            x = (screen_width - 400) // 2
            y = (screen_height - 300) // 2
            root.geometry(f"400x300+{x}+{y}")
            
            # Main container
            container = tk.Frame(root, bg='#e8f4fd', padx=30, pady=30)
            container.pack(fill='both', expand=True)
            
            # Title
            title_label = tk.Label(container, text="👁️ Eye Break Time!", 
                                  font=('Arial', 18, 'bold'), 
                                  bg='#e8f4fd', fg='#2c5282')
            title_label.pack(pady=(0, 20))
            
            # Message
            message_text = """It's been 20 minutes of screen time!

Follow the 20-20-20 Rule:
• Look at something 20 feet away
• For at least 20 seconds
• Every 20 minutes

This helps reduce eye strain and keeps your eyes healthy."""
            
            message_label = tk.Label(container, text=message_text, 
                                    font=('Arial', 11), 
                                    bg='#e8f4fd', fg='#1a202c',
                                    justify='left')
            message_label.pack(pady=(0, 20))
            
            # Close button
            close_button = tk.Button(container, text="✓ Got it!", 
                                    command=root.destroy,
                                    font=('Arial', 12, 'bold'),
                                    bg='#48bb78', fg='white',
                                    padx=20, pady=10,
                                    relief='flat', cursor='hand2')
            close_button.pack()
            
            # Auto-close after 15 seconds
            root.after(15000, root.destroy)
            
            # Play notification sound
            try:
                ctypes.windll.user32.MessageBeep(0x40)
            except:
                pass
            
            print("✓ Desktop notification shown")
            
            # Show the window
            root.mainloop()
            
        except Exception as e:
            print(f"❌ Error showing notification: {e}")

    def send_sms_notifications(self):
        """Send SMS notifications using HTTP method"""
        print(f"📱 Sending SMS to {len(self.recipient_numbers)} numbers...")
        
        for i, number in enumerate(self.recipient_numbers, 1):
            self.send_single_sms(number, i, len(self.recipient_numbers))

    def send_single_sms(self, phone_number, current, total):
        """Send a single SMS using Twilio's HTTP API"""
        try:
            print(f"   📤 Sending SMS {current}/{total} to {phone_number}...")
            
            # Try to import requests, install if needed
            try:
                import requests
            except ImportError:
                print(f"   📦 Installing requests library...")
                import subprocess
                import sys
                subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
                import requests
                print(f"   ✓ requests library installed")
            
            import base64
            
            # Message content
            message_body = ("🔔 Eye Health Reminder: It's been 20 minutes of screen time! "
                          "Please look at something 20 feet away for 20 seconds. "
                          "Take care of your eyes! 👁️ Don't forget to drink some water")
            
            # Twilio API endpoint
            api_url = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}/Messages.json"
            
            # Create authentication header
            credentials = f"{self.account_sid}:{self.auth_token}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            # Request headers
            headers = {
                'Authorization': f'Basic {encoded_credentials}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            # Request data
            payload = {
                'From': self.twilio_number,
                'To': phone_number,
                'Body': message_body
            }
            
            # Send the SMS
            response = requests.post(api_url, headers=headers, data=payload, timeout=30)
            
            # Check response
            if response.status_code == 201:
                # Success!
                result = response.json()
                print(f"   ✅ SMS sent successfully to {phone_number}")
                print(f"      Message SID: {result.get('sid', 'N/A')}")
                print(f"      Status: {result.get('status', 'queued')}")
                return True
            else:
                # Error
                print(f"   ❌ SMS failed for {phone_number}")
                print(f"      HTTP Status: {response.status_code}")
                
                # Try to get error details
                try:
                    error_info = response.json()
                    error_code = error_info.get('code', 'Unknown')
                    error_message = error_info.get('message', 'Unknown error')
                    print(f"      Error Code: {error_code}")
                    print(f"      Error Message: {error_message}")
                    
                    # Provide helpful explanations
                    if error_code == 21211:
                        print(f"      → Invalid phone number format")
                    elif error_code == 21614:
                        print(f"      → Not a mobile number or invalid format")
                    elif error_code == 20003:
                        print(f"      → Authentication failed - check Account SID/Auth Token")
                    elif error_code == 21408:
                        print(f"      → Permission to send to this region may not be enabled")
                    elif error_code == 21610:
                        print(f"      → Message blocked - number may have opted out")
                        
                except:
                    print(f"      Raw response: {response.text}")
                
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Network error sending to {phone_number}: {e}")
            return False
        except Exception as e:
            print(f"   ❌ Unexpected error sending to {phone_number}: {e}")
            return False

    def send_test_sms_now(self):
        """Send test SMS immediately"""
        print("\n🧪 Sending test SMS now...")
        self.send_sms_notifications()

if __name__ == "__main__":
    try:
        app = SimpleEyeHealthReminder()
    except Exception as e:
        print(f"Error starting application: {e}")
        input("Press Enter to exit...")
