"""
IP Logging Middleware

This middleware implements:
- Task 0: Basic IP logging
- Task 1: IP blacklisting (returns 403 for blocked IPs)
- Task 2: IP geolocation with 24-hour caching
"""
import logging
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden
from django.core.cache import cache
from django.conf import settings
from ipware import get_client_ip

from .models import RequestLog, BlockedIP

logger = logging.getLogger(__name__)


class IPLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log IP addresses, block blacklisted IPs,
    and perform geolocation lookups with caching.
    """

    def process_request(self, request):
        """
        Process each request to:
        1. Extract client IP address
        2. Check if IP is blocked (Task 1)
        3. Perform geolocation lookup with caching (Task 2)
        4. Log the request (Task 0)
        """
        # Skip logging for static files and health checks
        if self._should_skip_logging(request):
            return None

        # Get client IP address using django-ipware
        ip, is_routable = get_client_ip(request)
        if ip is None:
            ip = '0.0.0.0'

        # Anonymize IP if configured (for privacy compliance)
        if getattr(settings, 'IP_TRACKING_ANONYMIZE', False):
            ip = self._anonymize_ip(ip)

        # Task 1: Check if IP is blocked
        if self._is_ip_blocked(ip):
            logger.warning(f"Blocked IP attempt: {ip} accessing {request.path}")
            return HttpResponseForbidden(
                "Forbidden: Your IP address has been blacklisted."
            )

        # Task 2: Get geolocation data (with 24-hour cache)
        country, city = self._get_geolocation(ip)

        # Task 0: Log the request
        try:
            RequestLog.objects.create(
                ip_address=ip,
                path=request.path,
                method=request.method,
                country=country,
                city=city,
                user=request.user if hasattr(request, 'user') and request.user.is_authenticated else None
            )
        except Exception as e:
            logger.error(f"Failed to log request: {e}")

        return None

    def _should_skip_logging(self, request):
        """Skip logging for static files and common health check paths."""
        skip_paths = ['/static/', '/media/', '/favicon.ico', '/health']
        return any(request.path.startswith(path) for path in skip_paths)

    def _is_ip_blocked(self, ip):
        """
        Check if IP is in the blacklist.
        Uses cache to avoid frequent database queries.
        """
        cache_key = f'blocked_ip:{ip}'
        is_blocked = cache.get(cache_key)

        if is_blocked is None:
            is_blocked = BlockedIP.objects.filter(ip_address=ip).exists()
            # Cache for 1 hour
            cache.set(cache_key, is_blocked, 3600)

        return is_blocked

    def _get_geolocation(self, ip):
        """
        Get geolocation data for an IP address using geoip2 (MaxMind).
        Uses 24-hour caching to avoid repeated DB lookups.
        """
        # Skip geolocation for local/private IPs
        if ip in ['127.0.0.1', '::1', '0.0.0.0'] or ip.startswith('192.168.') or ip.startswith('10.'):
            return None, None

        cache_key = f'geoip:{ip}'
        geo_data = cache.get(cache_key)

        if geo_data is None:
            country = None
            city = None
            try:
                from geoip2.database import Reader
                import os
                geoip_path = getattr(settings, 'GEOIP_PATH', None) or os.environ.get('GEOIP_PATH')
                if not geoip_path:
                    logger.warning("GEOIP_PATH not set in settings or environment. Geolocation will be skipped.")
                else:
                    db_file = os.path.join(geoip_path, 'GeoLite2-City.mmdb')
                    if not os.path.exists(db_file):
                        logger.warning(f"GeoLite2-City.mmdb not found at {db_file}. Download from MaxMind and place it there.")
                    else:
                        with Reader(db_file) as reader:
                            response = reader.city(ip)
                            country = response.country.name
                            city = response.city.name
            except ImportError:
                logger.warning("geoip2 not installed. Install with: pip install geoip2")
            except Exception as e:
                logger.debug(f"GeoIP2 lookup failed for {ip}: {e}")

            geo_data = {'country': country, 'city': city}
            # Cache for 24 hours (86400 seconds)
            cache.set(cache_key, geo_data, 86400)

        return geo_data.get('country'), geo_data.get('city')

    def _anonymize_ip(self, ip):
        """
        Anonymize IP address by zeroing the last octet (IPv4)
        or last 64 bits (IPv6) for privacy compliance.
        """
        if '.' in ip:  # IPv4
            parts = ip.split('.')
            if len(parts) == 4:
                return '.'.join(parts[:3]) + '.0'
        elif ':' in ip:  # IPv6
            # Zero out last 64 bits
            parts = ip.split(':')
            if len(parts) >= 4:
                return ':'.join(parts[:4]) + '::0'
        return ip
