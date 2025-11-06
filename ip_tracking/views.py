from django.shortcuts import render
from django_ratelimit.decorators import ratelimit
from django.views import View
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.contrib.auth import login, authenticate
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt
from .models import RequestLog
from django.utils.timezone import now


# Sensitive view (login attemp)
@method_decorator(csrf_exempt, name='dispatch')
class LoginView(View):
    '''Loging view with IP-based limiting'''

    # Rate limit anonymouse users
    @method_decorator(
        ratelimit(
            key='ip', rate='5/m',
            method='POST',
            block=True
        )
    )
    def post(self, request):
        import json
        try:
            data = json.loads(request.body.decode())
        except Exception:
            return JsonResponse({"error": "Inavlid request body"}, status=400)
        username = data.get('username')
        password = data.get('password')
        if not username or not password:
            return JsonResponse({"error": "Username and password are required"}, status=400)

        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)

            csrf_token = get_token(request)
            return JsonResponse({
                "message": "Login sucessful",
                "username": user.username,
                "csrf_token": csrf_token
            })
        return JsonResponse({"error": "Invalid credentials"}, status=401)

class AuthenticatedSensitiveView(View):
    """
    View for authenticated users with stricter limits.
    """
    @method_decorator(ratelimit(key='user_or_ip', rate='10/m', method='POST', block=True))
    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication required"}, status=401)
        
        RequestLog.objects.create(
            ip_address=self.get_client_ip(request),
            path=request.path,
            timestamp=now(),
            country=None,
            city=None,
        )
        return JsonResponse({
            "Message": "Authenticated sensitive action logged sucessfully",
            "user": request.user.username,
            })


    def get_client_ip(self, request):
        '''Helper method to get client IP'''
        from ipware import get_client_ip
        ip, _ = get_client_ip(request)
        return ip or "0.0.0.0"

