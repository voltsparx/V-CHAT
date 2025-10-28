import socket
import threading
import argparse
import re
import os
import platform
import sys
from datetime import datetime
try:
    # Use colorama for cross-platform ANSI color support on Windows
    from colorama import init
except ImportError:
    # Fallback if colorama is not installed
    def init(autoreset=True):
        pass

# --- External Dependencies Notes ---
# Sound playback uses 'os.system', which relies on external commands (afplay, paplay, winsound).
# This is kept as a demonstration but clarified it needs system-specific tools/files.

# --- ANSI Color Setup ---
# Defined colors for the CLI aesthetic
COLORS = {
    'red': '\033[91m', 'orange': '\033[38;5;208m', 'purple': '\033[95m',
    'green': '\033[92m', 'blue': '\033[94m', 'light-blue': '\033[96m',
    'light-green': '\033[38;5;120m', 'yellow': '\033[93m',
    'pink': '\033[38;5;205m', 'light-pink': '\033[38;5;219m',
    'brown': '\033[38;5;130m', 'reset': '\033[0m'
}

def clear_screen():
    """Clears the terminal screen cross-platform."""
    # os.system is used to run shell commands to clear the screen.
    os.system('cls' if platform.system() == "Windows" else 'clear')

def print_banner():
    """Prints the application banner with colors using a simple line-based ASCII design, including author info."""
    clear_screen()
    orange = COLORS['orange']
    blue = COLORS['blue']
    yellow = COLORS['yellow']
    reset = COLORS['reset']
    
    # Simple ASCII Art banner for V-Chat using lines and dashes
    banner = [
        f"{orange}/–––––––––––––––––––––––––––––––––––––––––––––––––––––––––\\{reset}",
        f"{orange}|  {blue}V - C H A T{orange}   //   {blue}C L I   C H A T   T O O L{orange}   |{reset}",
        f"{orange}\\–––––––––––––––––––––––––––––––––––––––––––––––––––––––––/{reset}",
        f"  {blue}> P2P Communication via Socket Threads <{reset}",
        f"  {yellow}Author: Voltsparx | Contact: voltsparx@gmail.com{reset}"
    ]
    
    # Add an empty line for spacing
    print()
    for line in banner:
        print(line)
    print()


def get_local_ip():
    """Attempts to get the non-localhost IP address of the machine."""
    try:
        # Create a temporary socket to connect to a known external host (doesn't send data)
        # This forces the OS to determine the correct outgoing interface IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80)) # Google's public DNS
        ip = s.getsockname()[0]
        s.close()
        return ip
    except socket.error:
        # Fallback to localhost if no network connection is available
        return "127.0.0.1"

def choose_color(prompt):
    """Color selection menu for user preferences."""
    print(f"\n{COLORS['blue']}Select Appearance Color:{COLORS['reset']}")
    color_items = [c for c in COLORS.keys() if c != 'reset']
    
    for i, color in enumerate(color_items, 1):
        # Display the color name in its actual color
        print(f"{i}. {COLORS[color]}{color.capitalize()}{COLORS['reset']}")
    
    while True:
        try:
            choice = input(f"{prompt} (1-{len(color_items)}): ")
            if not choice.isdigit():
                 print(f"{COLORS['red']}Please enter a number.{COLORS['reset']}")
                 continue
                 
            choice_index = int(choice) - 1
            if 0 <= choice_index < len(color_items):
                return color_items[choice_index]
            print(f"{COLORS['red']}Invalid choice. Try again.{COLORS['reset']}")
        except ValueError:
            print(f"{COLORS['red']}Please enter a number.{COLORS['reset']}")

class SoundNotifier:
    """Class to handle cross-platform sound playback (best effort)."""
    # NOTE: Since we cannot guarantee the existence of specific sound files, 
    # this function provides system-level sound as a best-effort fallback.
    @staticmethod
    def play_sound(sound_type="notify"):
        """Plays a system-level notification sound."""
        system = platform.system()
        
        try:
            if system == "Darwin":
                # macOS
                os.system('afplay /System/Library/Sounds/Ping.aiff &')
            elif system == "Linux":
                # Linux (requires paplay or similar)
                os.system('paplay /usr/share/sounds/freedesktop/stereo/message-new-instant.oga &')
            elif system == "Windows":
                # Windows (requires winsound module)
                import winsound
                winsound.MessageBeep(winsound.MB_ICONASTERISK)
            return
        except Exception:
            # Silent failure if sound cannot be played
            pass

