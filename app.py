import tkinter as tk
from tkinter import messagebox, ttk
import smtplib
import random
import string
import time
import threading
import os
import json
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import hashlib
import re

class OTPVerificationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced OTP Verification System")
        self.root.geometry("600x600")
        self.root.resizable(0, 0)
        
        # Set theme colors
        self.bg_color = "#f5f5f5"
        self.primary_color = "#2962ff"
        self.success_color = "#00c853"
        self.error_color = "#d50000"
        self.warning_color = "#ff6d00"
        
        self.root.configure(bg=self.bg_color)
        
        # Generate a random OTP
        self.otp = self.generate_otp()
        self.email_sent = False
        self.attempt_count = 0
        self.max_attempts = 3
        self.otp_expiry_time = None
        self.countdown_thread = None
        self.countdown_running = False
        self.user_data_file = "user_verification_history.json"
        self.user_data = self.load_user_data()
        
        # Email configuration
        self.email_sender = "viholdivyaraj7@gmail.com"  # Your Gmail address
        self.email_password = "dkopdyntyqnmzkdy"   # Your Gmail app password
        
        # Create UI elements
        self.create_widgets()
        
        # Theme selection
        self.current_theme = "Light"
        self.apply_theme()
        
    def generate_otp(self, length=6, alphanumeric=False):
        """Generate OTP with customizable complexity"""
        if alphanumeric:
            # Generate alphanumeric OTP
            characters = string.ascii_uppercase + string.digits
            return ''.join(random.choice(characters) for _ in range(length))
        else:
            # Generate numeric OTP
            return str(random.randint(10**(length-1), 10**length - 1))
            
    def load_user_data(self):
        """Load user verification history"""
        if os.path.exists(self.user_data_file):
            try:
                with open(self.user_data_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
        
    def save_user_data(self):
        """Save user verification history"""
        with open(self.user_data_file, 'w') as f:
            json.dump(self.user_data, f)
    
    def create_widgets(self):
        # Main container
        self.main_frame = tk.Frame(self.root, bg=self.bg_color)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        header_frame.pack(fill="x", pady=10)
        
        # App logo/title
        tk.Label(header_frame, text="SecureVerify", font=("Arial", 24, "bold"), 
                 bg=self.bg_color, fg=self.primary_color).pack()
        tk.Label(header_frame, text="Advanced OTP Verification System", 
                 font=("Arial", 12), bg=self.bg_color).pack()
        
        # Settings/Options Menu
        options_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        options_frame.pack(fill="x", pady=10)
        
        # Theme Toggle
        self.theme_btn = tk.Button(options_frame, text="Dark Theme", 
                               command=self.toggle_theme, bg="#e0e0e0", width=12)
        self.theme_btn.pack(side="left", padx=5)
        
        # OTP Complexity
        tk.Label(options_frame, text="OTP Type:", bg=self.bg_color).pack(side="left", padx=5)
        self.otp_type = tk.StringVar(value="Numeric")
        ttk.Combobox(options_frame, textvariable=self.otp_type, 
                    values=["Numeric", "Alphanumeric"], width=12, state="readonly").pack(side="left", padx=5)
        
        tk.Label(options_frame, text="Length:", bg=self.bg_color).pack(side="left", padx=5)
        self.otp_length = tk.StringVar(value="6")
        ttk.Combobox(options_frame, textvariable=self.otp_length, 
                    values=["4", "6", "8"], width=5, state="readonly").pack(side="left", padx=5)
        
        # Notebook for different verification methods
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill="both", expand=True, pady=10)
        
        # Email Verification Tab
        self.email_tab = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(self.email_tab, text="Email Verification")
        
        # History Tab
        self.history_tab = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(self.history_tab, text="Verification History")
        
        # Create tab contents
        self.create_email_tab()
        self.create_history_tab()
        
        # Status bar
        self.status_frame = tk.Frame(self.main_frame, bg="#e0e0e0", height=25)
        self.status_frame.pack(fill="x", side="bottom", pady=10)
        
        self.status_label = tk.Label(self.status_frame, text="Ready", bg="#e0e0e0", anchor="w", padx=10)
        self.status_label.pack(fill="x", side="left")
        
        self.countdown_label = tk.Label(self.status_frame, text="", bg="#e0e0e0", anchor="e", padx=10)
        self.countdown_label.pack(fill="x", side="right")
    
    def create_email_tab(self):
        # Email Frame
        email_frame = tk.Frame(self.email_tab, bg=self.bg_color)
        email_frame.pack(pady=20, fill="x", padx=20)
        
        # Email Entry with validation
        tk.Label(email_frame, text="Recipient Email:", font=("Arial", 12), bg=self.bg_color).pack(anchor="w")
        
        email_validation_frame = tk.Frame(email_frame, bg=self.bg_color)
        email_validation_frame.pack(fill="x", pady=5)
        
        self.email_entry = tk.Entry(email_validation_frame, width=40, font=("Arial", 12))
        self.email_entry.pack(side="left", fill="x", expand=True)
        
        self.email_validation_label = tk.Label(email_validation_frame, text="", bg=self.bg_color)
        self.email_validation_label.pack(side="left", padx=5)
        
        # Email validation on typing
        self.email_entry.bind("<KeyRelease>", self.validate_email)
        
        # Message customization
        tk.Label(email_frame, text="Customize Message (Optional):", font=("Arial", 12), bg=self.bg_color).pack(anchor="w", pady=(10, 5))
        
        self.message_text = tk.Text(email_frame, width=40, height=4, font=("Arial", 11))
        self.message_text.insert("1.0", "Your OTP verification code is: {otp}\nValid for 5 minutes.")
        self.message_text.pack(fill="x", pady=5)
        
        # Send OTP button
        button_frame = tk.Frame(email_frame, bg=self.bg_color)
        button_frame.pack(fill="x", pady=10)
        
        self.send_otp_button = tk.Button(button_frame, text="Send OTP", font=("Arial", 12), 
                                    command=self.send_otp, bg=self.primary_color, fg="white",
                                    width=15, height=1)
        self.send_otp_button.pack(side="left", pady=10)
        
        self.regenerate_button = tk.Button(button_frame, text="Regenerate OTP", font=("Arial", 12), 
                                    command=self.regenerate_otp, state="disabled", width=15)
        self.regenerate_button.pack(side="left", pady=10, padx=10)
        
        # OTP Verification Frame
        self.otp_frame = tk.Frame(self.email_tab, bg=self.bg_color)
        self.otp_frame.pack(pady=20, fill="x", padx=20)
        
        tk.Label(self.otp_frame, text="Enter OTP:", font=("Arial", 12), bg=self.bg_color).pack(anchor="w")
        
        # OTP entry with individual digit boxes
        otp_digits_frame = tk.Frame(self.otp_frame, bg=self.bg_color)
        otp_digits_frame.pack(fill="x", pady=10)
        
        self.otp_entries = []
        for i in range(6):  # Default to 6 digits
            digit_entry = tk.Entry(otp_digits_frame, width=2, font=("Arial", 16), justify='center')
            digit_entry.grid(row=0, column=i, padx=5)
            # Auto-move to next entry
            digit_entry.bind('<KeyRelease>', lambda e, idx=i: self.move_to_next_entry(e, idx))
            self.otp_entries.append(digit_entry)
        
        # Verify Button
        self.verify_button = tk.Button(self.otp_frame, text="Verify OTP", font=("Arial", 12), 
                                   command=self.verify_otp, bg=self.primary_color, fg="white", 
                                   width=15, state="disabled")
        self.verify_button.pack(pady=10)
        
        # Attempts and countdown info
        self.attempts_label = tk.Label(self.otp_frame, text=f"Attempts: 0/{self.max_attempts}", 
                                  font=("Arial", 10), bg=self.bg_color)
        self.attempts_label.pack(pady=5)
    
    def create_history_tab(self):
        # History Frame
        history_frame = tk.Frame(self.history_tab, bg=self.bg_color)
        history_frame.pack(pady=20, fill="both", expand=True, padx=20)
        
        tk.Label(history_frame, text="Verification History", font=("Arial", 14, "bold"), 
                 bg=self.bg_color).pack(pady=(0, 10))
        
        # History Treeview
        columns = ("Email", "Date", "Time", "Status")
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=10)
        
        # Set column headings
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=100)
        
        self.history_tree.pack(fill="both", expand=True, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.history_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        # Clear History Button
        self.clear_history_button = tk.Button(history_frame, text="Clear History", 
                                         command=self.clear_history, bg="#e0e0e0", width=15)
        self.clear_history_button.pack(pady=10, anchor="e")
        
        # Load history
        self.update_history_display()
    
    def validate_email(self, event=None):
        """Validate email format on input"""
        email = self.email_entry.get()
        # Simple email validation pattern
        pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        
        if email and not re.match(pattern, email):
            self.email_validation_label.config(text="✗", fg=self.error_color)
            return False
        elif email:
            self.email_validation_label.config(text="✓", fg=self.success_color)
            return True
        else:
            self.email_validation_label.config(text="")
            return False
    
    def move_to_next_entry(self, event, idx):
        """Auto-move to next OTP digit box"""
        if event.char.isdigit() and idx < len(self.otp_entries) - 1:
            self.otp_entries[idx + 1].focus()
    
    def send_otp(self):
        recipient_email = self.email_entry.get()
        
        if not self.validate_email():
            messagebox.showerror("Error", "Please enter a valid email address")
            return
        
        # Update OTP type and length based on selections
        length = int(self.otp_length.get())
        alphanumeric = (self.otp_type.get() == "Alphanumeric")
        self.otp = self.generate_otp(length, alphanumeric)
        
        # Adjust OTP entry fields if needed
        self.adjust_otp_entries(length)
        
        try:
            # Get custom message or use default
            message_template = self.message_text.get("1.0", "end").strip()
            if not message_template:
                message_template = "Your OTP verification code is: {otp}\nValid for 5 minutes."
            
            body = message_template.format(otp=self.otp)
            
            # Setup email content
            msg = MIMEMultipart()
            msg['From'] = self.email_sender
            msg['To'] = recipient_email
            msg['Subject'] = "Your Secure Verification Code"
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Connect to Gmail SMTP server
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            
            # Login with your Gmail account
            server.login(self.email_sender, self.email_password)
            
            # Send email
            text = msg.as_string()
            server.sendmail(self.email_sender, recipient_email, text)
            server.quit()
            
            self.email_sent = True
            self.status_label.config(text=f"OTP sent to {recipient_email}")
            
            # Enable verification UI
            self.verify_button.config(state="normal")
            self.regenerate_button.config(state="normal")
            
            # Set OTP expiry
            self.otp_expiry_time = datetime.now() + timedelta(minutes=5)
            
            # Start countdown
            if self.countdown_thread is not None and self.countdown_running:
                self.countdown_running = False
                self.countdown_thread.join()
            
            self.countdown_running = True
            self.countdown_thread = threading.Thread(target=self.countdown_timer)
            self.countdown_thread.daemon = True
            self.countdown_thread.start()
            
            # Store in history
            if recipient_email not in self.user_data:
                self.user_data[recipient_email] = []
            
            self.user_data[recipient_email].append({
                "date": datetime.now().strftime("%Y-%m-%d"),
                "time": datetime.now().strftime("%H:%M:%S"),
                "status": "OTP Sent",
                "otp_type": self.otp_type.get(),
                "ip_address": "Local"  # In a real application, you'd get the actual IP
            })
            
            self.save_user_data()
            self.update_history_display()
            
        except Exception as e:
            self.status_label.config(text="Failed to send OTP")
            messagebox.showerror("Error", f"Failed to send email: {str(e)}")
    
    def adjust_otp_entries(self, length):
        """Adjust the number of OTP entry fields based on selected length"""
        # Clear existing entries
        for entry in self.otp_entries:
            entry.grid_forget()
        
        # Create new entries if needed
        if len(self.otp_entries) < length:
            for i in range(len(self.otp_entries), length):
                digit_entry = tk.Entry(self.otp_entries[0].master, width=2, font=("Arial", 16), justify='center')
                digit_entry.bind('<KeyRelease>', lambda e, idx=i: self.move_to_next_entry(e, idx))
                self.otp_entries.append(digit_entry)
        
        # Show only the required number of entries
        for i in range(length):
            self.otp_entries[i].delete(0, 'end')
            self.otp_entries[i].grid(row=0, column=i, padx=5)
    
    def regenerate_otp(self):
        """Regenerate a new OTP"""
        length = int(self.otp_length.get())
        alphanumeric = self.otp_type.get() == "Alphanumeric"
        self.otp = self.generate_otp(length, alphanumeric)
        
        # Adjust OTP entry fields
        self.adjust_otp_entries(length)
        
        # Reset attempt count
        self.attempt_count = 0
        self.attempts_label.config(text=f"Attempts: {self.attempt_count}/{self.max_attempts}")
        
        # Update expiry time
        self.otp_expiry_time = datetime.now() + timedelta(minutes=5)
        
        messagebox.showinfo("OTP Regenerated", "A new OTP has been generated.\nPlease notify the recipient to ignore previous OTP.")
        self.status_label.config(text="New OTP generated. Send to recipient.")
    
    def verify_otp(self):
        """Verify the entered OTP with detailed feedback"""
        if not self.email_sent:
            messagebox.showerror("Error", "Please send OTP first")
            return
        
        # Check if OTP has expired
        if datetime.now() > self.otp_expiry_time:
            messagebox.showerror("Error", "OTP has expired. Please regenerate.")
            self.countdown_label.config(text="OTP expired")
            self.verify_button.config(state="disabled")
            return
        
        # Get entered OTP from separate boxes
        entered_otp = ''
        for entry in self.otp_entries[:len(self.otp)]:
            entered_otp += entry.get()
        
        # Validate the entered OTP format
        if not entered_otp:
            messagebox.showerror("Error", "Please enter the OTP code")
            return
            
        if len(entered_otp) != len(self.otp):
            messagebox.showerror("Error", f"OTP should be {len(self.otp)} characters long")
            return
            
        # Check if OTP contains invalid characters based on type
        if self.otp_type.get() == "Numeric" and not entered_otp.isdigit():
            messagebox.showerror("Error", "Numeric OTP should contain only digits")
            return
            
        self.attempt_count += 1
        self.attempts_label.config(text=f"Attempts: {self.attempt_count}/{self.max_attempts}")
        
        if entered_otp == self.otp:
            # Success - OTP matches
            self.status_label.config(text="OTP Verified Successfully!")
            
            # Add to history
            self.add_to_history(self.email_entry.get(), "Verified")
            
            # Show success animation
            self.show_verification_result(True)
            
            # Disable further attempts after successful verification
            self.verify_button.config(state="disabled")
            self.regenerate_button.config(state="disabled")
            
        else:
            # Failed attempt - provide detailed feedback
            feedback = self.get_otp_feedback(entered_otp)
            
            if self.attempt_count >= self.max_attempts:
                message = f"Maximum attempts reached.\n{feedback}\nPlease regenerate OTP."
                messagebox.showerror("Error", message)
                self.verify_button.config(state="disabled")
                self.add_to_history(self.email_entry.get(), "Failed (Max attempts)")
            else:
                remaining = self.max_attempts - self.attempt_count
                message = f"Invalid OTP ({remaining} attempts remaining).\n{feedback}"
                messagebox.showerror("Error", message)
                self.add_to_history(self.email_entry.get(), "Failed")
                
            # Show failure animation
            self.show_verification_result(False)
            
            # Clear OTP fields for next attempt
            for entry in self.otp_entries:
                entry.delete(0, 'end')
            self.otp_entries[0].focus()

    def get_otp_feedback(self, entered_otp):
        """Provide detailed feedback about what's wrong with the entered OTP"""
        feedback = []
        
        # Check length
        if len(entered_otp) != len(self.otp):
            feedback.append(f"Length should be {len(self.otp)} characters")
        
        # Check character types
        if self.otp_type.get() == "Numeric" and not entered_otp.isdigit():
            feedback.append("Should contain only digits")
        elif self.otp_type.get() == "Alphanumeric":
            for char in entered_otp:
                if char not in string.ascii_uppercase + string.digits:
                    feedback.append("Should contain only letters and digits")
                    break
        
        # Check for correct digits in correct positions
        correct_positions = 0
        for i in range(min(len(entered_otp), len(self.otp))):
            if entered_otp[i] == self.otp[i]:
                correct_positions += 1
        
        if correct_positions > 0:
            feedback.append(f"{correct_positions} correct character(s) in right position")
        
        # Format the feedback
        if not feedback:
            return "The OTP is completely incorrect."
        
        return "Details:\n- " + "\n- ".join(feedback)

    def add_to_history(self, email, status):
        """Add verification attempt to history"""
        if email not in self.user_data:
            self.user_data[email] = []
        
        self.user_data[email].append({
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M:%S"),
            "status": status,
            "otp_type": self.otp_type.get(),
            "ip_address": "Local"
        })
        
        self.save_user_data()
        self.update_history_display()
    
    def update_history_display(self):
        """Update the history treeview with current data"""
        # Clear existing items
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Add history items
        for email, records in self.user_data.items():
            for record in records:
                self.history_tree.insert("", "end", values=(
                    email,
                    record["date"],
                    record["time"],
                    record["status"]
                ))
    
    def clear_history(self):
        """Clear verification history"""
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to clear all history?")
        if confirm:
            self.user_data = {}
            self.save_user_data()
            self.update_history_display()
            self.status_label.config(text="History cleared")
    
    def countdown_timer(self):
        """Display countdown until OTP expires"""
        while self.countdown_running and datetime.now() < self.otp_expiry_time:
            remaining = self.otp_expiry_time - datetime.now()
            mins, secs = divmod(remaining.seconds, 60)
            timeformat = f"OTP expires in: {mins:02d}:{secs:02d}"
            
            # Update label using the main thread
            self.root.after(0, lambda t=timeformat: self.countdown_label.config(text=t))
            time.sleep(1)
        
        if self.countdown_running:
            # OTP expired
            self.root.after(0, lambda: self.countdown_label.config(text="OTP expired"))
            self.root.after(0, lambda: self.verify_button.config(state="disabled"))
        
        self.countdown_running = False
    
    def show_verification_result(self, success):
        """Show animation for verification result"""
        result_window = tk.Toplevel(self.root)
        result_window.geometry("300x200")
        result_window.title("Verification Result")
        
        if success:
            result_window.configure(bg=self.success_color)
            label = tk.Label(result_window, text="✓", font=("Arial", 80), bg=self.success_color, fg="white")
            label.pack(pady=20)
            tk.Label(result_window, text="Verification Successful", font=("Arial", 14), 
                  bg=self.success_color, fg="white").pack()
        else:
            result_window.configure(bg=self.error_color)
            label = tk.Label(result_window, text="✗", font=("Arial", 80), bg=self.error_color, fg="white")
            label.pack(pady=20)
            tk.Label(result_window, text="Verification Failed", font=("Arial", 14), 
                  bg=self.error_color, fg="white").pack()
        
        # Auto close after 2 seconds
        result_window.after(2000, result_window.destroy)
    
    def toggle_theme(self):
        """Toggle between light and dark theme"""
        if self.current_theme == "Light":
            self.current_theme = "Dark"
            self.theme_btn.config(text="Light Theme")
        else:
            self.current_theme = "Light"
            self.theme_btn.config(text="Dark Theme")
        
        self.apply_theme()
    
    def apply_theme(self):
        """Apply the selected theme"""
        if self.current_theme == "Light":
            self.bg_color = "#f5f5f5"
            self.primary_color = "#2962ff"
            self.success_color = "#00c853"
            self.error_color = "#d50000"
            self.warning_color = "#ff6d00"
        else:
            self.bg_color = "#212121"
            self.primary_color = "#1e88e5"
            self.success_color = "#00c853"
            self.error_color = "#d50000"
            self.warning_color = "#ff6d00"
        
        # Update UI colors
        self.root.configure(bg=self.bg_color)
        self.main_frame.configure(bg=self.bg_color)
        
        # Update all frames and labels
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.configure(bg=self.bg_color)
            
            for child in widget.winfo_children():
                if isinstance(child, tk.Label) or isinstance(child, tk.Frame):
                    if child != self.status_label and child != self.countdown_label:
                        child.configure(bg=self.bg_color)
                
                # Text color for labels
                if isinstance(child, tk.Label) and self.current_theme == "Dark":
                    child.configure(fg="#e0e0e0")
                elif isinstance(child, tk.Label):
                    child.configure(fg="#212121")
        
        # Update buttons
        self.send_otp_button.configure(bg=self.primary_color)
        self.verify_button.configure(bg=self.primary_color)
        
        # Status bar (keep it distinguishable)
        status_bg = "#e0e0e0" if self.current_theme == "Light" else "#424242"
        status_fg = "#212121" if self.current_theme == "Light" else "#e0e0e0"
        self.status_frame.configure(bg=status_bg)
        self.status_label.configure(bg=status_bg, fg=status_fg)
        self.countdown_label.configure(bg=status_bg, fg=status_fg)


if __name__ == "__main__":
    # Create and run the app
    root = tk.Tk()
    app = OTPVerificationApp(root)
    root.mainloop()






                 