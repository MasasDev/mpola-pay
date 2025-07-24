"""
JSON Payload Validation Test
This script validates the structure of your payment plan JSON payload.
"""

import json
from datetime import datetime

def validate_json_payload():
    """Validate the payment plan JSON payload structure"""
    
    # Your original payload with fixed template variable
    payload = {
        "email": "test@example.com",  # Replace {{customer_email}} with actual email
        "title": "Monthly Family Support",
        "description": "Monthly payments to family members",
        "frequency": "monthly",
        "receivers": [
            {
                "name": "Jane Doe",
                "phone": "778520941",
                "countryCode": "+256",
                "amountPerInstallment": 5000,
                "numberOfInstallments": 2
            },
            {
                "name": "Mike Smith",
                "phone": "705902042",
                "countryCode": "+256",
                "amountPerInstallment": 3000,
                "numberOfInstallments": 2
            }
        ]
    }
    
    print("🔍 Validating JSON Payload Structure")
    print("=" * 50)
    
    # Basic structure validation
    required_fields = ["email", "title", "receivers"]
    optional_fields = ["description", "frequency", "start_date"]
    
    print("✅ Required fields check:")
    for field in required_fields:
        if field in payload:
            print(f"   ✓ {field}: {type(payload[field]).__name__}")
        else:
            print(f"   ❌ {field}: MISSING")
    
    print("\n📋 Optional fields check:")
    for field in optional_fields:
        if field in payload:
            print(f"   ✓ {field}: {type(payload[field]).__name__}")
        else:
            print(f"   ○ {field}: Not provided (OK)")
    
    # Receivers validation
    print(f"\n👥 Receivers validation ({len(payload.get('receivers', []))} receivers):")
    
    receiver_required_fields = ["name", "phone", "countryCode", "amountPerInstallment", "numberOfInstallments"]
    
    for i, receiver in enumerate(payload.get('receivers', []), 1):
        print(f"\n   Receiver {i}: {receiver.get('name', 'Unknown')}")
        for field in receiver_required_fields:
            if field in receiver:
                value = receiver[field]
                print(f"     ✓ {field}: {value} ({type(value).__name__})")
            else:
                print(f"     ❌ {field}: MISSING")
    
    # Calculate totals
    print(f"\n💰 Financial Summary:")
    subtotal_amount = 0
    for receiver in payload.get('receivers', []):
        amount_per = receiver.get('amountPerInstallment', 0)
        num_installments = receiver.get('numberOfInstallments', 0)
        receiver_total = amount_per * num_installments
        subtotal_amount += receiver_total
        print(f"   {receiver.get('name', 'Unknown')}: ${amount_per} × {num_installments} = ${receiver_total}")
    
    # Calculate processing fee (1.5%)
    processing_fee = subtotal_amount * 0.015
    total_amount = subtotal_amount + processing_fee
    
    print(f"   Subtotal: ${subtotal_amount}")
    print(f"   Processing Fee (1.5%): ${processing_fee:.2f}")
    print(f"   Total Amount: ${total_amount:.2f}")
    
    # Data type validation
    print(f"\n🔢 Data Type Validation:")
    
    email = payload.get('email', '')
    if '@' in email and '.' in email:
        print(f"   ✓ Email format looks valid: {email}")
    else:
        print(f"   ⚠️  Email format might be invalid: {email}")
    
    for i, receiver in enumerate(payload.get('receivers', []), 1):
        amount = receiver.get('amountPerInstallment')
        installments = receiver.get('numberOfInstallments')
        
        if isinstance(amount, (int, float)) and amount > 0:
            print(f"   ✓ Receiver {i} amount is valid number: {amount}")
        else:
            print(f"   ❌ Receiver {i} amount is invalid: {amount}")
            
        if isinstance(installments, int) and installments > 0:
            print(f"   ✓ Receiver {i} installments is valid integer: {installments}")
        else:
            print(f"   ❌ Receiver {i} installments is invalid: {installments}")
    
    # Phone number validation
    print(f"\n📞 Phone Number Validation:")
    for i, receiver in enumerate(payload.get('receivers', []), 1):
        phone = str(receiver.get('phone', ''))
        country_code = receiver.get('countryCode', '')
        
        if phone.isdigit() and len(phone) >= 7:
            print(f"   ✓ Receiver {i} phone looks valid: {country_code}{phone}")
        else:
            print(f"   ⚠️  Receiver {i} phone might be invalid: {country_code}{phone}")
    
    # Generate the properly formatted JSON
    print(f"\n📄 Properly Formatted JSON:")
    print("-" * 30)
    print(json.dumps(payload, indent=2))
    
    return payload

def generate_curl_command(payload):
    """Generate a curl command for testing"""
    print(f"\n🔧 cURL Command for Testing:")
    print("-" * 30)
    
    json_str = json.dumps(payload).replace('"', '\\"')
    
    curl_command = f'''curl -X POST "http://localhost:8000/api/payment-plans/" \\
  -H "Content-Type: application/json" \\
  -d "{json_str}"'''
    
    print(curl_command)
    
    # Also provide a more readable version
    print(f"\n📋 Alternative cURL with file:")
    print("-" * 30)
    print("# Save the JSON to a file first:")
    print("cat > payment_plan.json << 'EOF'")
    print(json.dumps(payload, indent=2))
    print("EOF")
    print()
    print("# Then use the file in curl:")
    print('curl -X POST "http://localhost:8000/api/payment-plans/" \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d @payment_plan.json')

if __name__ == "__main__":
    print("Payment Plan JSON Validation")
    print("=" * 50)
    
    payload = validate_json_payload()
    generate_curl_command(payload)
    
    print(f"\n✅ Validation Complete!")
    print(f"\nNext steps:")
    print(f"1. Make sure customer exists in database")
    print(f"2. Start your Django server")
    print(f"3. Use the cURL command above to test")
    print(f"4. Or run: python test_payment_plan.py")
    print(f"5. Or run: python manage.py test_payment_plan --create-customer")
