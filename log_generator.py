import time
import random
import datetime
import os

LOG_FILE = "system.log"

NORMAL_MESSAGES = [
    "INFO: System temperature is {num}C",
    "INFO: CPU utilization at {num}%",
    "DEBUG: Cache refreshed in {num}ms",
    "INFO: Active connections: {num}",
    "INFO: Disk read speed {num}MB/s",
    "DEBUG: Worker thread {num} spawned successfully",
    "INFO: Memory footprint steady at {num}MB"
]

ANOMALY_MESSAGES = [
    "ERROR: Connection timeout after {num}ms. Service unreachable.",
    "CRITICAL: Memory leak detected! Usage at {num}%",
    "FATAL: Disk failure on /dev/sda1. I/O wait {num}ms",
    "ERROR: Authentication failed for user root. Invalid token {num}.",
    "EXCEPTION: Null pointer dereference in module auth_service. Code {num}."
]

def generate_log():
    # Ensure file is clear on start
    with open(LOG_FILE, "w") as f:
        f.write(f"[{datetime.datetime.now().isoformat()}] INFO: Log generation started.\n")

    print(f"Starting dummy log generator. Writing to '{LOG_FILE}'...")
    print("Press Ctrl+C to stop.\n")

    with open(LOG_FILE, "a") as f:
        while True:
            timestamp = datetime.datetime.now().isoformat()
            
            # 5% chance of generating an anomaly
            is_anomaly = random.random() < 0.05
            
            if is_anomaly:
                template = random.choice(ANOMALY_MESSAGES)
                # Anomalies often involve extreme numeric values
                num = random.randint(5000, 25000)
            else:
                template = random.choice(NORMAL_MESSAGES)
                # Normal operations have smaller numeric metrics
                num = random.randint(10, 150)
                
            log_line = f"[{timestamp}] {template.format(num=num)}\n"
            f.write(log_line)
            f.flush()
            
            # Output to console for visibility
            if is_anomaly:
                print(f"[GENERATED ANOMALY] {log_line.strip()}")
            else:
                print(f"[GENERATED NORMAL]  {log_line.strip()}")
            
            # Sleep to simulate a real-time log stream
            time.sleep(random.uniform(0.1, 1.0))

if __name__ == "__main__":
    try:
        generate_log()
    except KeyboardInterrupt:
        print("\nLog generator stopped gracefully.")
