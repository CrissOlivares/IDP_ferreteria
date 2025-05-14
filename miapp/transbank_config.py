from transbank.common.options import WebpayOptions
from transbank.webpay.webpay_plus.transaction import Transaction
from django.conf import settings

def get_transaction():
    return Transaction(WebpayOptions(
        commerce_code=settings.TRANSBANK_COMMERCE_CODE,
        api_key=settings.TRANSBANK_API_KEY,
        integration_type=settings.TRANSBANK_ENVIRONMENT  # 'integration' o 'production'
    ))
