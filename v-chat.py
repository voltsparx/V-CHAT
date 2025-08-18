import socket
import threading
import argparse
import re
import os
import platform
import netifaces
from datetime import datetime
from colorama import Fore, Back, Style, init

# Configure sound file paths
SOUND_DIR = os.path.join("assets", "sounds")
NOTIFY_SOUND = os.path.join(SOUND_DIR, "notify.mp3")
MENTION_SOUND = os.path.join(SOUND_DIR, "mention.wav")

# ANSI Color Setup
COLORS = {
    'red': '\033[91m', 'orange': '\033[38;5;208m', 'purple': '\033[95m',
    'green': '\033[92m', 'blue': '\033[94m', 'light-blue': '\033[96m',
    'light-green': '\033[38;5;120m', 'yellow': '\033[93m',
    'pink': '\033[38;5;205m', 'light-pink': '\033[38;5;219m',
    'brown': '\033[38;5;130m', 'reset': '\033[0m'
}

def clear_screen():
    """Clears the terminal screen cross-platform."""
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')
# Clear screen at first
clear_screen()

# Initialize colorama with settings for all OSes
init(autoreset=True)  # Auto-reset colors after each print

def print_orange(text):
    """Prints text in orange (bright yellow) on all platforms."""
    if platform.system() == "Windows":
        # Windows: Use bright yellow (closest to orange)
        print(Fore.YELLOW + Style.BRIGHT + text)
    else:
        # macOS/Linux: Use ANSI color code for orange (ESC[38;5;214m)
        print("\033[38;5;214m" + text + "\033[0m")

print_orange("█▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀█")
print_orange("█  ██╗   ██╗         ██████╗██╗  ██╗ █████╗ ████████╗  █")
print_orange("█  ╚██╗ ██╔╝        ██╔════╝██║  ██║██╔══██╗╚══██╔══╝  █")
print_orange("█   ╚█  █╔╝ █████╗  ██║     ███████║███████║   ██║     █")
print_orange("█    ╚██╔╝  ╚════╝  ██║     ██╔══██║██╔══██║   ██║     █")
print_orange("█     ██║           ╚██████╗██║  ██║██║  ██║   ██║     █")
print_orange("█     ╚═╝            ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝     █")
print_orange("█▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄█")
print_orange("║► BY: Voltsparx                         VERSION: 1.0 ◄║")
print_orange("║► Contact: voltsparx@gmail.com                       ◄║")
print_orange("║► Repo: https://github.com/voltsparx/V-CHAT          ◄║")
print_orange("▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀")


def get_network_info(network_type):
    """Get IP address based on selected network type"""
    try:
        if network_type == "internet":
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        
        elif network_type in ["wifi", "ethernet"]:
            interfaces = netifaces.interfaces()
            for interface in interfaces:
                if (network_type == "wifi" and ("wl" in interface or "en0" in interface)) or \
                   (network_type == "ethernet" and ("eth" in interface or "en1" in interface)):
                    addrs = netifaces.ifaddresses(interface)
                    if netifaces.AF_INET in addrs:
                        return addrs[netifaces.AF_INET][0]['addr']
    except:
        pass
    return "127.0.0.1"

def choose_network():
    """Network type selection menu"""
    print(f"\n{COLORS['blue']}Select Network Type:{COLORS['reset']}")
    print(f"1. {COLORS['green']}Internet (Public IP){COLORS['reset']}")
    print(f"2. {COLORS['blue']}WiFi (Local Network){COLORS['reset']}")
    print(f"3. {COLORS['purple']}Ethernet (Local Network){COLORS['reset']}")
    
    while True:
        choice = input("Choose (1-3): ")
        if choice == "1": return "internet"
        elif choice == "2": return "wifi"
        elif choice == "3": return "ethernet"
        print(f"{COLORS['red']}Invalid choice. Try again.{COLORS['reset']}")

def choose_color(prompt):
    """Color selection menu"""
    print("\nAvailable colors:")
    for i, color in enumerate(COLORS.keys(), 1):
        if color != 'reset':
            print(f"{i}. {COLORS[color]}{color}{COLORS['reset']}")
    
    while True:
        try:
            choice = int(input(f"{prompt} (1-{len(COLORS)-1}): ")) - 1
            if 0 <= choice < len(COLORS)-1:
                return list(COLORS.keys())[choice]
            print("Invalid choice. Try again.")
        except ValueError:
            print("Please enter a number.")

