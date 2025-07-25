# services/bitnob.py
import requests
from django.conf import settings

BASE = "https://api.bitnob.co/api/v1"
HEADERS = {"Authorization": f"Bearer {settings.BITNOB_API_KEY}", "Content-Type": "application/json"}

def lookup_mobile(country, number):
    # Skip lookup for Uganda as it's not supported
    if country in ["+256", "256", "UG", "Uganda"]:
        return {"status": True, "message": "Lookup skipped for Uganda", "data": {"accountName": "Mobile Money Account"}}
    
    url = f"{BASE}/payouts/mobile/lookup"
    payload = {"countryCode": country,  "accountNumber": number}
    return requests.post(url, json=payload, headers=HEADERS).json()

def request_mobile_invoice(country, number, sender_name, amount_cents, callback_url=None):
    url = f"{BASE}/mobile-payments/initiate"
    payload = {
        "countryCode": country,
        "accountNumber": number,
        "senderName": sender_name,
        "amount": amount_cents,
        
        "description": f"Payout to {number}",
    }
    if callback_url: payload["callbackUrl"] = callback_url
    response = requests.post(url, json=payload, headers=HEADERS).json()
    
    # Extract id and reference from response for payment processing
    if response.get('status') and response.get('data'):
        invoice_data = response['data']
        extracted_id = invoice_data.get('id')
        extracted_reference = invoice_data.get('reference')
        
        return {
            'response': response,
            'id': extracted_id,
            'reference': extracted_reference,
            'success': True,
            'amount': invoice_data.get('amount'),
            'status': invoice_data.get('status'),
            'expires_at': invoice_data.get('expiresAt')
        }
    
    # Return error response with debugging info
    return {
        'response': response, 
        'id': None, 
        'reference': None, 
        'success': False,
        'error': response.get('message', 'Unknown error')
    }

def pay_mobile_invoice(customer_email, reference=None, invoice_id=None, wallet="USD"):
    # The API expects: POST /mobile-payments/pay/{id} with reference in body
    if not invoice_id:
        return {"status": False, "message": "invoice_id is required for payment"}
    
    if not reference:
        return {"status": False, "message": "reference is required for payment"}
    
    url = f"{BASE}/mobile-payments/pay/{invoice_id}"
    payload = {
        "customerEmail": customer_email, 
        "reference": reference,
        "wallet": wallet
    }
    
    try:
        response = requests.post(url, json=payload, headers=HEADERS).json()
        return response
    except requests.exceptions.RequestException as e:
        return {"status": False, "message": f"Payment request failed: {str(e)}"}

def create_and_pay_mobile_invoice(country, number, sender_name, amount_cents, customer_email, wallet="USD", callback_url=None):
    """
    Complete workflow: Create invoice and immediately pay it
    Returns the payment result along with invoice details
    """
    # Step 1: Create the invoice
    invoice_result = request_mobile_invoice(country, number, sender_name, amount_cents, callback_url)
    
    if not invoice_result['success']:
        return {
            'invoice_success': False,
            'payment_success': False,
            'error': f"Invoice creation failed: {invoice_result['error']}",
            'invoice_result': invoice_result
        }
    
    # Step 2: Pay the invoice using extracted id and reference
    payment_result = pay_mobile_invoice(
        customer_email=customer_email,
        invoice_id=invoice_result['id'],
        reference=invoice_result['reference'],
        wallet=wallet
    )
    
    return {
        'invoice_success': True,
        'payment_success': payment_result.get('status', False),
        'invoice_result': invoice_result,
        'payment_result': payment_result,
        'invoice_id': invoice_result['id'],
        'reference': invoice_result['reference']
    }


