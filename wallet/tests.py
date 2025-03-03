import uuid
from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from .models import Wallet

class WalletOperationTests(TestCase):
    def setUp(self):
        # Настройка: создаем пользователя и кошелек для тестов
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.wallet = Wallet.objects.create(user=self.user, balance=Decimal('100.00'))
        self.client = APIClient() # Инициализируем APIClient

    def test_deposit_operation_success(self):
        # Тест успешного пополнения кошелька (DEPOSIT)
        url = reverse('wallet:wallet_operation', kwargs={'uuid': self.wallet.id})
        data = {'operationType': 'DEPOSIT', 'amount': 50.00} # Данные запроса для пополнения
        response = self.client.post(url, data, format='json') # Выполняем POST запрос через APIClient

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(Decimal(response.data['balance']), self.wallet.balance + Decimal('50.00'))

    def test_withdraw_operation_success(self):
        # Тест успешного снятия средств с кошелька (WITHDRAW)
        url = reverse('wallet:wallet_operation', kwargs={'uuid': self.wallet.id})
        data = {'operationType': 'WITHDRAW', 'amount': 30.00}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(Decimal(response.data['balance']), self.wallet.balance - Decimal('30.00'))

    def test_withdraw_operation_insufficient_funds(self):
        # Тест неуспешного снятия средств (WITHDRAW) - недостаточно средств на балансе
        url = reverse('wallet:wallet_operation', kwargs={'uuid': self.wallet.id})
        data = {'operationType': 'WITHDRAW', 'amount': 200.00} # Сумма снятия больше баланса
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 'error')
        self.assertIn('Недостаточно средств', response.data['message'])

    def test_invalid_operation_type(self):
        # Тест с неверным типом операции (invalid operationType)
        url = reverse('wallet:wallet_operation', kwargs={'uuid': self.wallet.id})
        data = {'operationType': 'INVALID_TYPE', 'amount': 100.00} # Неверный operationType
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('operationType', response.data)

    def test_invalid_amount_format(self):
        # Тест с неверным форматом суммы (invalid amount format) - строка вместо числа
        url = reverse('wallet:wallet_operation', kwargs={'uuid': self.wallet.id})
        data = {'operationType': 'DEPOSIT', 'amount': 'abc'} # Неверный формат amount (строка)
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('amount', response.data)

    def test_wallet_not_found(self):
        # Тест с неверным UUID кошелька (wallet not found)
        invalid_uuid = uuid.uuid4() # Генерируем случайный UUID, которого точно нет в БД
        url = reverse('wallet:wallet_operation', kwargs={'uuid': invalid_uuid}) # URL с неверным UUID
        data = {'operationType': 'DEPOSIT', 'amount': 100.00}
        response = self.client.post(url, data, format='json')

        print(f"test_wallet_not_found: response.status_code = {response.status_code}")
        print(f"test_wallet_not_found: response.data = {response.data}")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'],'Кошелек не найден')


class WalletDetailTests(TestCase):
    def setUp(self):
        # Настройка: создаем пользователя и кошелек для тестов
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.wallet = Wallet.objects.create(user=self.user, balance=Decimal('100.00'))
        self.client = APIClient() # Инициализируем APIClient

    def test_get_wallet_detail_success(self):
        # Тест успешного получения деталей кошелька (GET)
        url = reverse('wallet:wallet_detail', kwargs={'uuid': self.wallet.id})  # URL для деталей кошелька
        response = self.client.get(url)  # Выполняем GET запрос через APIClient

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['balance'], str(self.wallet.balance))
        self.assertEqual(response.data['user'], self.user.id)

    def test_get_wallet_detail_not_found(self):
        # Тест получения деталей кошелька с неверным UUID (wallet not found)
        invalid_uuid = uuid.uuid4() # Генерируем случайный UUID, которого точно нет в БД
        url = reverse('wallet:wallet_detail', kwargs={'uuid': invalid_uuid}) # URL с неверным UUID
        response = self.client.get(url) # Выполняем GET запрос через APIClient

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], 'Кошелек не найден.')