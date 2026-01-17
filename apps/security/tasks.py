"""
Celery tasks for IP Tracking.

Task 4: Anomaly detection to flag suspicious IPs using basic machine learning.
"""
import logging
from celery import shared_task
from django.utils import timezone
from django.db.models import Count, Q
from datetime import timedelta

from .models import RequestLog, SuspiciousIP

logger = logging.getLogger(__name__)

# ML imports (optional - will fail gracefully if not installed)
try:
    import numpy as np
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    logger.warning("scikit-learn or numpy not available. ML-based anomaly detection will be disabled.")


@shared_task
def detect_suspicious_ips():
    """
    Task 4: Detect suspicious IPs using basic machine learning (Isolation Forest)
    combined with rule-based detection:
    - ML-based anomaly detection using scikit-learn
    - IPs exceeding 100 requests/hour
    - IPs accessing sensitive paths (e.g., /admin, /login)
    
    This task runs hourly via Celery Beat.
    """
    one_hour_ago = timezone.now() - timedelta(hours=1)
    
    # Get all requests from the last hour
    recent_logs = RequestLog.objects.filter(timestamp__gte=one_hour_ago)
    
    if recent_logs.count() == 0:
        logger.info("No recent logs to analyze")
        return "No logs to analyze"
    
    flagged_count = 0
    
    # Rule-based detection: High volume IPs
    high_volume_ips = (
        recent_logs
        .values('ip_address')
        .annotate(request_count=Count('id'))
        .filter(request_count__gt=100)
    )
    
    for entry in high_volume_ips:
        ip = entry['ip_address']
        count = entry['request_count']
        reason = f'High request volume: {count} requests in the last hour (threshold: 100)'
        
        suspicious_ip, created = SuspiciousIP.objects.get_or_create(
            ip_address=ip,
            defaults={
                'reason': reason,
                'request_count': count
            }
        )
        
        if not created:
            suspicious_ip.reason = reason
            suspicious_ip.request_count = count
            suspicious_ip.save(update_fields=['reason', 'request_count', 'last_seen'])
        
        flagged_count += 1
        logger.info(f"Flagged IP {ip} for high volume: {count} requests/hour")
    
    # Rule-based detection: Sensitive paths
    sensitive_paths = ['/admin', '/login', '/api/admin', '/api/login']
    sensitive_access = (
        recent_logs
        .filter(path__in=sensitive_paths)
        .values('ip_address')
        .annotate(access_count=Count('id'))
        .filter(access_count__gte=10)
    )
    
    for entry in sensitive_access:
        ip = entry['ip_address']
        count = entry['access_count']
        
        paths_accessed = recent_logs.filter(
            ip_address=ip,
            path__in=sensitive_paths,
            timestamp__gte=one_hour_ago
        ).values_list('path', flat=True).distinct()
        
        reason = f'Repeated access to sensitive paths ({count} times): {", ".join(paths_accessed)}'
        
        suspicious_ip, created = SuspiciousIP.objects.get_or_create(
            ip_address=ip,
            defaults={
                'reason': reason,
                'request_count': count
            }
        )
        
        if not created:
            suspicious_ip.reason = reason
            suspicious_ip.request_count = count
            suspicious_ip.save(update_fields=['reason', 'request_count', 'last_seen'])
        
        flagged_count += 1
        logger.info(f"Flagged IP {ip} for sensitive path access: {count} times")
    
    # ML-based anomaly detection using scikit-learn
    if ML_AVAILABLE:
        try:
            flagged_ml = _ml_anomaly_detection(recent_logs)
            flagged_count += flagged_ml
        except Exception as e:
            logger.error(f"ML anomaly detection failed: {e}")
    else:
        logger.debug("ML-based anomaly detection skipped (scikit-learn not available)")
    
    logger.info(f"Anomaly detection completed. Flagged {flagged_count} suspicious IP(s).")
    return f"Flagged {flagged_count} suspicious IP(s)"
    

def _ml_anomaly_detection(recent_logs):
    """
    Use scikit-learn Isolation Forest for ML-based anomaly detection.
    Detects IPs with unusual behavior patterns.
    """
    if not ML_AVAILABLE:
        return 0
    
    flagged_count = 0
    
    try:
        # Aggregate features per IP
        ip_features = (
            recent_logs
            .values('ip_address')
            .annotate(
                request_count=Count('id'),
                unique_paths=Count('path', distinct=True),
                sensitive_path_count=Count('id', filter=Q(path__in=['/admin', '/login', '/api/admin', '/api/login']))
            )
        )
        
        if len(ip_features) < 2:
            # Need at least 2 IPs for ML to work
            return 0
        
        # Prepare features for ML
        features = []
        ip_list = []
        
        for entry in ip_features:
            ip_list.append(entry['ip_address'])
            features.append([
                entry['request_count'],
                entry['unique_paths'],
                entry['sensitive_path_count'],
            ])
        
        # Convert to numpy array
        X = np.array(features)
        
        # Standardize features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Train Isolation Forest (unsupervised anomaly detection)
        # contamination: expected proportion of anomalies (5%)
        isolation_forest = IsolationForest(contamination=0.05, random_state=42)
        predictions = isolation_forest.fit_predict(X_scaled)
        
        # Flag anomalous IPs (predictions == -1)
        for i, prediction in enumerate(predictions):
            if prediction == -1:  # Anomaly detected
                ip = ip_list[i]
                feature_values = features[i]
                
                reason = (
                    f'ML-detected anomaly: {feature_values[0]} requests, '
                    f'{feature_values[1]} unique paths, '
                    f'{feature_values[2]} sensitive path accesses'
                )
                
                suspicious_ip, created = SuspiciousIP.objects.get_or_create(
                    ip_address=ip,
                    defaults={
                        'reason': reason,
                        'request_count': feature_values[0]
                    }
                )
                
                if not created:
                    suspicious_ip.reason = reason
                    suspicious_ip.request_count = feature_values[0]
                    suspicious_ip.save(update_fields=['reason', 'request_count', 'last_seen'])
                
                flagged_count += 1
                logger.info(f"ML flagged IP {ip} as anomalous")
    
    except ImportError:
        logger.warning("scikit-learn not available. Install with: pip install scikit-learn")
    except Exception as e:
        logger.error(f"ML anomaly detection error: {e}")
    
    return flagged_count


@shared_task
def cleanup_old_logs():
    """
    Cleanup task to delete old request logs based on retention policy.
    Helps with privacy compliance and database management.
    """
    from django.conf import settings
    
    retention_days = getattr(settings, 'IP_TRACKING_RETENTION_DAYS', 90)
    cutoff_date = timezone.now() - timedelta(days=retention_days)
    
    deleted_count, _ = RequestLog.objects.filter(timestamp__lt=cutoff_date).delete()
    
    logger.info(f"Cleaned up {deleted_count} old request logs (older than {retention_days} days)")
    return f"Deleted {deleted_count} old logs"
