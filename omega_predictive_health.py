"""
Predictive Health Analysis for The Gatekeeper
==============================================
Time-series forecasting and anomaly detection for system health

Features:
- 7-day disk usage forecasting (Prophet)
- CPU/Memory anomaly detection (Isolation Forest)
- Disk exhaustion prediction (3-day early warning)
- Health trend analysis
- Automated alerts

Requirements:
- prophet>=1.1.5
- scikit-learn>=1.4.0
- pandas>=2.1.0
- statsmodels>=0.14.1
- numpy>=1.24.0
"""

import os
import sys
import logging
import psutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import json

try:
    import pandas as pd
    import numpy as np
    from sklearn.ensemble import IsolationForest
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("Warning: scikit-learn/pandas not available for anomaly detection")

try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    print("Warning: Prophet not available for forecasting")


@dataclass
class HealthMetric:
    """Single health metric reading"""
    timestamp: datetime
    disk_usage_percent: float
    cpu_percent: float
    memory_percent: float
    disk_io_read_mb: float
    disk_io_write_mb: float

    def to_dict(self) -> dict:
        return {
            'timestamp': self.timestamp.isoformat(),
            'disk_usage_percent': self.disk_usage_percent,
            'cpu_percent': self.cpu_percent,
            'memory_percent': self.memory_percent,
            'disk_io_read_mb': self.disk_io_read_mb,
            'disk_io_write_mb': self.disk_io_write_mb
        }


@dataclass
class DiskForecast:
    """Disk usage forecast"""
    current_usage: float
    forecast_7d: float
    days_until_full: Optional[int]
    trend: str  # 'increasing', 'stable', 'decreasing'
    prediction_dates: List[datetime]
    prediction_values: List[float]

    def to_dict(self) -> dict:
        return {
            'current_usage': self.current_usage,
            'forecast_7d': self.forecast_7d,
            'days_until_full': self.days_until_full,
            'trend': self.trend,
            'predictions': [
                {'date': d.isoformat(), 'value': v}
                for d, v in zip(self.prediction_dates, self.prediction_values)
            ]
        }


@dataclass
class Anomaly:
    """Detected anomaly"""
    timestamp: datetime
    metric_name: str
    value: float
    anomaly_score: float
    severity: str  # 'low', 'medium', 'high'

    def to_dict(self) -> dict:
        return {
            'timestamp': self.timestamp.isoformat(),
            'metric_name': self.metric_name,
            'value': self.value,
            'anomaly_score': self.anomaly_score,
            'severity': self.severity
        }


