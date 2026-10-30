import socket

# Connect to the C++ NS-3 UDP Control Socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
NS3_ADDRESS = ("127.0.0.1", 9998)

while True:
    print("\n" + "="*35)
    print(" NS-3 REAL-TIME ATTACK CONTROLLER ")
    print("="*35)
    print("1. Inject DDoS Flood (50Mbps)")
    print("2. Inject Port Scan")
    print("3. Exit")
    
    choice = input("Select Attack [1-3]: ").strip()
    
    if choice == '1':
        sock.sendto(b"DDOS", NS3_ADDRESS)
        print("[✓] Command sent! Check NS-3 output.")
    elif choice == '2':
        sock.sendto(b"PORTSCAN", NS3_ADDRESS)
        print("[✓] Command sent! Check NS-3 output.")
    elif choice == '3':
        break
    else:
        print("Invalid choice.")
