import socket
import json
import joblib
import pandas as pd
import datetime

MODEL_PATH = "iot23_rf_a100.joblib"
META_PATH = "model_artifacts.joblib"
HOST = "127.0.0.1"
PORT = 9999
LOG_FILE = "log.txt"
open(LOG_FILE, "a").close()

print(f"[+] Loading model from '{MODEL_PATH}'...")
model = joblib.load(MODEL_PATH)
if hasattr(model, "set_params"):
    try:
        model.set_params(device="cpu")
    except Exception:
        pass

meta = joblib.load(META_PATH)
feature_names = meta['features']
encoders = meta.get('encoders', {})

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen(5)
print(f"[+] Detector listening on {HOST}:{PORT}")
print(f"[+] Anomalies will be logged to {LOG_FILE}\n")

while True:
    conn, addr = server.accept()
    buffer = ""
    while True:
        data = conn.recv(8192).decode('utf-8')
        if not data:
            break
        buffer += data
        
        while "\n" in buffer:
            line, buffer = buffer.split("\n", 1)
            line = line.strip()
            if not line:
                continue
            
            try:
                flow = json.loads(line)
                row = {}
                for col in feature_names:
                    val = flow.get(col, 0)
                    if col in encoders:
                        enc_dict = encoders[col]
                        str_val = str(val)
                        # Safely fetch the mapped integer, defaulting to 0 for unseen live data
                        row[col] = enc_dict.get(str_val, 0)
                    else:
                        row[col] = float(val) if val not in ['-', '', None] else 0.0

                df_sample = pd.DataFrame([row])[feature_names]
                
                # The ML Model autonomously evaluates the raw flow features here
                pred = model.predict(df_sample)[0]
                
                if pred == 1:
                    status = "🚨 MALICIOUS"
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    attack_name = flow.get('attack_type', 'Unlabeled_Threat')
                    log_entry = f"[{timestamp}] ATTACK: {attack_name} | Port: {flow.get('id.orig_p')}->{flow.get('id.resp_p')} | Pkts: {flow.get('orig_pkts')}\n"
                    
                    with open(LOG_FILE, "a") as f:
                        f.write(log_entry)
                else:
                    status = "✅ BENIGN"

                # Print the model's independent verdict
                print(f"[FLOW] Verdict: {status} | Port: {flow.get('id.orig_p', '?')}->{flow.get('id.resp_p', '?')} | Pkts: {flow.get('orig_pkts', 0)}")

            except Exception as err:
                pass
    conn.close()