class PredictiveHealthAnalyzer:
    """
    Predictive health analysis using Prophet and Isolation Forest

    Usage:
        analyzer = PredictiveHealthAnalyzer()
        analyzer.collect_metrics()  # Collect current metrics
        forecast = analyzer.forecast_disk_usage(days=7)
        anomalies = analyzer.detect_anomalies()
    """

    def __init__(self, history_file: str = "health_metrics_history.json"):
        """
        Initialize predictive health analyzer

        Args:
            history_file: File to store historical metrics
        """
        self.logger = logging.getLogger(__name__)
        self.history_file = Path(history_file)
        self.metrics_history: List[HealthMetric] = []
        self.anomalies: List[Anomaly] = []

        # Load existing history
        self._load_history()

        # Anomaly detector (trained on historical data)
        self.anomaly_detector: Optional[IsolationForest] = None
        if SKLEARN_AVAILABLE and len(self.metrics_history) > 10:
            self._train_anomaly_detector()

    def collect_metrics(self, path: str = "C:\\") -> HealthMetric:
        """
        Collect current system health metrics

        Args:
            path: Disk path to monitor

        Returns:
            HealthMetric with current readings
        """
        try:
            # Disk usage
            disk = psutil.disk_usage(path)
            disk_usage_percent = disk.percent

            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)

            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent

            # Disk I/O
            disk_io = psutil.disk_io_counters()
            disk_io_read_mb = disk_io.read_bytes / (1024 * 1024)
            disk_io_write_mb = disk_io.write_bytes / (1024 * 1024)

            metric = HealthMetric(
                timestamp=datetime.now(),
                disk_usage_percent=disk_usage_percent,
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                disk_io_read_mb=disk_io_read_mb,
                disk_io_write_mb=disk_io_write_mb
            )

            # Add to history
            self.metrics_history.append(metric)

            # Keep only last 30 days
            cutoff = datetime.now() - timedelta(days=30)
            self.metrics_history = [
                m for m in self.metrics_history
                if m.timestamp > cutoff
            ]

            # Save history
            self._save_history()

            self.logger.info(f"Collected metrics: Disk={disk_usage_percent:.1f}% CPU={cpu_percent:.1f}% Memory={memory_percent:.1f}%")

            return metric

        except Exception as e:
            self.logger.error(f"Failed to collect metrics: {e}")
            raise

    def forecast_disk_usage(self, days: int = 7) -> Optional[DiskForecast]:
        """
        Forecast disk usage using Prophet

        Args:
            days: Number of days to forecast

        Returns:
            DiskForecast or None if insufficient data
        """
        if not PROPHET_AVAILABLE:
            self.logger.warning("Prophet not available for forecasting")
            return None

        if len(self.metrics_history) < 7:
            self.logger.warning("Insufficient historical data (need at least 7 data points)")
            return None

        try:
            # Prepare data for Prophet
            df = pd.DataFrame([
                {
                    'ds': m.timestamp,
                    'y': m.disk_usage_percent
                }
                for m in self.metrics_history
            ])

            # Train Prophet model
            model = Prophet(
                daily_seasonality=True,
                yearly_seasonality=False,
                weekly_seasonality=True if len(df) > 14 else False
            )

            # Suppress Prophet output
            with open(os.devnull, 'w') as devnull:
                old_stdout = sys.stdout
                sys.stdout = devnull
                model.fit(df)
                sys.stdout = old_stdout

            # Make forecast
            future = model.make_future_dataframe(periods=days)
            forecast = model.predict(future)

            # Get current and predicted values
            current_usage = self.metrics_history[-1].disk_usage_percent
            forecast_7d = forecast.iloc[-1]['yhat']

            # Calculate trend
            recent_avg = np.mean([m.disk_usage_percent for m in self.metrics_history[-7:]])
            if forecast_7d > recent_avg + 5:
                trend = 'increasing'
            elif forecast_7d < recent_avg - 5:
                trend = 'decreasing'
            else:
                trend = 'stable'

            # Estimate days until full (if increasing)
            days_until_full = None
            if trend == 'increasing' and forecast_7d < 100:
                # Linear extrapolation
                daily_increase = (forecast_7d - current_usage) / days
                if daily_increase > 0:
                    remaining_percent = 100 - current_usage
                    days_until_full = int(remaining_percent / daily_increase)

            # Get prediction dates and values
            prediction_dates = forecast['ds'].tail(days).tolist()
            prediction_values = forecast['yhat'].tail(days).tolist()

            result = DiskForecast(
                current_usage=current_usage,
                forecast_7d=forecast_7d,
                days_until_full=days_until_full,
                trend=trend,
                prediction_dates=prediction_dates,
                prediction_values=prediction_values
            )

            self.logger.info(f"Forecast: Current={current_usage:.1f}% → 7-day={forecast_7d:.1f}% Trend={trend}")

            return result

        except Exception as e:
            self.logger.error(f"Forecasting failed: {e}")
            return None

    def detect_anomalies(self, window: int = 20) -> List[Anomaly]:
        """
        Detect anomalies in recent metrics using Isolation Forest

        Args:
            window: Number of recent metrics to analyze

        Returns:
            List of detected anomalies
        """
        if not SKLEARN_AVAILABLE:
            self.logger.warning("scikit-learn not available for anomaly detection")
            return []

        if len(self.metrics_history) < window:
            self.logger.warning(f"Insufficient data for anomaly detection (need {window}, have {len(self.metrics_history)})")
            return []

        try:
            # Retrain detector if needed
            if self.anomaly_detector is None:
                self._train_anomaly_detector()

            # Get recent metrics
            recent = self.metrics_history[-window:]

            # Prepare features
            X = np.array([
                [
                    m.cpu_percent,
                    m.memory_percent,
                    m.disk_usage_percent
                ]
                for m in recent
            ])

            # Predict anomalies
            predictions = self.anomaly_detector.predict(X)
            scores = self.anomaly_detector.score_samples(X)

            # Find anomalies (prediction == -1)
            anomalies = []
            for i, (pred, score) in enumerate(zip(predictions, scores)):
                if pred == -1:
                    metric = recent[i]

                    # Determine which metric is anomalous
                    cpu_zscore = abs((metric.cpu_percent - np.mean(X[:, 0])) / (np.std(X[:, 0]) + 1e-6))
                    mem_zscore = abs((metric.memory_percent - np.mean(X[:, 1])) / (np.std(X[:, 1]) + 1e-6))
                    disk_zscore = abs((metric.disk_usage_percent - np.mean(X[:, 2])) / (np.std(X[:, 2]) + 1e-6))

                    zscores = {
                        'cpu': (cpu_zscore, metric.cpu_percent),
                        'memory': (mem_zscore, metric.memory_percent),
                        'disk': (disk_zscore, metric.disk_usage_percent)
                    }

                    # Get most anomalous metric
                    anomalous_metric = max(zscores.items(), key=lambda x: x[1][0])
                    metric_name, (zscore, value) = anomalous_metric

                    # Determine severity
                    if zscore > 3:
                        severity = 'high'
                    elif zscore > 2:
                        severity = 'medium'
                    else:
                        severity = 'low'

                    anomaly = Anomaly(
                        timestamp=metric.timestamp,
                        metric_name=metric_name,
                        value=value,
                        anomaly_score=float(score),
                        severity=severity
                    )

                    anomalies.append(anomaly)
                    self.anomalies.append(anomaly)

            if anomalies:
                self.logger.warning(f"Detected {len(anomalies)} anomalies")
                for a in anomalies:
                    self.logger.warning(f"  - {a.metric_name}={a.value:.1f}% (severity: {a.severity})")

            return anomalies

        except Exception as e:
            self.logger.error(f"Anomaly detection failed: {e}")
            return []

    def get_health_summary(self) -> Dict:
        """Get overall health summary"""
        if not self.metrics_history:
            return {
                'status': 'unknown',
                'metrics_collected': 0
            }

        latest = self.metrics_history[-1]

        # Determine status
        if latest.disk_usage_percent > 90 or latest.cpu_percent > 90 or latest.memory_percent > 90:
            status = 'critical'
        elif latest.disk_usage_percent > 80 or latest.cpu_percent > 80 or latest.memory_percent > 80:
            status = 'warning'
        else:
            status = 'healthy'

        # Get forecast
        forecast = self.forecast_disk_usage(days=7)

        # Recent anomalies
        recent_anomalies = [a for a in self.anomalies if a.timestamp > datetime.now() - timedelta(hours=24)]

        return {
            'status': status,
            'metrics_collected': len(self.metrics_history),
            'latest_metrics': {
                'disk_usage': latest.disk_usage_percent,
                'cpu': latest.cpu_percent,
                'memory': latest.memory_percent,
                'timestamp': latest.timestamp.isoformat()
            },
            'forecast': forecast.to_dict() if forecast else None,
            'recent_anomalies': len(recent_anomalies),
            'days_until_disk_full': forecast.days_until_full if forecast else None
        }

    def should_alert(self) -> Tuple[bool, str]:
        """
        Check if alert should be triggered

        Returns:
            (should_alert, reason)
        """
        if not self.metrics_history:
            return False, ""

        latest = self.metrics_history[-1]

        # Critical thresholds
        if latest.disk_usage_percent > 95:
            return True, f"Critical: Disk usage at {latest.disk_usage_percent:.1f}%"

        if latest.cpu_percent > 95:
            return True, f"Critical: CPU usage at {latest.cpu_percent:.1f}%"

        if latest.memory_percent > 95:
            return True, f"Critical: Memory usage at {latest.memory_percent:.1f}%"

        # Forecast-based alert
        forecast = self.forecast_disk_usage(days=7)
        if forecast and forecast.days_until_full and forecast.days_until_full <= 3:
            return True, f"Warning: Disk will be full in {forecast.days_until_full} days"

        # Anomaly-based alert
        recent_anomalies = [
            a for a in self.anomalies
            if a.timestamp > datetime.now() - timedelta(hours=1)
            and a.severity in ['high', 'critical']
        ]
        if len(recent_anomalies) >= 3:
            return True, f"Warning: {len(recent_anomalies)} anomalies detected in last hour"

        return False, ""

    def _train_anomaly_detector(self):
        """Train Isolation Forest on historical data"""
        if not SKLEARN_AVAILABLE or len(self.metrics_history) < 10:
            return

        try:
            X = np.array([
                [m.cpu_percent, m.memory_percent, m.disk_usage_percent]
                for m in self.metrics_history
            ])

            self.anomaly_detector = IsolationForest(
                contamination=0.1,  # Expect 10% anomalies
                random_state=42
            )
            self.anomaly_detector.fit(X)

            self.logger.info("Trained anomaly detector on historical data")

        except Exception as e:
            self.logger.error(f"Failed to train anomaly detector: {e}")

    def _load_history(self):
        """Load metrics history from file"""
        if not self.history_file.exists():
            return

        try:
            with open(self.history_file) as f:
                data = json.load(f)

            self.metrics_history = [
                HealthMetric(
                    timestamp=datetime.fromisoformat(m['timestamp']),
                    disk_usage_percent=m['disk_usage_percent'],
                    cpu_percent=m['cpu_percent'],
                    memory_percent=m['memory_percent'],
                    disk_io_read_mb=m['disk_io_read_mb'],
                    disk_io_write_mb=m['disk_io_write_mb']
                )
                for m in data.get('metrics', [])
            ]

            self.logger.info(f"Loaded {len(self.metrics_history)} historical metrics")

        except Exception as e:
            self.logger.error(f"Failed to load history: {e}")

    def _save_history(self):
        """Save metrics history to file"""
        try:
            data = {
                'metrics': [m.to_dict() for m in self.metrics_history],
                'last_updated': datetime.now().isoformat()
            }

            with open(self.history_file, 'w') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            self.logger.error(f"Failed to save history: {e}")