class ChatServer:
    def __init__(self, host, port, username, user_color, arrow_color):
        self.clients = {}  # {socket: (username, user_color, arrow_color)}
        self.usernames = {}  # {username: socket}
        self.username = username
        self.user_color = user_color
        self.arrow_color = arrow_color
        
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Allows reuse of the port after the server is stopped
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port))
        self.server.listen(10)
        
        local_ip = get_local_ip()
        
        print(f"\n{COLORS['blue']}╔══════════════════════════════════════════╗")
        print(f"║   V-CHAT SERVER v2.0 - LIVE           ║")
        print(f"╠══════════════════════════════════════════╣")
        print(f"║ {COLORS['green']}Bind Host: {host:<30}{COLORS['blue']}║")
        print(f"║ {COLORS['green']}Local IP:  {local_ip:<30}{COLORS['blue']}║")
        print(f"║ {COLORS['green']}Port:      {port:<30}{COLORS['blue']}║")
        print(f"║ {COLORS['yellow']}Share the IP/Port above with clients!{COLORS['blue']}║")
        print(f"╚══════════════════════════════════════════╝{COLORS['reset']}")
        
        # Add server's own information to the user list for full functionality
        self.server_socket = socket.socket() # Dummy socket for server's own data
        self.clients[self.server_socket] = (username, user_color, arrow_color)
        self.usernames[username] = self.server_socket
        
        print(f"\n{COLORS['blue']}[*]{COLORS['reset']} Server running as {COLORS[user_color]}[{username}]{COLORS['reset']}...")

    def process_mentions(self, message, current_socket):
        """Handle @mentions by highlighting the username."""
        
        def replace_mention(match):
            mentioned_user = match.group(1)
            # Find the mentioned user's color for highlighting
            mentioned_sock = self.usernames.get(mentioned_user)
            if mentioned_sock and mentioned_sock in self.clients:
                mentioned_color = self.clients[mentioned_sock][1]
                # Send sound command to the mentioned client
                if mentioned_sock != self.server_socket:
                    try:
                        mentioned_sock.send("PLAY_SOUND|mention".encode('utf-8'))
                    except Exception:
                        pass
                
                return f"{COLORS[mentioned_color]}@{mentioned_user}{COLORS['reset']}"
            return match.group(0) # If user not found, return as-is
        
        return re.sub(r'@([a-zA-Z0-9_]+)', replace_mention, message)

    def send_private(self, sender_socket, recipient_name, message):
        """Handles private messages between users."""
        if recipient_name not in self.usernames:
            # Send error message back to sender
            sender_socket.send(f"{COLORS['red']}[!] User '{recipient_name}' not found.{COLORS['reset']}".encode('utf-8'))
            return

        sender_name, sender_color, _, = self.clients[sender_socket]
        recipient_socket = self.usernames[recipient_name]
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Message for the recipient
        recipient_msg = f"{COLORS['yellow']}[PM @{timestamp}] {sender_name} {COLORS[sender_color]}->{COLORS['reset']} {message}"
        # Message confirmation for the sender
        sender_msg = f"{COLORS['purple']}[PM to {recipient_name} @{timestamp}] {COLORS[sender_color]}->{COLORS['reset']} {message}"
        
        try:
            if recipient_socket != self.server_socket:
                recipient_socket.send(recipient_msg.encode('utf-8'))
                # Play sound for recipient
                recipient_socket.send("PLAY_SOUND|mention".encode('utf-8'))
            else:
                 # If server is recipient (i.e., server is sending PM to itself)
                print(recipient_msg)
            
            # Send confirmation back to sender (unless sender is server itself)
            if sender_socket != self.server_socket:
                sender_socket.send(sender_msg.encode('utf-8'))
            else:
                 print(sender_msg)
                 
        except Exception as e:
            print(f"{COLORS['red']}[!] PM send error for {recipient_name}: {e}{COLORS['reset']}")
            # If recipient socket fails, remove them
            self.remove_client(recipient_socket)

    def broadcast(self, message, exclude_socket=None):
        """Sends a message to all connected clients."""
        processed_msg = self.process_mentions(message, exclude_socket)
        
        # Print to server console
        if exclude_socket != self.server_socket:
            print(processed_msg)

        # Send to all clients
        for client_socket in list(self.clients.keys()):
            # Do not send to the server's dummy socket or the excluded socket
            if client_socket != exclude_socket and client_socket != self.server_socket:
                try:
                    client_socket.send(processed_msg.encode('utf-8'))
                    # Send generic notification sound trigger
                    client_socket.send("PLAY_SOUND|notify".encode('utf-8'))
                except Exception:
                    # If sending fails, assume the client is disconnected
                    self.remove_client(client_socket)

    def remove_client(self, client_socket, graceful=False):
        """Handles client disconnections and informs others."""
        if client_socket in self.clients and client_socket != self.server_socket:
            username, _, _ = self.clients[client_socket]
            timestamp = datetime.now().strftime("%H:%M:%S")
            leave_msg = f"{COLORS['yellow']}[{timestamp}] {username} has {'left gracefully' if graceful else 'disconnected unexpectedly'}.{COLORS['reset']}"
            
            self.broadcast(leave_msg, exclude_socket=client_socket)
            
            # Clean up the dictionaries
            if username in self.usernames:
                del self.usernames[username]
            del self.clients[client_socket]
            
            try:
                client_socket.close()
            except:
                pass

    def handle_client(self, client_socket, addr):
        """Manages the connection and message flow for a single client."""
        try:
            # 1. Initial Handshake: Receive username and color preferences
            init_data = client_socket.recv(1024).decode('utf-8')
            if not init_data:
                raise ValueError("Empty handshake data")
                
            parts = init_data.split('|')
            if len(parts) != 3:
                raise ValueError("Invalid handshake format")
                
            client_username, client_user_color, client_arrow_color = parts
            
            # 2. Check for duplicate usernames
            if client_username in self.usernames:
                client_socket.send(f"{COLORS['red']}[!] Username '{client_username}' already taken. Disconnecting.{COLORS['reset']}".encode('utf-8'))
                client_socket.close()
                return
                
            # 3. Register client
            self.clients[client_socket] = (client_username, client_user_color, client_arrow_color)
            self.usernames[client_username] = client_socket
            
            # 4. Broadcast join message
            timestamp = datetime.now().strftime("%H:%M:%S")
            join_msg = f"{COLORS['yellow']}[{timestamp}] {client_username} has joined the chat!{COLORS['reset']}"
            self.broadcast(join_msg, exclude_socket=client_socket)
            
            # 5. Send welcome message
            welcome_msg = f"{COLORS['green']}[*] Welcome to V-Chat, {client_username}! Type /help for commands.{COLORS['reset']}"
            client_socket.send(welcome_msg.encode('utf-8'))
            
            # 6. Message handling loop
            while True:
                try:
                    msg = client_socket.recv(1024).decode('utf-8')
                    if not msg:
                        break # Client disconnected
                        
                    # Command processing
                    if msg.strip() == "/exit":
                        self.remove_client(client_socket, graceful=True)
                        break
                        
                    if msg.strip() == "/users":
                        self.handle_users_command(client_socket)
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
                        
                    if msg.startswith("/help"):
                        # Send help message back to client
                        self.send_help(client_socket)
                        continue
                        
                    # Broadcast regular message
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    # Format: [HH:MM:SS Username] » Message
                    formatted_msg = (
                        f"{COLORS[client_user_color]}[{timestamp} {client_username}]{COLORS['reset']} "
                        f"{COLORS[client_arrow_color]}»{COLORS['reset']} {msg}"
                    )
                    self.broadcast(formatted_msg, exclude_socket=client_socket)
                    
                except Exception:
                    break # Break on socket error

        except Exception as e:
            print(f"{COLORS['red']}[!] Client handler error ({addr[0]}): {e}{COLORS['reset']}")
        finally:
            self.remove_client(client_socket)

    def handle_users_command(self, client_socket):
        """Sends the list of online users to the requesting client."""
        users_list = f"{COLORS['blue']}Online users ({len(self.usernames)-1}):{COLORS['reset']}\n"
        
        # Filter out the server's own dummy socket for count and display
        online_users = [
            (username, color) for sock, (username, color, _) in self.clients.items()
            if sock != self.server_socket
        ]

        users_list += "\n".join([f"  {COLORS[color]}{user}{COLORS['reset']}" 
                               for user, color in online_users])
        
        # Send the list
        client_socket.send(users_list.encode('utf-8'))

    def send_help(self, client_socket):
        """Sends the available commands list to the requesting client."""
        help_msg = f"\n{COLORS['blue']}Available commands:{COLORS['reset']}\n"
        help_msg += f"{COLORS['yellow']}/exit{COLORS['reset']} - Disconnect from chat\n"
        help_msg += f"{COLORS['yellow']}/msg username message{COLORS['reset']} - Send private message\n"
        help_msg += f"{COLORS['yellow']}/users{COLORS['reset']} - List online users\n"
        help_msg += f"{COLORS['yellow']}@username{COLORS['reset']} - Mention someone (plays sound)\n"
        
        client_socket.send(help_msg.encode('utf-8'))


    def run(self):
        """Main server loop, accepting connections."""
        try:
            while True:
                client, addr = self.server.accept()
                print(f"{COLORS['green']}[+] New connection from {addr[0]}:{addr[1]}{COLORS['reset']}")
                # Start a new thread to handle each client connection
                threading.Thread(target=self.handle_client, args=(client, addr)).start()
        except KeyboardInterrupt:
            print(f"\n{COLORS['red']}[!] Server shutting down.{COLORS['reset']}")
        except Exception as e:
            print(f"{COLORS['red']}[!] Server error: {e}{COLORS['reset']}")
        finally:
            # Cleanup all active client connections
            for client in list(self.clients.keys()):
                self.remove_client(client)
            self.server.close()

