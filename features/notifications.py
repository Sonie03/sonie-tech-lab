"""
Windows Toast Notification system for DevBuddy AI.
Uses PowerShell's BurntToast-compatible XML format via
the Windows.UI.Notifications WinRT API through comtypes/ctypes.
Falls back to a silent print if the Windows API is unavailable.
"""
import threading

def _send_toast_worker(title: str, message: str, icon_path: str = ""):
    """Runs the toast notification in a background thread."""
    try:
        # Use PowerShell as a cross-Python-version compatible method
        import subprocess
        # Escape quotes in title/message for PowerShell safety
        safe_title = title.replace("'", "''").replace('"', '`"')
        safe_message = message.replace("'", "''").replace('"', '`"')

        ps_script = f"""
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
[Windows.UI.Notifications.ToastNotification, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

$APP_ID = "DevBuddy.AI"
$template = @"
<toast>
    <visual>
        <binding template='ToastGeneric'>
            <text>{safe_title}</text>
            <text>{safe_message}</text>
        </binding>
    </visual>
</toast>
"@

$xml = New-Object Windows.Data.Xml.Dom.XmlDocument
$xml.LoadXml($template)
$toast = New-Object Windows.UI.Notifications.ToastNotification $xml
[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($APP_ID).Show($toast)
"""
        subprocess.Popen(
            ["powershell", "-NoProfile", "-NonInteractive", "-WindowStyle", "Hidden", "-Command", ps_script],
            creationflags=0x08000000  # CREATE_NO_WINDOW
        )
    except Exception as e:
        print(f"[Toast Notification] {title}: {message}  (Error: {e})")


def send_notification(title: str, message: str, icon_path: str = ""):
    """
    Sends a Windows 11 Toast Notification asynchronously.
    
    Args:
        title:      The notification title (bold).
        message:    The notification body text.
        icon_path:  Optional path to a PNG icon (currently unused, reserved).
    """
    t = threading.Thread(target=_send_toast_worker, args=(title, message, icon_path), daemon=True)
    t.start()
