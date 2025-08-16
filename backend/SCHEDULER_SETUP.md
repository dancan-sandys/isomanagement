# Scheduler Setup Guide

This document explains how to set up automated scheduled tasks for the ISO Management System.

## Overview

The system includes several scheduled tasks that should run automatically:

1. **Maintenance Tasks** (Daily at 08:00)
   - Document review reminders
   - Archive obsolete documents
   - Equipment maintenance/calibration alerts
   - Retention policy enforcement
   - Cleanup old notifications

2. **Audit Reminders** (Daily at 08:00)
   - Audit plan reminders (audits without approved plans)
   - Findings due reminders
   - Overdue findings escalations

3. **Email Notifications** (Optional)
   - High-priority notifications sent via email
   - Configured through environment variables

## Setup Options

### Option 1: Cron (Recommended for Linux/macOS)

Add these entries to your crontab (`crontab -e`):

```bash
# Daily at 08:00 - Run all scheduled tasks
0 8 * * * cd /path/to/iso/backend && source venv/bin/activate && python run_scheduled_tasks.py --task=all >> /var/log/iso-scheduler.log 2>&1

# Hourly - Run maintenance tasks only (for equipment alerts)
0 * * * * cd /path/to/iso/backend && source venv/bin/activate && python run_scheduled_tasks.py --task=maintenance >> /var/log/iso-scheduler.log 2>&1
```

### Option 2: Systemd Timers (Linux)

Create a systemd service file `/etc/systemd/system/iso-scheduler.service`:

```ini
[Unit]
Description=ISO Management System Scheduler
After=network.target

[Service]
Type=oneshot
User=iso-user
WorkingDirectory=/path/to/iso/backend
Environment=PATH=/path/to/iso/backend/venv/bin
ExecStart=/path/to/iso/backend/venv/bin/python run_scheduled_tasks.py --task=all

[Install]
WantedBy=multi-user.target
```

Create a timer file `/etc/systemd/system/iso-scheduler.timer`:

```ini
[Unit]
Description=Run ISO Scheduler daily at 08:00
Requires=iso-scheduler.service

[Timer]
OnCalendar=*-*-* 08:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

Enable and start:
```bash
sudo systemctl enable iso-scheduler.timer
sudo systemctl start iso-scheduler.timer
```

### Option 3: Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger to Daily at 08:00
4. Action: Start a program
5. Program: `C:\path\to\iso\backend\venv\Scripts\python.exe`
6. Arguments: `run_scheduled_tasks.py --task=all`

## Email Configuration

To enable email notifications, set these environment variables:

```bash
# Enable email notifications
EMAIL_ENABLED=true

# SMTP Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@your-domain.com
FROM_NAME=ISO Management System
```

### Gmail Setup

For Gmail, you'll need to:
1. Enable 2-factor authentication
2. Generate an App Password
3. Use the App Password as SMTP_PASSWORD

## Testing

Test the scheduler manually:

```bash
# Test all tasks
python run_scheduled_tasks.py --task=all --verbose

# Test maintenance only
python run_scheduled_tasks.py --task=maintenance --verbose

# Test audit reminders only
python run_scheduled_tasks.py --task=audit_reminders --verbose
```

## Monitoring

Check the logs to ensure tasks are running:

```bash
# View cron logs
tail -f /var/log/iso-scheduler.log

# Check systemd timer status
systemctl status iso-scheduler.timer

# List recent timer runs
journalctl -u iso-scheduler.service --since "1 hour ago"
```

## Troubleshooting

### Common Issues

1. **Permission denied**: Ensure the user running cron has access to the backend directory
2. **Python path issues**: Use absolute paths in cron commands
3. **Database connection**: Ensure the database is accessible from the cron environment
4. **Email not sending**: Check SMTP configuration and firewall settings

### Debug Mode

Run with verbose logging to see detailed output:

```bash
python run_scheduled_tasks.py --task=all --verbose
```

## Security Considerations

1. **File permissions**: Ensure the scheduler script and logs are not world-readable
2. **Database credentials**: Use environment variables for database connection
3. **Email credentials**: Store SMTP passwords securely
4. **Log rotation**: Implement log rotation to prevent disk space issues

## Performance

- Tasks typically complete within 30-60 seconds
- Monitor database performance during task execution
- Consider running during off-peak hours
- Implement task queuing for high-volume environments
