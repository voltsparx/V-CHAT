╔══════════════════════════════════════════════════════════════╗
║                   V-CHAT - Terminal Chat Application         ║
║                   Version 2.0                                ║
║                   By Voltsparx                               ║
╚══════════════════════════════════════════════════════════════╝

📌 DESCRIPTION:
V-CHAT is a secure, cross-platform terminal chat application with:
- Encrypted communications (future update)
- Customizable colors and notifications
- Private messaging and user mentions
- Sound notifications for messages
- Works on Windows, Linux, and macOS

🌟 FEATURES:
✔ Cross-platform terminal interface
✔ Custom username and message colors
✔ @mentions with sound notifications
✔ Private messages (/msg command)
✔ Online user list (/users command)
✔ Message timestamps
✔ Network auto-detection (LAN/WAN)
✔ Sound notifications (customizable)
✔ Lightweight and fast

⚙️ SYSTEM REQUIREMENTS:
- Python 3.6+
- Terminal with ANSI color support
- Basic sound playback capability

📥 INSTALLATION:
1. Ensure Python 3.6+ is installed
2. Install required packages:
   pip install colorama netifaces

3. Clone the repository:
   git clone https://github.com/voltsparx/V-CHAT.git
   cd V-CHAT

🚀 USAGE:

► SERVER MODE:
python vchat.py --server --username YOUR_NAME

► CLIENT MODE:
python vchat.py --host SERVER_IP --username YOUR_NAME

Optional arguments:
--port PORT_NUMBER (default: 65432)

🔧 CUSTOMIZATION:
When first run, you'll be prompted to:
1. Choose your username color
2. Choose your message arrow color
3. Select network type (for server)

🎮 COMMANDS:
/exit             - Disconnect from chat
/msg USER MESSAGE - Send private message
/notify [True/False] - Toggle notifications
/users            - List online users
@username         - Mention a user (plays sound)

🔒 SECURITY NOTES:
- Currently transmits in plaintext (encryption coming in v3.0)
- Only share server IP with trusted users
- Default port is 65432 (change with --port for security)

📁 FILE STRUCTURE:
vchat.py          - Main application
assets/sounds/    - Notification sound files
README.txt        - This file

📧 CONTACT:
Author: Voltsparx
Email: voltsparx@gmail.com
GitHub: https://github.com/voltsparx/V-CHAT

⚠️ DISCLAIMER:
This tool is for educational purposes only. The developer is not responsible 
for any misuse of this software.

🔄 CHANGELOG:
v2.0 - Complete rewrite with:
       - Better error handling
       - Timestamps on messages
       - User list command
       - Improved network detection
       - Simplified commands
v1.0 - Initial release
