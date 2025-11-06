from django.urls import path
from .views import LoginView, AuthenticatedSensitiveView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('authenticated/', AuthenticatedSensitiveView.as_view(), name='authenticated')
]
