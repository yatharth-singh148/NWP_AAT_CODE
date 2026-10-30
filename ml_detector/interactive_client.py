import socket
import json
import time
import random
import threading
import sys

HOST = "127.0.0.1"
PORT = 9999

def generate_flow(attack_type="Benign"):
    """Generates features exactly matching IoT-23 dataset signatures."""
    # Base Benign Flow
    flow = {
        "id.orig_p": random.randint(40000, 60000),
        "id.resp_p": 80,
        "proto": "tcp",
        "service": "-",
        "duration": random.uniform(0.1, 5.0),
        "orig_bytes": random.randint(100, 1000),
        "resp_bytes": random.randint(100, 5000),
        "conn_state": "SF",
        "local_orig": "-",
        "local_resp": "-",
        "missed_bytes": 0,
        "history": "ShAdDa",
        "orig_pkts": random.randint(5, 20),
        "orig_ip_bytes": random.randint(500, 2000),
        "resp_pkts": random.randint(5, 20),
        "resp_ip_bytes": random.randint(500, 5000),
        "attack_type": attack_type
    }

    # Override with precise Malicious ML features
    if attack_type == "DDoS":
        flow["proto"] = "udp"
        flow["conn_state"] = "S0"
        flow["history"] = "D"
        flow["duration"] = 0.0
        flow["orig_bytes"] = 0
        flow["resp_bytes"] = 0
        flow["orig_pkts"] = random.randint(1000, 5000)
        flow["resp_pkts"] = 0
        flow["orig_ip_bytes"] = flow["orig_pkts"] * 40
        flow["resp_ip_bytes"] = 0
        
    elif attack_type == "PortScan":
        flow["id.resp_p"] = random.randint(1, 1024)
        flow["conn_state"] = "S0"
        flow["history"] = "S"
        flow["duration"] = 0.0
        flow["orig_bytes"] = 0
        flow["resp_bytes"] = 0
        flow["orig_pkts"] = 1
        flow["resp_pkts"] = 0
        flow["orig_ip_bytes"] = 40
        flow["resp_ip_bytes"] = 0

    elif attack_type == "C&C_Beacon":
        flow["conn_state"] = "OTH"
        flow["history"] = "C"
        flow["orig_bytes"] = 0
        flow["resp_bytes"] = 0
        
    return flow

def send_flow(sock, attack_type):
    flow = generate_flow(attack_type)
    payload = json.dumps(flow) + "\n"
    sock.sendall(payload.encode('utf-8'))

def continuous_mode(sock):
    print("\n[+] Starting Continuous Mode. Press Ctrl+C to stop.")
    print("[+] Sending mostly benign traffic, injecting random anomalies...\n")
    try:
        while True:
            # 90% chance benign, 10% chance anomaly
            if random.random() < 0.10:
                anomaly = random.choice(["DDoS", "PortScan", "C&C_Beacon"])
                print(f"[*] Auto-injecting anomaly: {anomaly}")
                send_flow(sock, anomaly)
            else:
                send_flow(sock, "Benign")
            
            time.sleep(0.5) # Transmit every half second
    except KeyboardInterrupt:
        print("\n[*] Exiting Continuous Mode.")

def manual_mode(sock):
    while True:
        print("\n=== MANUAL ANOMALY INJECTION ===")
        print("1. Send Normal / Benign Traffic")
        print("2. Simulate DDoS Attack (High Packet Flood)")
        print("3. Simulate PortScan (Rapid Single Packets)")
        print("4. Simulate C&C Beacon (Long Duration, Low Packet)")
        print("5. Return to Main Menu")
        
        choice = input("Select an option [1-5]: ").strip()
        
        if choice == '1':
            send_flow(sock, "Benign")
            print("[✓] Sent Benign flow.")
        elif choice == '2':
            send_flow(sock, "DDoS")
            print("[🚨] Injected DDoS flow.")
        elif choice == '3':
            send_flow(sock, "PortScan")
            print("[🚨] Injected PortScan flow.")
        elif choice == '4':
            send_flow(sock, "C&C_Beacon")
            print("[🚨] Injected C&C Beacon flow.")
        elif choice == '5':
            break
        else:
            print("[!] Invalid selection.")

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((HOST, PORT))
    except ConnectionRefusedError:
        print("[!] Cannot connect. Ensure detector_server.py is running.")
        sys.exit(1)

    while True:
        print("\n" + "="*30)
        print(" NETWORK SIMULATION TERMINAL")
        print("="*30)
        print("1. Continuous Mode (Auto-stream with random anomalies)")
        print("2. Simulation Mode (Manual anomaly injection)")
        print("3. Exit")
        
        mode = input("Select Mode [1-3]: ").strip()
        
        if mode == '1':
            continuous_mode(sock)
        elif mode == '2':
            manual_mode(sock)
        elif mode == '3':
            print("Exiting...")
            break
        else:
            print("Invalid mode selected.")
            
    sock.close()

if __name__ == "__main__":
    main()
