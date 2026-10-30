import socket
import time
import json
import pandas as pd

CSV_PATH = "dataset13.csv"
HOST = "127.0.0.1"
PORT = 9999
STREAM_INTERVAL_SEC = 0.05

print(f"[+] Reading unlabeled dataset from '{CSV_PATH}'...")
df = pd.read_csv(CSV_PATH, sep=None, engine='python', na_values=['-', '(empty)'])
df.columns = df.columns.str.strip()

# Shuffle the dataset
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

print(f"[+] Dataset loaded. Total raw flows to stream: {len(df)}")

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))
print(f"[+] Connected to ML detector at {HOST}:{PORT}. Streaming flows...")

try:
    for idx, row in df.iterrows():
        flow_data = row.to_dict()
        
        # Stream only the raw features without appending any ground_truth keys
        payload = json.dumps(flow_data) + "\n"
        sock.sendall(payload.encode('utf-8'))
        time.sleep(STREAM_INTERVAL_SEC)
except KeyboardInterrupt:
    print("\n[*] Stream stopped by user.")
finally:
    sock.close()
