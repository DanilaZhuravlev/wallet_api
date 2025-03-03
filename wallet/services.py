# wallet/services.py
from decimal import Decimal
from uuid import UUID
import logging

from django.db.models import F
from rest_framework import status
from rest_framework.response import Response
from .models import Wallet

logger = logging.getLogger(__name__)


def process_wallet_operation(wallet_id, operation_type, amount):
    logger.debug(f"Начало process_wallet_operation: wallet_id={wallet_id}, operation_type={operation_type}, amount={amount}") # ЛОГ

    try:
        if not isinstance(wallet_id, UUID):
            wallet_id = UUID(wallet_id)
            logger.debug(f"wallet_id преобразован в UUID: wallet_id={wallet_id}") #  ЛОГ
        amount = Decimal(str(amount))
        logger.debug(f"amount преобразован в Decimal: amount={amount}") #  ЛОГ

        if operation_type == "DEPOSIT":
            logger.debug(f"Тип операции: DEPOSIT") # ЛОГ
            # Атомарно увеличиваем баланс без явной блокировки
            updated = Wallet.objects.filter(id=wallet_id).update(balance=F('balance') + amount)
            logger.debug(f"После Wallet.objects.filter(id=wallet_id).update(...): updated={updated}") #  ЛОГ
            if updated:
                new_balance = Wallet.objects.get(id=wallet_id).balance
                operation_result = {"status": "success", "balance": str(new_balance)}
                logger.debug(f"DEPOSIT успешен, operation_result={operation_result}") #  ЛОГ
                response = Response(operation_result, status=status.HTTP_200_OK)
                logger.debug(f"DEPOSIT успешен, response={response}") # ЛОГ
                return response
            else:
                operation_result = {"status": "error", "message": "Кошелек не найден"}
                logger.debug(f"DEPOSIT не успешен, кошелек не найден, operation_result={operation_result}") # ЛОГ
                response = Response(operation_result, status=status.HTTP_404_NOT_FOUND)
                logger.debug(f"DEPOSIT не успешен, кошелек не найден, response={response}") # ЛОГ
                return response

        elif operation_type == "WITHDRAW":
            logger.debug(f"Тип операции: WITHDRAW") # ЛОГ
            # Атомарно уменьшаем баланс, если текущий баланс >= amount
            updated = Wallet.objects.filter(id=wallet_id, balance__gte=amount).update(balance=F('balance') - amount)
            logger.debug(f"После Wallet.objects.filter(id=wallet_id, balance__gte=amount).update(...): updated={updated}") # ЛОГ
            if updated:
                new_balance = Wallet.objects.get(id=wallet_id).balance
                operation_result = {"status": "success", "balance": str(new_balance)}
                logger.debug(f"WITHDRAW успешен, operation_result={operation_result}") #  ЛОГ
                response = Response(operation_result, status=status.HTTP_200_OK)
                logger.debug(f"WITHDRAW успешен, response={response}") #  ЛОГ
                return response
            else:
                if Wallet.objects.filter(id=wallet_id).exists():
                    operation_result = {"status": "error", "message": "Недостаточно средств"}
                    logger.debug(f"WITHDRAW не успешен, недостаточно средств, operation_result={operation_result}") # ЛОГ
                    response = Response(operation_result, status=status.HTTP_400_BAD_REQUEST)
                    logger.debug(f"WITHDRAW не успешен, недостаточно средств, response={response}") #  ЛОГ
                    return response
                else:
                    operation_result = {"status": "error", "message": "Кошелек не найден"}
                    logger.debug(f"WITHDRAW не успешен, кошелек не найден, operation_result={operation_result}") # ЛОГ
                    response = Response(operation_result, status=status.HTTP_404_NOT_FOUND)
                    logger.debug(f"WITHDRAW не успешен, кошелек не найден, response={response}") # ЛОГ
                    return response

        else: # Обработка некорректного operation_type
            operation_result = {"status": "error", "message": "Неизвестный тип операции"}
            logger.debug(f"Неверный operation_type, operation_result={operation_result}") # ЛОГ
            response = Response(operation_result, status=status.HTTP_400_BAD_REQUEST)
            logger.debug(f"Неверный operation_type, response={response}") # ЛОГ
            return response

    except Exception as e:
        logger.exception("Ошибка в процессе операции")
        response = Response(
            {"detail": "Ошибка при обработке операции кошелька"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
        logger.debug(f"Исключение в process_wallet_operation, response={response}, error={e}") # ЛОГ
        return response