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
    os.system('cls' if platform.system() == "Windows" else 'clear')

def print_banner():
    """Prints the application banner with colors"""
    clear_screen()
    orange = COLORS['orange']
    reset = COLORS['reset']
    
    banner = [
        "█▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀█",
        "█  ██╗   ██╗         ██████╗██╗  ██╗ █████╗ ████████╗  █",
        "█  ╚██╗ ██╔╝        ██╔════╝██║  ██║██╔══██╗╚══██╔══╝  █",
        "█   ╚█  █╔╝ █████╗  ██║     ███████║███████║   ██║     █",
        "█    ╚██╔╝  ╚════╝  ██║     ██╔══██║██╔══██║   ██║     █",
        "█     ██║           ╚██████╗██║  ██║██║  ██║   ██║     █",
        "█     ╚═╝            ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝     █",
        "█▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄█",
        "║► BY: Voltsparx                         VERSION: 2.0 ◄║",
        "║► Contact: voltsparx@gmail.com                       ◄║",
        "║► Repo: https://github.com/voltsparx/V-CHAT          ◄║",
        "▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀"
    ]
    
    for line in banner:
        print(f"{orange}{line}{reset}")

def get_network_info(network_type):
    """Get IP address based on selected network type"""
    try:
        if network_type == "internet":
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        
        interfaces = netifaces.interfaces()
        for interface in interfaces:
            if (network_type == "wifi" and ("wl" in interface or "wlan" in interface or "en0" in interface)) or \
               (network_type == "ethernet" and ("eth" in interface or "en" in interface)):
                addrs = netifaces.ifaddresses(interface)
                if netifaces.AF_INET in addrs:
                    return addrs[netifaces.AF_INET][0]['addr']
    except Exception as e:
        print(f"{COLORS['red']}[!] Network detection error: {e}{COLORS['reset']}")
    return "127.0.0.1"

def choose_network():
    """Network type selection menu"""
    print(f"\n{COLORS['blue']}Select Network Type:{COLORS['reset']}")
    print(f"1. {COLORS['green']}Internet (Public IP){COLORS['reset']}")
    print(f"2. {COLORS['blue']}WiFi (Local Network){COLORS['reset']}")
    print(f"3. {COLORS['purple']}Ethernet (Local Network){COLORS['reset']}")
    
    while True:
        choice = input(f"{COLORS['yellow']}Choose (1-3): {COLORS['reset']}")
        if choice == "1": return "internet"
        elif choice == "2": return "wifi"
        elif choice == "3": return "ethernet"
        print(f"{COLORS['red']}Invalid choice. Try again.{COLORS['reset']}")

def choose_color(prompt):
    """Color selection menu"""
    print(f"\n{COLORS['blue']}Available colors:{COLORS['reset']}")
    color_items = [c for c in COLORS.keys() if c != 'reset']
    
    for i, color in enumerate(color_items, 1):
        print(f"{i}. {COLORS[color]}{color}{COLORS['reset']}")
    
    while True:
        try:
            choice = int(input(f"{prompt} (1-{len(color_items)}): ")) - 1
            if 0 <= choice < len(color_items):
                return color_items[choice]
            print(f"{COLORS['red']}Invalid choice. Try again.{COLORS['reset']}")
        except ValueError:
            print(f"{COLORS['red']}Please enter a number.{COLORS['reset']}")

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
        except Exception as e:
            print(f"{COLORS['red']}[!] Sound error: {e}{COLORS['reset']}")
        
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
        except Exception as e:
            print(f"{COLORS['red']}[!] System sound error: {e}{COLORS['reset']}")

