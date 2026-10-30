# Network Anomaly Detection using NS-3 Simulation

A Network Programming (NWP) AAT project that detects malicious network flows in
real time. A machine-learning model trained on the **IoT-23** dataset classifies
flows streamed over TCP sockets, and attacks (DDoS, port scan, C&C beacon) can be
injected on demand to test it. An NS-3 control channel is included for driving
attacks from a simulation.

## How It Works

```
 stream_feeder.py ──┐                         ┌─> console verdict (BENIGN / MALICIOUS)
 (replays dataset)  ├─ JSON flows (TCP :9999) ─> detector_server.py ─┤
 interactive_client.py ┘                       (ML model)           └─> log.txt (attacks)

 attack_controller.py ── UDP "DDOS"/"PORTSCAN" (:9998) ──> NS-3 simulation
```

1. **Detector server** loads the trained model and feature encoders, listens on
   `127.0.0.1:9999`, and classifies each newline-delimited JSON flow.
   Flows predicted as malicious are written to `log.txt`.
2. **Traffic sources** feed the detector:
   - `stream_feeder.py` replays `dataset13.csv` (2,110 IoT-23 flows, shuffled) at 20 flows/sec.
   - `interactive_client.py` generates synthetic flows, either continuous (about 10% random anomalies)
     or manual injection of **Benign, DDoS, PortScan, C&C Beacon** traffic.
3. **Attack controller** (`attack_controller.py`) sends `DDOS` / `PORTSCAN` commands
   over UDP port 9998, intended for a listening NS-3 simulation.

## Repository Structure

| Path | Description |
|------|-------------|
| `ml_detector/detector_server.py` | Real-time detection server (socket + model inference + logging) |
| `ml_detector/stream_feeder.py` | Streams the IoT-23 CSV to the detector |
| `ml_detector/interactive_client.py` | Menu-driven synthetic traffic and anomaly injector |
| `ml_detector/attack_controller.py` | UDP command client for NS-3 attack injection |
| `ml_detector/iot23_rf_a100.joblib` | Trained classifier used by the server |
| `ml_detector/model_artifacts.joblib` | Feature list and categorical encoders |
| `ml_detector/network_anomaly_model.pkl` | Alternate scikit-learn pipeline (about 26 MB, not used by the server) |
| `ml_detector/dataset13.csv` | IoT-23 flow sample (Zeek `conn.log` format) |
| `ml_detector/log.txt` | Sample output log of detected attacks |
| `scratch/` | NS-3 `scratch` directory (see note below) |

## Features Used

`proto, service, duration, orig_bytes, resp_bytes, conn_state, local_orig, local_resp,
missed_bytes, history, orig_pkts, orig_ip_bytes, resp_pkts, resp_ip_bytes`
(categorical fields are label-encoded; unseen values default to 0).

## Setup & Usage

**Requirements:** Python 3.8+, `pandas`, `joblib`, `scikit-learn`, `xgboost`
(the saved model needs XGBoost to load), and optionally ns-3.

```bash
pip install pandas joblib scikit-learn xgboost
cd ml_detector

# Terminal 1: start the detector
python detector_server.py

# Terminal 2: send traffic (choose one)
python stream_feeder.py          # replay the IoT-23 dataset
python interactive_client.py     # synthetic / manual attacks

# Optional: trigger attacks in a running NS-3 simulation
python attack_controller.py
```

Detected attacks are appended to `ml_detector/log.txt`.

## Notes & Limitations

- **The NS-3 simulation is not included.** `scratch/` contains only the stock ns-3
  template files (`scratch-simulator.cc`, `subdir/`, `nested-subdir/`). The UDP
  listener on port 9998 that `attack_controller.py` talks to, and any NS-3-to-detector
  flow export, still need to be added.
- The detector labels flows only as benign or malicious; `log.txt` records the
  attack name as `Unlabeled_Threat` unless the sender includes an `attack_type` field.
- `interactive_client.py` flows are hand-crafted approximations of IoT-23 attack
  signatures, not real captured traffic.
- `stream_feeder.py` and `detector_server.py` use relative paths, so run them from `ml_detector/`.
- The model files are named `rf` (random forest) but require XGBoost to unpickle.
  Pin the library versions used for training for reproducibility.
- Model training code and evaluation metrics (accuracy, precision, recall) are not in the repo.

## Authors

Yatharth Singh, Thilak K, Vinayak Sunil Rodd. Thanmay K H