class SoundNotifier:
    @staticmethod
    def play_sound(sound_type="notify"):
        """Cross-platform sound playback"""
        sound_file = NOTIFY_SOUND if sound_type == "notify" else MENTION_SOUND
        try:
            if os.path.exists(sound_file):
                system = platform.system()
                if system == "Darwin":
                    os.system(f'afplay "{sound_file}"')
                elif system == "Linux":
                    os.system(f'paplay "{sound_file}"')
                elif system == "Windows":
                    os.system(f'start "" "{sound_file}"')
                return
        except:
            pass
        
        # System fallback sounds
        try:
            system = platform.system()
            if system == "Darwin":
                os.system('afplay /System/Library/Sounds/Ping.aiff')
            elif system == "Linux":
                os.system('paplay /usr/share/sounds/freedesktop/stereo/message.oga')
            elif system == "Windows":
                import winsound
                winsound.MessageBeep()
        except:
            pass

class KaliChatServer:
    def __init__(self, host, port, username, user_color, arrow_color):
        self.clients = {}
        self.usernames = {}
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port))
        self.server.listen(10)
        
        # Network info display
        network_type = choose_network()
        local_ip = get_network_info(network_type)
        
        print(f"\n{COLORS['blue']}╔══════════════════════════════════════════╗")
        print(f"║   KALI LINUX TERMINAL CHAT SERVER      ║")
        print(f"╠══════════════════════════════════════════╣")
        print(f"║ {COLORS['green']}Network Type: {network_type.capitalize():<25}{COLORS['blue']}║")
        print(f"║ {COLORS['green']}Server IP: {local_ip:<30}{COLORS['blue']}║")
        print(f"║ {COLORS['green']}Port: {port:<36}{COLORS['blue']}║")
        print(f"║ {COLORS['green']}Share these details with clients!{COLORS['blue']:>8}║")
        print(f"╚══════════════════════════════════════════╝{COLORS['reset']}")
        
        print(f"\n{COLORS['blue']}[*]{COLORS['reset']} Server {COLORS[user_color]}[{username}@py]{COLORS['reset']} ready for connections...")

    def process_mentions(self, message, current_socket):
        """Handle @mentions with sound notifications"""
        def replace_mention(match):
            mentioned_user = match.group(1)
            if mentioned_user in self.usernames:
                mentioned_socket = self.usernames[mentioned_user]
                if mentioned_socket != current_socket:
                    self.clients[mentioned_socket][3] = True
                    mentioned_socket.send("PLAY_SOUND|mention".encode('utf-8'))
                return f"{COLORS[self.clients[self.usernames[mentioned_user]][1]]}@{mentioned_user}{COLORS['reset']}"
            return match.group(0)
        return re.sub(r'@([a-zA-Z0-9_]+)', replace_mention, message)

    def send_private(self, sender_socket, recipient_name, message):
        """Handle private messages"""
        sender_name, sender_color, _, _ = self.clients[sender_socket]
        
        if recipient_name in self.usernames:
            recipient_socket = self.usernames[recipient_name]
            
            # Format messages
            recipient_msg = f"{COLORS['yellow']}[PM] {sender_name} *whispers* {COLORS[sender_color]}---->{COLORS['reset']} {message}"
            sender_msg = f"{COLORS['purple']}[PM to {recipient_name}] {COLORS[sender_color]}---->{COLORS['reset']} {message}"
            
            try:
                recipient_socket.send(recipient_msg.encode('utf-8'))
                sender_socket.send(sender_msg.encode('utf-8'))
                recipient_socket.send("PLAY_SOUND|mention".encode('utf-8'))
            except:
                self.remove_client(recipient_socket)
                sender_socket.send(f"{COLORS['red']}[!] User {recipient_name} disconnected.{COLORS['reset']}".encode('utf-8'))
        else:
            sender_socket.send(f"{COLORS['red']}[!] User {recipient_name} not found.{COLORS['reset']}".encode('utf-8'))

    def broadcast(self, message, exclude_socket=None):
        """Send message to all clients"""
        processed_msg = self.process_mentions(message, exclude_socket)
        for client_socket in list(self.clients.keys()):
            if client_socket != exclude_socket:
                try:
                    client_socket.send(processed_msg.encode('utf-8'))
                    if self.clients[client_socket][3]:  # Check notify setting
                        client_socket.send("PLAY_SOUND|notify".encode('utf-8'))
                except:
                    self.remove_client(client_socket)

    def remove_client(self, client_socket, graceful=False):
        """Handle client disconnections"""
        if client_socket in self.clients:
            username, _, _, _ = self.clients[client_socket]
            leave_msg = f"{COLORS['yellow']}[-] {username} has {'left gracefully' if graceful else 'disconnected unexpectedly'}.{COLORS['reset']}"
            self.broadcast(leave_msg)
            if username in self.usernames:
                del self.usernames[username]
            del self.clients[client_socket]
            client_socket.close()

    def handle_client(self, client_socket, addr):
        """Manage client connections"""
        try:
            # Initial handshake
            init_data = client_socket.recv(1024).decode('utf-8')
            client_username, client_user_color, client_arrow_color, notify_setting = init_data.split('|')
            notify_setting = notify_setting == "True"
            
            # Register client
            self.clients[client_socket] = (client_username, client_user_color, client_arrow_color, notify_setting)
            self.usernames[client_username] = client_socket
            
            # Broadcast join message
            join_msg = f"{COLORS['yellow']}[+] {client_username} has joined the Terminal!{COLORS['reset']}"
            self.broadcast(join_msg)
            
            # Message handling loop
            while True:
                msg = client_socket.recv(1024).decode('utf-8')
                if not msg:
                    break
                    
                # Command processing
                if msg.strip() == "/exit-terminal-chat":
                    self.remove_client(client_socket, graceful=True)
                    break
                    
                if msg.startswith("/notify-me "):
                    parts = msg.split()
                    if len(parts) == 3 and parts[2] in ["True", "False"]:
                        self.clients[client_socket] = (
                            self.clients[client_socket][0],
                            self.clients[client_socket][1],
                            self.clients[client_socket][2],
                            parts[2] == "True"
                        )
                        client_socket.send(f"{COLORS['green']}[*] Notification setting updated: {parts[2]}{COLORS['reset']}".encode('utf-8'))
                    else:
                        error_msg = f"{COLORS['red']}[!] Invalid command format.{COLORS['reset']}\n"
                        error_msg += f"Usage: /notify-me on every message [True/False]\n"
                        error_msg += f"       {' '*(len(msg.split()[0]) + len(msg.split()[1]) + 1)}{'^'*(len(msg.split()[2]) if len(msg.split()) > 2 else 0)}"
                        client_socket.send(error_msg.encode('utf-8'))
                    continue
                    
                if msg.startswith("/msg "):
                    parts = msg.split(maxsplit=2)
                    if len(parts) >= 3:
                        _, recipient, private_msg = parts
                        self.send_private(client_socket, recipient, private_msg)
                    else:
                        error_msg = f"{COLORS['red']}[!] Invalid private message format.{COLORS['reset']}\n"
                        error_msg += f"Usage: /msg username message\n"
                        error_msg += f"       {' '*(len(msg.split()[0]) + 1)}{'^'*(len(' '.join(msg.split()[1:])))}"
                        client_socket.send(error_msg.encode('utf-8'))
                    continue
                    
                # Broadcast regular message
                formatted_msg = f"{COLORS[client_user_color]}[{client_username}@py]{COLORS['reset']} {COLORS[client_arrow_color]}|---->{COLORS['reset']} {msg}"
                self.broadcast(formatted_msg, exclude_socket=client_socket)
                
        except Exception as e:
            print(f"{COLORS['red']}[!] Client handler error: {e}{COLORS['reset']}")
        finally:
            if client_socket in self.clients:
                self.remove_client(client_socket)

    def run(self):
        """Main server loop"""
        try:
            while len(self.clients) < 10:
                client, addr = self.server.accept()
                threading.Thread(target=self.handle_client, args=(client, addr)).start()
        except KeyboardInterrupt:
            print(f"\n{COLORS['red']}[!] Server shutting down.{COLORS['reset']}")
        finally:
            self.server.close()

