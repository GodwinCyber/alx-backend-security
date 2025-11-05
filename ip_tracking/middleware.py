import datetime
from django.utils.timezone import now
from .models import RequestLog
from ipware import get_client_ip


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
        