class ChatClient:
    def __init__(self, host, port, username, user_color, arrow_color):
        self.username = username
        self.user_color = user_color
        self.arrow_color = arrow_color
        self.running = True
        
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((host, port))
            
            # Send initial client data (username and colors)
            self.client.send(f"{username}|{user_color}|{arrow_color}".encode('utf-8'))
            
            print(f"\n{COLORS['green']}[+]{COLORS['reset']} Connected to {host}:{port} as {COLORS[user_color]}[{username}]{COLORS['reset']}")
            
            self.print_help()
            
        except ConnectionRefusedError:
            self.show_connection_error(host, port)
            sys.exit(1)
        except Exception as e:
            print(f"{COLORS['red']}[!] Connection error: {e}{COLORS['reset']}")
            sys.exit(1)

    def show_connection_error(self, host, port):
        """Display detailed connection error."""
        print(f"\n{COLORS['red']}╔══════════════════════════════════════════╗")
        print(f"║          CONNECTION FAILED!            ║")
        print(f"╠══════════════════════════════════════════╣")
        print(f"║ {COLORS['yellow']}Could not connect to {host}:{port:<16}{COLORS['red']}║")
        print(f"║ {COLORS['yellow']}Check if the server is running and the{COLORS['red']}║")
        print(f"║ {COLORS['yellow']}IP/Port are correct (e.g., firewall issues).{COLORS['red']}║")
        print(f"╚══════════════════════════════════════════╝{COLORS['reset']}")

    def print_help(self):
        """Print available commands to the client console."""
        print(f"\n{COLORS['blue']}Available commands:{COLORS['reset']}")
        print(f"{COLORS['yellow']}/exit{COLORS['reset']} - Disconnect from chat")
        print(f"{COLORS['yellow']}/msg username message{COLORS['reset']} - Send private message")
        print(f"{COLORS['yellow']}/users{COLORS['reset']} - List online users")
        print(f"{COLORS['yellow']}/help{COLORS['reset']} - Show this list again")
        print(f"{COLORS['yellow']}@username{COLORS['reset']} - Mention someone (plays sound on their end)")
        print(f"\n{COLORS['green']}Start chatting below:{COLORS['reset']}")

    def receive_messages(self):
        """Thread for receiving messages from the server."""
        while self.running:
            try:
                # Use a larger buffer for potentially long colored messages
                msg = self.client.recv(4096).decode('utf-8') 
                if not msg:
                    # Server closed the connection
                    print(f"\n{COLORS['red']}[!] Disconnected from server.{COLORS['reset']}")
                    self.running = False
                    break
                    
                def run(self):
        """Starts the client process."""
        # Start the thread to listen for messages from the server
        receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
        receive_thread.start()
        
        # Start the main input thread
        self.send_messages()
        
        # Cleanup
        self.client.close()
        receive_thread.join(1)

