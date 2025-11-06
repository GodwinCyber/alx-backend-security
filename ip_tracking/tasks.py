from celery import shared_task
from django.utils.timezone import now, timedelta
from .models import RequestLog, SuspiciousIP
from django.db import models

@shared_task
def detect_anomalies():
    '''Flag IP that exceed speciffied number of request in an hour '''
    one_hour_ago = now() - timedelta(hours=1)

    # Detect IP exceeding 100 request in last hour
    high_volume_ips = (
        RequestLog.objects.filter(timestamp__gte=one_hour_ago)
        .values("ip_address")
        .annotate(request_count=models.Count("id"))
        .filter(request_count__gt=100)
    )

    for entry in high_volume_ips:
        ip = entry["ip_address"]
        SuspiciousIP.objects.get_or_create(
            ip_address=ip,
            resason="More than 100 request in the last hour",
        )

    # Detect IPs accessing sensitive endpoint
    sensitive_paths = ["/admin", "/login"]
    suspicious_logs = RequestLog.objects.filter(
        timestamp__gte=one_hour_ago,
        path__in=sensitive_paths,
    ).values_list("ip_address", "path")

    for ip, path in suspicious_logs:
        SuspiciousIP.objects.get_or_create(
            ip_address=ip,
            reason=f"Accessed sensitive path: {path}"
        )
    return "Anomaly detected task completed."



