#serializers.py
from decimal import Decimal

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Wallet

class UserRegistrationSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    wallet_balance = serializers.DecimalField(source='wallet.balance', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'wallet_balance')
        unique_together = ['username', 'email']

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Такое имя пользователя уже зарегистрировано.')
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        Wallet.objects.create(user=user)
        return user

class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['user', 'balance']

class WalletOperationSerializer(serializers.Serializer):
    operationType = serializers.ChoiceField(choices=['DEPOSIT', 'WITHDRAW'])
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate_amount(self, value):
        if value <= Decimal('0'):  # ПРОВЕРКА: amount должен быть > 0
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value