if __name__ == "__main__":
    # Initialize colorama for Windows if available
    try:
        init(autoreset=True)
    except NameError:
        pass # colorama not imported

    # --- Argument Parsing ---
    parser = argparse.ArgumentParser(
        description="V-Chat: A CLI P2P Chat Application. Run with --server to start a server."
    )
    parser.add_argument(
        "--host", 
        type=str, 
        help="IP address to BIND (server) or CONNECT (client)."
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=65432, 
        help="Port number to use (default: 65432)."
    )
    parser.add_argument(
        "--server", 
        action="store_true", 
        help="Run V-Chat in server mode."
    )
    parser.add_argument(
        "--username", 
        type=str, 
        required=True, 
        help="Your desired display username."
    )
    args = parser.parse_args()

    # --- Setup and Run ---
    print_banner()
    
    # Get user preferences for colors
    user_color = choose_color("Choose username color")
    arrow_color = choose_color("Choose message arrow color")

    # Start application logic
    if args.server:
        # Server mode
        server = ChatServer(args.host or "0.0.0.0", args.port, args.username, user_color, arrow_color)
        server.run()
    else:
        # Client mode
        if not args.host:
            print(f"{COLORS['red']}[!] Must specify --host (IP of the server) when running in client mode.{COLORS['reset']}")
            sys.exit(1)
        client = ChatClient(args.host, args.port, args.username, user_color, arrow_color)
        client.run()