class ChatServer:
    def __init__(self, host, port, username, user_color, arrow_color):
        self.clients = {}  # {socket: (username, user_color, arrow_color, notify_setting)}
        self.usernames = {}  # {username: socket}
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port))
        self.server.listen(10)
        
        # Network info display
        network_type = choose_network()
        local_ip = get_network_info(network_type)
        
        print(f"\n{COLORS['blue']}╔══════════════════════════════════════════╗")
        print(f"║   TERMINAL CHAT SERVER v2.0           ║")
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
            if mentioned_user in self.usernames and mentioned_user != self.clients[current_socket][0]:
                mentioned_socket = self.usernames[mentioned_user]
                self.clients[mentioned_socket] = (*self.clients[mentioned_socket][:3], True)
                mentioned_socket.send("PLAY_SOUND|mention".encode('utf-8'))
                return f"{COLORS[self.clients[mentioned_socket][1]]}@{mentioned_user}{COLORS['reset']}"
            return match.group(0)
        
        return re.sub(r'@([a-zA-Z0-9_]+)', replace_mention, message)

    def send_private(self, sender_socket, recipient_name, message):
        """Handle private messages"""
        if recipient_name not in self.usernames:
            sender_socket.send(f"{COLORS['red']}[!] User '{recipient_name}' not found.{COLORS['reset']}".encode('utf-8'))
            return

        sender_name, sender_color, _, _ = self.clients[sender_socket]
        recipient_socket = self.usernames[recipient_name]
        
        # Format messages
        timestamp = datetime.now().strftime("%H:%M:%S")
        recipient_msg = f"{COLORS['yellow']}[PM @{timestamp}] {sender_name} *whispers* {COLORS[sender_color]}---->{COLORS['reset']} {message}"
        sender_msg = f"{COLORS['purple']}[PM to {recipient_name} @{timestamp}] {COLORS[sender_color]}---->{COLORS['reset']} {message}"
        
        try:
            recipient_socket.send(recipient_msg.encode('utf-8'))
            sender_socket.send(sender_msg.encode('utf-8'))
            recipient_socket.send("PLAY_SOUND|mention".encode('utf-8'))
        except Exception as e:
            print(f"{COLORS['red']}[!] PM error: {e}{COLORS['reset']}")
            self.remove_client(recipient_socket)
            sender_socket.send(f"{COLORS['red']}[!] User {recipient_name} disconnected.{COLORS['reset']}".encode('utf-8'))

    def broadcast(self, message, exclude_socket=None):
        """Send message to all clients"""
        processed_msg = self.process_mentions(message, exclude_socket)
        for client_socket in list(self.clients.keys()):
            if client_socket != exclude_socket:
                try:
                    client_socket.send(processed_msg.encode('utf-8'))
                    if self.clients[client_socket][3]:  # Check notify setting
                        client_socket.send("PLAY_SOUND|notify".encode('utf-8'))
                except Exception as e:
                    print(f"{COLORS['red']}[!] Broadcast error: {e}{COLORS['reset']}")
                    self.remove_client(client_socket)

    def remove_client(self, client_socket, graceful=False):
        """Handle client disconnections"""
        if client_socket in self.clients:
            username, _, _, _ = self.clients[client_socket]
            timestamp = datetime.now().strftime("%H:%M:%S")
            leave_msg = f"{COLORS['yellow']}[{timestamp}] {username} has {'left gracefully' if graceful else 'disconnected unexpectedly'}.{COLORS['reset']}"
            self.broadcast(leave_msg)
            
            if username in self.usernames:
                del self.usernames[username]
            if client_socket in self.clients:
                del self.clients[client_socket]
            
            try:
                client_socket.close()
            except:
                pass

    def handle_client(self, client_socket, addr):
        """Manage client connections"""
        try:
            # Initial handshake
            init_data = client_socket.recv(1024).decode('utf-8')
            if not init_data:
                raise ValueError("Empty handshake data")
                
            parts = init_data.split('|')
            if len(parts) != 4:
                raise ValueError("Invalid handshake format")
                
            client_username, client_user_color, client_arrow_color, notify_setting = parts
            notify_setting = notify_setting == "True"
            
            # Check for duplicate usernames
            if client_username in self.usernames:
                client_socket.send(f"{COLORS['red']}[!] Username '{client_username}' already taken.{COLORS['reset']}".encode('utf-8'))
                client_socket.close()
                return
                
            # Register client
            self.clients[client_socket] = (client_username, client_user_color, client_arrow_color, notify_setting)
            self.usernames[client_username] = client_socket
            
            # Broadcast join message
            timestamp = datetime.now().strftime("%H:%M:%S")
            join_msg = f"{COLORS['yellow']}[{timestamp}] {client_username} has joined the chat!{COLORS['reset']}"
            self.broadcast(join_msg)
            
            # Send welcome message
            welcome_msg = f"{COLORS['green']}[*] Welcome to the chat, {client_username}!{COLORS['reset']}"
            client_socket.send(welcome_msg.encode('utf-8'))
            
            # Message handling loop
            while True:
                try:
                    msg = client_socket.recv(1024).decode('utf-8')
                    if not msg:
                        break
                        
                    # Command processing
                    if msg.strip() == "/exit":
                        self.remove_client(client_socket, graceful=True)
                        break
                        
                    if msg.startswith("/notify "):
                        parts = msg.split()
                        if len(parts) == 2 and parts[1] in ["True", "False"]:
                            self.clients[client_socket] = (
                                self.clients[client_socket][0],
                                self.clients[client_socket][1],
                                self.clients[client_socket][2],
                                parts[1] == "True"
                            )
                            client_socket.send(f"{COLORS['green']}[*] Notifications {'enabled' if parts[1] == 'True' else 'disabled'}.{COLORS['reset']}".encode('utf-8'))
                        else:
                            error_msg = f"{COLORS['red']}[!] Usage: /notify [True/False]{COLORS['reset']}"
                            client_socket.send(error_msg.encode('utf-8'))
                        continue
                        
                    if msg.startswith("/msg "):
                        parts = msg.split(maxsplit=2)
                        if len(parts) >= 3:
                            _, recipient, private_msg = parts
                            self.send_private(client_socket, recipient, private_msg)
                        else:
                            error_msg = f"{COLORS['red']}[!] Usage: /msg username message{COLORS['reset']}"
                            client_socket.send(error_msg.encode('utf-8'))
                        continue
                        
                    if msg.strip() == "/users":
                        users_list = f"{COLORS['blue']}Online users ({len(self.usernames)}):{COLORS['reset']}\n"
                        users_list += "\n".join([f"  {COLORS[self.clients[sock][1]]}{user}{COLORS['reset']}" 
                                               for user, sock in self.usernames.items()])
                        client_socket.send(users_list.encode('utf-8'))
                        continue
                        
                    # Broadcast regular message
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    formatted_msg = f"{COLORS[client_user_color]}[{timestamp} {client_username}]{COLORS['reset']} {COLORS[client_arrow_color]}»{COLORS['reset']} {msg}"
                    self.broadcast(formatted_msg, exclude_socket=client_socket)
                    
                except Exception as e:
                    print(f"{COLORS['red']}[!] Message handling error: {e}{COLORS['reset']}")
                    break
                    
        except Exception as e:
            print(f"{COLORS['red']}[!] Client handler error: {e}{COLORS['reset']}")
        finally:
            self.remove_client(client_socket)

    def run(self):
        """Main server loop"""
        try:
            while True:
                client, addr = self.server.accept()
                print(f"{COLORS['green']}[+] New connection from {addr[0]}:{addr[1]}{COLORS['reset']}")
                threading.Thread(target=self.handle_client, args=(client, addr)).start()
        except KeyboardInterrupt:
            print(f"\n{COLORS['red']}[!] Server shutting down.{COLORS['reset']}")
        except Exception as e:
            print(f"{COLORS['red']}[!] Server error: {e}{COLORS['reset']}")
        finally:
            for client in list(self.clients.keys()):
                self.remove_client(client)
            self.server.close()

