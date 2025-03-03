from django.urls import path
from .views import UserRegistration, WalletDetail, WalletOperation

app_name = 'wallet'

urlpatterns = [
    path("register/", UserRegistration.as_view(), name="register"),
    path("<uuid:uuid>/", WalletDetail.as_view(), name="wallet_detail"),
    path("<uuid:uuid>/operation/", WalletOperation.as_view(), name="wallet_operation"),
]
