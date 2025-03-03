# views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Wallet
from .serializers import WalletOperationSerializer, WalletSerializer, UserRegistrationSerializer
from .services import process_wallet_operation
import logging

logger = logging.getLogger(__name__)


class WalletOperation(APIView):
    def post(self, request, *args, **kwargs):
        serializer = WalletOperationSerializer(data=request.data)
        if serializer.is_valid():
            wallet_id = str(kwargs["uuid"])
            operation_type = serializer.validated_data["operationType"]
            amount = serializer.validated_data["amount"]

            return process_wallet_operation(wallet_id, operation_type, amount)

        else:
            logger.error(f"Ошибки валидации сериализатора: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserRegistration(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WalletDetail(APIView):
    def get(self, request, *args, **kwargs):
        try:
            wallet = Wallet.objects.get(id=kwargs['uuid'])
        except Wallet.DoesNotExist:
            return Response({"detail": "Кошелек не найден."}, status=status.HTTP_404_NOT_FOUND)
        serializer = WalletSerializer(wallet)
        return Response(serializer.data, status=status.HTTP_200_OK)