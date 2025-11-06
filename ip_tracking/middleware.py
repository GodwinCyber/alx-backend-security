import datetime
from django.utils.timezone import now
from django.conf import settings
from .models import RequestLog, BlockedIP
from ipware import get_client_ip
from django.http import HttpResponseForbidden
import ipgeolocation #import GeolocationApi, ApiClient, Configuration
from django.core.cache import cache


class RequestLoggingMiddleware:
    '''
    Middleware that logs the IP address, timestamp, and request path
    for every incoming request.
    '''
    def __init__(self, get_response):
        '''One time configuration and initialization'''
        self.get_response = get_response

    def __call__(self, request):
        '''Middleware to log IP, timestamp and path of incoming request'''
        client_ip, is_routable = get_client_ip(request)

        # Get the client IP
        if client_ip is None:
            client_ip = "0.0.0.0"

        # Get the request path
        path = request.path

        timestamp = now()

        # Sae the Ip address
        try:
            RequestLog.objects.create(
                ip_address=client_ip,
                path=path,
                timestamp=timestamp
            )
        except Exception as e:
            print(f"Error logging request: {e}")

        response = self.get_response(request)
        return response
    
class RequestBlockedMiddleware:
    '''Blocked an IP address based on the blacklist'''
    def __init__(self, get_response):
        '''One time configurations and initialization'''
        self.get_response = get_response
        

    def __call__(self, request):
        '''Block request from IP from the blocked ip'''
        client_ip = get_client_ip(request) or "0.0.0.0"

        if BlockedIP.objects.filter(ip_address=client_ip).exists():
            return HttpResponseForbidden("Access forbidden: Your IP address has been blocked")
        
        # Log request
        RequestLog.objects.create(
            ip_address=client_ip,
            path=request.path,
        )

        response = self.get_response(request)
        return response
    
class GeoRequestLoggingMiddleware:
    '''
    Middleware that logs request data + country + city with caching
    '''
    def __init__(self, get_response):
        self.get_response = get_response
        self.geo = ipgeolocation.IPGeolocationApi(settings.IPGEOLOCATION_API_KEY)

    def __call__(self, request):
        """Extract the IP"""
        response = self.get_response(request)
        self.log_request(request)
        return response

        # check if geolocation data has been cached
    def log_request(self, request):
        ip = request.META.get("REMOTE_ADDR")
        
        cached_geo = cache.get(ip)
        if cached_geo:
            country = cached_geo["country"]
            city = cached_geo["city"]
        else:
            try:
                geo_data = self.geo.get_ip_geolocation(ip)
                country = geo_data.get("country_name", "")
                city = geo_data.get("city", "")
                cache.set(ip, {"country": country, "city": city}, 60 * 60 * 24)
            except Exception:
                country = ""
                city = ""
        # Save request record
        RequestLog.objects.create(
            ip_address=ip,
            path=request.path,
            timestamp=now(),
            country=country,
            city=city
        )


        
