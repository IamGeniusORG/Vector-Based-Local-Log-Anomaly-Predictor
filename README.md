# 🎯 Vector-Based Local Log Anomaly Predictor

An entirely local, machine-learning-powered terminal scanner that autonomously flags system anomalies in real-time. It uses pure mathematics (Micro-Feature Vectorization & Rolling Z-Scores) to detect outliers in log streams **without** relying on massive, slow, or expensive external Cloud APIs.

---

## 🤔 What is this?
Imagine you have a server generating thousands of logs per minute. Instead of paying for a cloud service to monitor these logs or manually reading them yourself, this script acts as an autonomous "Security Guard". 

It silently reads your streaming logs, uses math to figure out what a "normal" log looks like, and instantly flashes a warning in your terminal the second something behaves unusually. 

### 🌟 Key Features
* **100% Local & Offline**: No data leaves your machine. Perfect for secure environments or Edge/IoT devices.
* **No Hardcoded Rules**: You don't have to tell it what an "error" is. It learns the baseline dynamically using Z-Scores.
* **Zero Latency**: Written in pure Python using standard libraries. It processes logs the millisecond they are generated.
* **Highly Configurable**: Easily tune the rolling window size and anomaly threshold via the command line.

---

## 🧮 How It Works (The Math Made Simple)

Machine learning algorithms can't read English, so we have to convert the text logs into numbers. This is called **Vectorization**.

Every time a log line is generated, our script converts it into a **4-Dimensional Vector** `[Length, Keywords, Severity, Metrics]`:

1. **Length:** The raw character length of the log. *(Errors and stack traces are usually much longer than normal heartbeat logs).*
2. **Keywords:** The number of scary words found *(e.g., "timeout", "leak", "failure")*.
3. **Severity:** A mapped score based on logging levels. *(`INFO` = 0, `WARNING` = 1, `ERROR` = 2, `FATAL` = 3).*
4. **Metrics:** It dynamically extracts the largest number found in the log *(like `140MB/s` or `5831ms`)*.

### 💡 A Simple Example
Let's say the system is running normally. The script watches the logs and learns that "normal" looks like this:
> `INFO: Disk read speed 105MB/s`  👉 Vector: `[29.0, 0.0, 0.0, 105.0]`

Suddenly, an anomaly occurs in the system:
> `FATAL: Disk failure on /dev/sda1. I/O wait 5831ms` 👉 Vector: `[49.0, 2.0, 3.0, 5831.0]`

The script compares this new vector to the recent rolling average using a **Z-Score** (Standard Deviation). Because all 4 numbers violently spike compared to the baseline, it instantly triggers an alarm!

---

## 🚀 Getting Started

You can test this entire pipeline locally in seconds. The project comes with a Dummy Log Generator to simulate an active server.

### 1. Clone the Repository
First, download the project to your local machine and navigate into the folder:
```bash
git clone https://github.com/IamGeniusORG/Vector-Based-Local-Log-Anomaly-Predictor.git
cd Vector-Based-Local-Log-Anomaly-Predictor
```

### 2. Open Terminal A (The Server)
In your first terminal window, run the generator to simulate a system generating normal logs with occasional anomalies:
```bash
python log_generator.py
```

### 3. Open Terminal B (The Predictor)
Open a **second, completely separate terminal window**, navigate to the same folder, and run the predictor to tail the logs and watch the magic happen:
```bash
cd Vector-Based-Local-Log-Anomaly-Predictor
python anomaly_predictor.py
```
*(Optional: You can tune the engine using arguments: `python anomaly_predictor.py --window 50 --threshold 3.0`)*

---

## 📸 Example Output
When the predictor catches an anomaly, it will explicitly isolate **why** it flagged it by pointing out exactly which features deviated from the baseline:

```text
[ANOMALY DETECTED] Triggers: Length (Z=7.81), Keywords (Z=3.50), Severity (Z=3.50), Metrics (Z=463.25)
Log Line: EXCEPTION: Null pointer dereference in module auth_service. Code 23806.
Vector [Len, Keyw, Sev, Num]: [71.0, 1.0, 3.0, 23806.0]
Z-Scores: [7.81, 3.50, 3.50, 463.25]
```