class KaliChatClient:
    def __init__(self, host, port, username, user_color, arrow_color):
        self.username = username
        self.user_color = user_color
        self.arrow_color = arrow_color
        self.notify_all = False
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            self.client.connect((host, port))
            print(f"{COLORS['green']}[+]{COLORS['reset']} Connected to {host}:{port} as {COLORS[user_color]}[{username}@py]{COLORS['reset']}")
        except ConnectionRefusedError:
            print(f"\n{COLORS['red']}╔══════════════════════════════════════════╗")
            print(f"║          CONNECTION FAILED!            ║")
            print(f"╠══════════════════════════════════════════╣")
            print(f"║ {COLORS['yellow']}Could not connect to {host}:{port:<16}{COLORS['red']}║")
            print(f"║ {COLORS['yellow']}Possible reasons:                    {COLORS['red']}║")
            print(f"║ {COLORS['yellow']}1. Server is not running             {COLORS['red']}║")
            print(f"║ {COLORS['yellow']}2. Wrong IP/port specified           {COLORS['red']}║")
            print(f"║ {COLORS['yellow']}3. Firewall blocking the connection  {COLORS['red']}║")
            print(f"╚══════════════════════════════════════════╝{COLORS['reset']}")
            exit(1)
        
        # Send initial client data
        self.client.send(f"{username}|{user_color}|{arrow_color}|{self.notify_all}".encode('utf-8'))
        
        print("\nAvailable commands:")
        print(f"{COLORS['yellow']}/exit-terminal-chat{COLORS['reset']} - Disconnect")
        print(f"{COLORS['yellow']}/msg username message{COLORS['reset']} - Private message")
        print(f"{COLORS['yellow']}/notify-me on every message [True/False]{COLORS['reset']} - Toggle notifications")
        print(f"{COLORS['yellow']}@username{COLORS['reset']} - Mention someone (plays sound)")

    def receive_messages(self):
        while True:
            try:
                msg = self.client.recv(1024).decode('utf-8')
                if not msg:
                    print(f"{COLORS['red']}[!] Disconnected from server.{COLORS['reset']}")
                    break
                if msg.startswith("PLAY_SOUND|"):
                    SoundNotifier.play_sound(msg.split("|")[1])
                else:
                    print(f"\n{msg}")
            except:
                break

    def send_messages(self):
        while True:
            msg = input()
            if msg.strip() == "/exit-terminal-chat":
                self.client.send(msg.encode('utf-8'))
                print(f"{COLORS['yellow']}[*] Disconnecting...{COLORS['reset']}")
                break
            if msg.startswith("/notify-me "):
                parts = msg.split()
                if len(parts) == 3 and parts[2] in ["True", "False"]:
                    self.notify_all = parts[2] == "True"
            self.client.send(msg.encode('utf-8'))

    def run(self):
        threading.Thread(target=self.receive_messages, daemon=True).start()
        self.send_messages()

if __name__ == "__main__":
    # Create assets directory if missing
    os.makedirs(SOUND_DIR, exist_ok=True)
    
    parser = argparse.ArgumentParser(description="Kali Linux Terminal Chat")
    parser.add_argument("--host", type=str, help="IP to bind (server) or connect (client)")
    parser.add_argument("--port", type=int, default=65432, help="Port number")
    parser.add_argument("--server", action="store_true", help="Run in server mode")
    parser.add_argument("--username", type=str, required=True, help="Your username")
    args = parser.parse_args()

    print("\n" + "═"*50)
    print(f"{COLORS['blue']} KALI LINUX TERMINAL CHAT {COLORS['reset']}")
    print("═"*50)
    
    user_color = choose_color("Choose username color")
    arrow_color = choose_color("Choose arrow color")

    if args.server:
        server = KaliChatServer(args.host or "0.0.0.0", args.port, args.username, user_color, arrow_color)
        server.run()
    else:
        if not args.host:
            print(f"{COLORS['red']}[!] Must specify --host for client mode{COLORS['reset']}")
            exit(1)
        client = KaliChatClient(args.host, args.port, args.username, user_color, arrow_color)
        client.run()