# Global instance
_analyzer_instance: Optional[PredictiveHealthAnalyzer] = None


def get_health_analyzer() -> PredictiveHealthAnalyzer:
    """Get or create global health analyzer"""
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = PredictiveHealthAnalyzer()
    return _analyzer_instance


if __name__ == "__main__":
    # Demo/test mode
    import argparse

    parser = argparse.ArgumentParser(description="Predictive Health Analysis Demo")
    parser.add_argument('--collect', action='store_true', help='Collect current metrics')
    parser.add_argument('--forecast', action='store_true', help='Show disk usage forecast')
    parser.add_argument('--anomalies', action='store_true', help='Detect anomalies')
    parser.add_argument('--summary', action='store_true', help='Show health summary')
    parser.add_argument('--days', type=int, default=7, help='Forecast days (default: 7)')
    args = parser.parse_args()

    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    analyzer = get_health_analyzer()

    print("\n📊 Predictive Health Analyzer")
    print(f"Historical metrics: {len(analyzer.metrics_history)}")

    if args.collect:
        print("\n📈 Collecting current metrics...")
        metric = analyzer.collect_metrics()
        print(f"  Disk: {metric.disk_usage_percent:.1f}%")
        print(f"  CPU: {metric.cpu_percent:.1f}%")
        print(f"  Memory: {metric.memory_percent:.1f}%")

    if args.forecast:
        print(f"\n🔮 Forecasting disk usage ({args.days} days)...")
        forecast = analyzer.forecast_disk_usage(days=args.days)
        if forecast:
            print(f"  Current: {forecast.current_usage:.1f}%")
            print(f"  {args.days}-day forecast: {forecast.forecast_7d:.1f}%")
            print(f"  Trend: {forecast.trend}")
            if forecast.days_until_full:
                print(f"  ⚠️ Disk full in: {forecast.days_until_full} days")

    if args.anomalies:
        print("\n🚨 Detecting anomalies...")
        anomalies = analyzer.detect_anomalies()
        if anomalies:
            for a in anomalies:
                print(f"  {a.severity.upper()}: {a.metric_name}={a.value:.1f}% at {a.timestamp.strftime('%Y-%m-%d %H:%M')}")
        else:
            print("  No anomalies detected")

    if args.summary:
        print("\n📋 Health Summary:")
        summary = analyzer.get_health_summary()
        print(f"  Status: {summary['status'].upper()}")
        print(f"  Metrics collected: {summary['metrics_collected']}")
        if summary.get('latest_metrics'):
            print(f"  Latest:")
            print(f"    Disk: {summary['latest_metrics']['disk_usage']:.1f}%")
            print(f"    CPU: {summary['latest_metrics']['cpu']:.1f}%")
            print(f"    Memory: {summary['latest_metrics']['memory']:.1f}%")
        if summary.get('days_until_disk_full'):
            print(f"  ⚠️ Disk full in: {summary['days_until_disk_full']} days")

        should_alert, reason = analyzer.should_alert()
        if should_alert:
            print(f"\n🚨 ALERT: {reason}")

    if not any([args.collect, args.forecast, args.anomalies, args.summary]):
        print("\nUsage:")
        print("  py -3.11 omega_predictive_health.py --collect --summary")
        print("  py -3.11 omega_predictive_health.py --forecast --days 7")
        print("  py -3.11 omega_predictive_health.py --anomalies")
