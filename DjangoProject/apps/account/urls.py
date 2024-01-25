from .views import *
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('register/', RegistrationView.as_view(), name="register"),
    path('login/', LoginView.as_view(), name="login"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('checksession/', CheckSession.as_view(), name="checksession"),
    path('deletesession/', DeleteSession.as_view(), name="deletesession"),
    path('validate_username/', csrf_exempt(UsernameValidationView.as_view()), name='validate_username')
]
