# services/bitnob.py
import requests
from django.conf import settings

BASE = "https://sandboxapi.bitnob.co/api/v1"
HEADERS = {"Authorization": f"Bearer {settings.BITNOB_API_KEY}", "Content-Type": "application/json"}

def lookup_mobile(country, number):
    url = f"{BASE}/payouts/mobile/lookup"
    payload = {"countryCode": country,  "accountNumber": number}
    return requests.post(url, json=payload, headers=HEADERS).json()

def request_mobile_invoice(country, number, sender_name, amount_cents, callback_url=None):
    url = f"{BASE}/payouts/mobile/invoice"
    payload = {
        "countryCode": country,
        "accountNumber": number,
        "senderName": sender_name,
        "amount": amount_cents,
        "paymentMethodIdentifier": "MOBILEMONEY",
        "description": f"Payout to {number}",
    }
    if callback_url: payload["callbackUrl"] = callback_url
    return requests.post(url, json=payload, headers=HEADERS).json()

def pay_mobile_invoice(customer_email, reference, wallet="USD"):
    url = f"{BASE}/payouts/mobile/pay"
    payload = {"customerEmail": customer_email, "reference": reference, "wallet": wallet}
    return requests.post(url, json=payload, headers=HEADERS).json()


