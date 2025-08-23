# Email Setup Instructions for Testing

## To test email functionality, you need to configure SMTP credentials:

### 1. Create a `.env` file in the backend directory with the following content:

```bash
# Email Configuration
EMAIL_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@iso-system.com
FROM_NAME=ISO 22000 FSMS

# Email Notification Settings
EMAIL_PRIORITY_THRESHOLD=MEDIUM
ENABLE_EMAIL_NOTIFICATIONS=true
ENABLE_SMS_NOTIFICATIONS=false
```

### 2. Gmail Setup (Recommended):

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate App Password**:
   - Go to Google Account Settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
3. **Replace in .env file**:
   - `SMTP_USERNAME=your-actual-gmail@gmail.com`
   - `SMTP_PASSWORD=your-16-character-app-password`

### 3. Test the email functionality:

```bash
cd backend
python simple_email_test.py
```

### 4. Alternative: Set environment variables directly:

```bash
# Windows PowerShell
$env:SMTP_USERNAME="your-email@gmail.com"
$env:SMTP_PASSWORD="your-app-password"
python simple_email_test.py

# Or on Linux/Mac
export SMTP_USERNAME="your-email@gmail.com"
export SMTP_PASSWORD="your-app-password"
python simple_email_test.py
```

### 5. Expected Result:

If configured correctly, you should see:
```
✅ Email sent successfully!
📧 Email delivered to: okoraok18@gmail.com
🎉 Email test PASSED! Check your inbox at okoraok18@gmail.com
```

### 6. Troubleshooting:

- **Authentication Error**: Check your username and app password
- **Connection Error**: Check your internet connection and firewall
- **Gmail Issues**: Make sure you're using an App Password, not your regular password

### 7. Security Note:

- Never commit your `.env` file to version control
- Use App Passwords instead of regular passwords
- Keep your credentials secure
