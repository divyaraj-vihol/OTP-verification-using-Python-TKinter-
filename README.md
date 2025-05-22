# SecureVerify - Advanced OTP Verification System

A robust, feature-rich OTP (One-Time Password) verification system built with Python and Tkinter.

![SecureVerify Interface](https://github.com/yourusername/secureverify/raw/main/screenshots/otp_verification.png)

## Features

- **Email-based OTP delivery**: Send verification codes securely via email
- **Configurable OTP complexity**: Choose between numeric or alphanumeric OTPs with customizable length (4, 6, or 8 characters)
- **Real-time OTP expiration**: Visual countdown timer showing remaining OTP validity
- **Enhanced security features**: Limited verification attempts, detailed security feedback
- **Verification history**: Track all verification attempts with dates, times, and status
- **Customizable themes**: Choose between light and dark interface modes
- **Email validation**: Real-time validation of email format
- **Interactive UI elements**: Individual digit entry boxes with auto-focus navigation
- **Custom messaging**: Personalize the OTP email message

## Requirements

- Python 3.6+
- Tkinter (usually included with Python installation)
- Internet connection (for sending emails)

## Installation
git clone https://github.com/divyaraj-vihol/OTP-verification-using-Python-TKinter-.git
cd OTP-verification-using-Python-TKinter-

2. Install dependencies (if not already installed):
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python secureverify.py
   ```

## Usage

1. **Email Configuration**:
   - Before using the application, update the email sender credentials in the code:
   ```python
   self.email_sender = "your_email@gmail.com"
   self.email_password = "your_app_password"
   ```
   Note: For Gmail, you'll need to use an App Password if you have 2FA enabled.

2. **Sending OTP**:
   - Enter the recipient's email address
   - Customize the OTP type and length if desired
   - Optionally customize the email message
   - Click "Send OTP"

3. **Verifying OTP**:
   - Ask the recipient to check their email
   - Enter the received OTP code in the individual digit boxes
   - Click "Verify OTP"

4. **Verification History**:
   - Switch to the History tab to view all verification attempts
   - Clear history if needed

## Security Features

- OTP expiration after 5 minutes
- Limited verification attempts (3 by default)
- Detailed feedback on incorrect attempts
- Verification history tracking
- Email format validation

## Customization

The application offers several customization options:

- **OTP Type**: Choose between numeric digits only or alphanumeric characters
- **OTP Length**: Select from 4, 6, or 8 character lengths
- **Email Message**: Customize the text sent with the OTP (use {otp} as a placeholder)
- **Theme**: Toggle between light and dark interface themes

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.


## Disclaimer

This application is provided for educational purposes. When using in production:
1. Implement additional security measures
2. Secure email credentials properly
3. Consider using a dedicated email service API instead of SMTP
4. Add proper error handling and logging
