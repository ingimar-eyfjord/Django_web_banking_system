from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from django.contrib.auth.views import LoginView, LogoutView
from django_otp.forms import OTPAuthenticationForm
from bank.views import logout_view
from rest_framework.authtoken.views import obtain_auth_token 

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^accounts/login/$', LoginView.as_view(authentication_form=OTPAuthenticationForm)),
    url(r'^accounts/logout/$', logout_view, name='logout'),
    path('', include('bank.urls')),
    path('api/v1/', include('api.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('api/v1/rest-auth/', include('rest_auth.urls')),
    path('api/v1/api-token-auth/', obtain_auth_token, name='api_token_auth'), 
]
