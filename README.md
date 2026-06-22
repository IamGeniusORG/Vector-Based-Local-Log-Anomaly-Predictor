# Vector-Based Local Log Anomaly Predictor

This project implements a local, vector-based log anomaly predictor from scratch in Python. It is designed to act as an automated terminal log scanner that flags system outliers without relying on massive, slow external cloud APIs.

## Architecture

The system consists of two primary scripts:
1. **`log_generator.py`**: A dummy log generator that simulates an active system log stream, occasionally injecting anomalies (e.g., error messages, high numbers).
2. **`anomaly_predictor.py`**: The core engine that tails the active log file, converts text patterns into micro-feature matrices, and calculates statistical variance thresholds to detect anomalies in real-time.

## Step-by-Step Logic & Math Transformation

### 1. Live Text Stream Reader
The predictor uses a custom generator function (`follow`) that behaves like the Unix `tail -f` command. It continuously seeks new lines appended to the log file, ensuring real-time processing as the runtime metrics stream in.

### 2. Mathematical Transformation (Vectorization)
When a log line is read, it must be transformed into a numerical format that statistical algorithms can understand. This process is called "feature extraction" or "vectorization". 
Our micro-feature matrix consists of 3 distinct dimensions (a 3D vector):
* **Feature 1 (Text Length):** The absolute character length of the log line. Anomalous logs (like stack traces or verbose error details) often differ in length from standard operational logs.
* **Feature 2 (Keyword Frequency):** We scan the text against a predefined set of error keywords (e.g., "error", "fail", "timeout"). The count of these words forms the second dimension.
* **Feature 3 (Numeric Delta/Value):** System metrics often contain numbers (latency in ms, CPU %, memory usage). We parse out all numerical values using regular expressions and take the maximum value. Anomalies often present as huge spikes in these metrics.

*Example:*
Log line: `"ERROR: Connection timeout after 5000ms."`
Vector Transformation: `[41.0, 2.0, 5000.0]` -> (Length=41, Keywords=2 ("ERROR", "timeout"), Max Number=5000)

### 3. Rolling Z-Score Calculation (Anomaly Detection)
Instead of a simple Euclidean distance, we use a rolling Z-score calculation. This is highly effective because it naturally adapts to the shifting baseline of a running system.

* **Rolling Window:** The system maintains a history (a `collections.deque`) of the last *N* log vectors (default: 30).
* **Mean ($\mu$) and Standard Deviation ($\sigma$):** For every new vector that comes in, we calculate the average and the spread (standard deviation) of each feature dimension within the current window.
* **Z-Score Calculation:** The Z-score measures how many standard deviations a data point is from the mean. 
  $$ Z = \frac{|X - \mu|}{\sigma} $$
  Where $X$ is the new feature value, $\mu$ is the rolling mean, and $\sigma$ is the rolling standard deviation.
* **Thresholding:** If the Z-score for *any* feature exceeds our defined threshold (e.g., 2.5), it means the log line deviates significantly from recent normal behavior. The system immediately flags it and flashes a warning in the terminal.

## How to Run & Test

1. Open a terminal (Terminal 1) and start the dummy log generator. This will continuously write to `system.log`:
   ```bash
   python log_generator.py
   ```

2. Open a second terminal (Terminal 2) in the same directory and start the anomaly predictor. It will begin tailing the `system.log` file:
   ```bash
   python anomaly_predictor.py
   ```

3. Watch the terminal output! Terminal 1 will show you what it is generating, and Terminal 2 will silently consume normal logs but immediately flash red/yellow alerts whenever it detects an anomalous entry based on its real-time statistical baseline.
