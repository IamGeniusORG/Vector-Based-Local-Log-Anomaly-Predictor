import time
import re
import math
import collections
import argparse
import os
import sys
from typing import List, Tuple

# ANSI escape codes for terminal colors
COLORS = {
    "RED": '\033[91m',
    "YELLOW": '\033[93m',
    "RESET": '\033[0m',
    "CYAN": '\033[96m',
    "GREEN": '\033[92m',
    "MAGENTA": '\033[95m'
}

ERROR_KEYWORDS = {'error', 'fail', 'exception', 'timeout', 'critical', 'fatal', 'leak', 'unreachable', 'invalid'}

SEVERITY_MAP = {
    'DEBUG': 0.0,
    'INFO': 0.0,
    'WARNING': 1.0,
    'ERROR': 2.0,
    'CRITICAL': 3.0,
    'FATAL': 3.0,
    'EXCEPTION': 3.0
}

class Vectorizer:
    @staticmethod
    def extract_features(log_line: str) -> List[float]:
        """
        Converts text patterns into a 4-dimensional micro-feature matrix.
        """
        # 1. Strip the timestamp bracket [YYYY-MM-DD...] to avoid parsing it as a metric
        content_match = re.search(r'\]\s*(.*)', log_line)
        content = content_match.group(1) if content_match else log_line
        content_lower = content.lower()
        
        # Feature 1: Log line length (of the actual content, ignoring timestamp)
        length = float(len(content))
        
        # Feature 2: Error keyword count
        keyword_count = sum(1 for word in ERROR_KEYWORDS if word in content_lower)
        
        # Feature 3: Severity Level Extraction
        severity_score = 0.0
        for level, score in SEVERITY_MAP.items():
            if level in log_line:  # Check original line for uppercase severities
                severity_score = max(severity_score, score)
                
        # Feature 4: Max Numeric Metric (ignores timestamp since we stripped it)
        # Removed \b boundaries to properly catch numbers attached to units (e.g., 5831ms, 105MB/s)
        numbers = re.findall(r'\d+(?:\.\d+)?', content)
        max_num = max([float(n) for n in numbers]) if numbers else 0.0
        
        return [length, float(keyword_count), severity_score, max_num]


class AnomalyDetector:
    def __init__(self, window_size: int, threshold: float, min_baseline: int):
        self.window_size = window_size
        self.threshold = threshold
        self.min_baseline = min_baseline
        self.history = collections.deque(maxlen=window_size)
        
    def _calculate_mean_std(self, feature_idx: int) -> Tuple[float, float]:
        """Calculates mean and standard deviation for a specific feature in the rolling window."""
        values = [vec[feature_idx] for vec in self.history]
        n = len(values)
        if n < 2:
            return values[0] if n == 1 else 0.0, 0.0
            
        mean = sum(values) / n
        variance = sum((x - mean) ** 2 for x in values) / (n - 1)
        std_dev = math.sqrt(variance)
        return mean, std_dev

    def process_vector(self, vector: List[float]) -> Tuple[bool, List[float], List[str]]:
        """
        Calculates Z-scores for the incoming vector against the rolling baseline.
        Returns: (is_anomalous, z_scores, triggered_reasons)
        """
        # Not enough data for a meaningful baseline yet
        if len(self.history) < self.min_baseline:
            self.history.append(vector)
            return False, [0.0] * len(vector), []
            
        z_scores = []
        is_anomalous = False
        triggered_reasons = []
        feature_names = ["Length", "Keywords", "Severity", "Metrics"]
        
        # Calculate Z-score for each feature
        for i, val in enumerate(vector):
            mean, std = self._calculate_mean_std(i)
            if std > 0:
                z_score = abs((val - mean) / std)
            else:
                # If std is 0 (constant baseline) and we deviate, it's highly anomalous
                z_score = 0.0 if val == mean else self.threshold + 1.0 
                
            z_scores.append(z_score)
            if z_score > self.threshold:
                is_anomalous = True
                triggered_reasons.append(f"{feature_names[i]} (Z={z_score:.2f})")
                
        # Add the new vector to history (rolling window)
        self.history.append(vector)
        return is_anomalous, z_scores, triggered_reasons


def follow(file):
    """Generator that yields new lines in a file, starting from the beginning."""
    file.seek(0, 0)
    while True:
        line = file.readline()
        if not line:
            time.sleep(0.1)
            continue
        yield line


def main():
    parser = argparse.ArgumentParser(description="Advanced Vector-Based Local Log Anomaly Predictor")
    parser.add_argument("--log", type=str, default="system.log", help="Path to the log file to tail")
    parser.add_argument("--window", type=int, default=30, help="Rolling window size for baseline (default: 30)")
    parser.add_argument("--threshold", type=float, default=2.5, help="Z-score threshold for anomalies (default: 2.5)")
    parser.add_argument("--min-baseline", type=int, default=10, help="Minimum logs needed before alerting (default: 10)")
    args = parser.parse_args()

    c_cyan = COLORS['CYAN']
    c_reset = COLORS['RESET']
    c_green = COLORS['GREEN']
    c_red = COLORS['RED']
    c_yellow = COLORS['YELLOW']
    c_magenta = COLORS['MAGENTA']

    print(f"{c_cyan}=================================================={c_reset}")
    print(f"{c_cyan}  Advanced Vector-Based Local Log Predictor      {c_reset}")
    print(f"{c_cyan}=================================================={c_reset}")
    print(f"Configuration: Window={args.window}, Threshold={args.threshold}, Min Baseline={args.min_baseline}")
    print(f"Waiting for live logs in '{args.log}'...")
    
    vectorizer = Vectorizer()
    detector = AnomalyDetector(window_size=args.window, threshold=args.threshold, min_baseline=args.min_baseline)
    
    try:
        while not os.path.exists(args.log):
            time.sleep(1)
            
        with open(args.log, 'r') as log_file:
            print(f"{c_green}Log file found! Tailing stream & building baseline...{c_reset}\n")
            loglines = follow(log_file)
            
            for line in loglines:
                line = line.strip()
                if not line:
                    continue
                    
                vector = vectorizer.extract_features(line)
                is_anomaly, z_scores, reasons = detector.process_vector(vector)
                
                if is_anomaly:
                    z_str = ", ".join([f"{z:.2f}" for z in z_scores])
                    reasons_str = ", ".join(reasons)
                    print(f"{c_red}[ANOMALY DETECTED]{c_reset} {c_magenta}Triggers: {reasons_str}{c_reset}")
                    print(f"{c_yellow}Log Line:{c_reset} {line}")
                    print(f"{c_cyan}Vector [Len, Keyw, Sev, Num]:{c_reset} {vector}")
                    print(f"{c_cyan}Z-Scores:{c_reset} [{z_str}]\n")
                
    except KeyboardInterrupt:
        print(f"\n{c_yellow}Predictor stopped gracefully.{c_reset}")
        sys.exit(0)

if __name__ == "__main__":
    main()