class ChatClient:
    def __init__(self, host, port, username, user_color, arrow_color):
        self.username = username
        self.user_color = user_color
        self.arrow_color = arrow_color
        self.notify_all = True
        self.running = True
        
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((host, port))
            print(f"{COLORS['green']}[+]{COLORS['reset']} Connected to {host}:{port} as {COLORS[user_color]}[{username}]{COLORS['reset']}")
            
            # Send initial client data
            self.client.send(f"{username}|{user_color}|{arrow_color}|{self.notify_all}".encode('utf-8'))
            
            # Print help
            self.print_help()
            
        except ConnectionRefusedError:
            self.show_connection_error(host, port)
            exit(1)
        except Exception as e:
            print(f"{COLORS['red']}[!] Connection error: {e}{COLORS['reset']}")
            exit(1)

    def show_connection_error(self, host, port):
        """Display detailed connection error"""
        print(f"\n{COLORS['red']}╔══════════════════════════════════════════╗")
        print(f"║          CONNECTION FAILED!            ║")
        print(f"╠══════════════════════════════════════════╣")
        print(f"║ {COLORS['yellow']}Could not connect to {host}:{port:<16}{COLORS['red']}║")
        print(f"║ {COLORS['yellow']}Possible reasons:                    {COLORS['red']}║")
        print(f"║ {COLORS['yellow']}1. Server is not running             {COLORS['red']}║")
        print(f"║ {COLORS['yellow']}2. Wrong IP/port specified           {COLORS['red']}║")
        print(f"║ {COLORS['yellow']}3. Firewall blocking the connection  {COLORS['red']}║")
        print(f"║ {COLORS['yellow']}4. Network issues                    {COLORS['red']}║")
        print(f"╚══════════════════════════════════════════╝{COLORS['reset']}")

    def print_help(self):
        """Print available commands"""
        print(f"\n{COLORS['blue']}Available commands:{COLORS['reset']}")
        print(f"{COLORS['yellow']}/exit{COLORS['reset']} - Disconnect from chat")
        print(f"{COLORS['yellow']}/msg username message{COLORS['reset']} - Send private message")
        print(f"{COLORS['yellow']}/notify [True/False]{COLORS['reset']} - Toggle message notifications")
        print(f"{COLORS['yellow']}/users{COLORS['reset']} - List online users")
        print(f"{COLORS['yellow']}@username{COLORS['reset']} - Mention someone (plays sound)")
        print(f"\n{COLORS['green']}Start chatting below:{COLORS['reset']}")

    def receive_messages(self):
        """Thread for receiving messages from server"""
        while self.running:
            try:
                msg = self.client.recv(1024).decode('utf-8')
                if not msg:
                    print(f"{COLORS['red']}[!] Disconnected from server.{COLORS['reset']}")
                    self.running = False
                    break
                    
                if msg.startswith("PLAY_SOUND|"):
                    SoundNotifier.play_sound(msg.split("|")[1])
                else:
                    print(f"\n{msg}", end='\n> ')
            except Exception as e:
                if self.running:  # Only show error if we didn't initiate disconnect
                    print(f"{COLORS['red']}[!] Receive error: {e}{COLORS['reset']}")
                self.running = False
                break

    def send_messages(self):
        """Main thread for sending messages"""
        while self.running:
            try:
                msg = input("> ")
                if not msg.strip():
                    continue
                    
                if msg.strip() == "/exit":
                    self.client.send("/exit".encode('utf-8'))
                    print(f"{COLORS['yellow']}[*] Disconnecting...{COLORS['reset']}")
                    self.running = False
                    break
                    
                self.client.send(msg.encode('utf-8'))
            except KeyboardInterrupt:
                print(f"\n{COLORS['yellow']}[*] Disconnecting...{COLORS['reset']}")
                self.client.send("/exit".encode('utf-8'))
                self.running = False
                break
            except Exception as e:
                print(f"{COLORS['red']}[!] Send error: {e}{COLORS['reset']}")
                self.running = False
                break

    def run(self):
        """Start client threads"""
        receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
        receive_thread.start()
        
        self.send_messages()
        
        # Cleanup
        self.client.close()
        receive_thread.join(1)

if __name__ == "__main__":
    # Initialize colorama
    init(autoreset=True)
    
    # Create assets directory if missing
    os.makedirs(SOUND_DIR, exist_ok=True)
    
    # Parse arguments
    parser = argparse.ArgumentParser(description="Terminal Chat Application")
    parser.add_argument("--host", type=str, help="IP to bind (server) or connect (client)")
    parser.add_argument("--port", type=int, default=65432, help="Port number (default: 65432)")
    parser.add_argument("--server", action="store_true", help="Run in server mode")
    parser.add_argument("--username", type=str, required=True, help="Your username")
    args = parser.parse_args()

    # Show banner
    print_banner()
    
    # Get user preferences
    print(f"\n{COLORS['blue']}Customize your chat appearance:{COLORS['reset']}")
    user_color = choose_color("Choose username color")
    arrow_color = choose_color("Choose message arrow color")

    # Start server or client
    if args.server:
        server = ChatServer(args.host or "0.0.0.0", args.port, args.username, user_color, arrow_color)
        server.run()
    else:
        if not args.host:
            print(f"{COLORS['red']}[!] Must specify --host for client mode{COLORS['reset']}")
            exit(1)
        client = ChatClient(args.host, args.port, args.username, user_color, arrow_color)
        client.run()
