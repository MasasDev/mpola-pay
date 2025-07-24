#!/usr/bin/env python3
"""
Test script for the Payment Plan API
This script demonstrates how to test the CreatePaymentPlan endpoint with proper error handling.
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"  # Update this to your Django server URL
API_ENDPOINT = f"{BASE_URL}/api/payment-plans/"  # Update this to your actual endpoint

def test_payment_plan_creation():
    """Test creating a payment plan with the provided JSON payload"""
    
    # First, we need to create a customer - update this email as needed
    customer_email = "test@example.com"
    
    # Sample customer creation payload (if needed)
    customer_payload = {
        "email": customer_email,
        "firstName": "Test",
        "lastName": "Customer",
        "phone": "1234567890",
        "countryCode": "+1"
    }
    
    # Payment plan payload - your original request
    payment_plan_payload = {
        "email": customer_email,  # Use actual customer email instead of {{customer_email}}
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
    
    print("Testing Payment Plan Creation...")
    print(f"Payload: {json.dumps(payment_plan_payload, indent=2)}")
    print("-" * 50)
    
    try:
        # Make the API request
        response = requests.post(
            API_ENDPOINT,
            json=payment_plan_payload,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print("-" * 50)
        
        # Parse response
        try:
            response_data = response.json()
            print(f"Response Data: {json.dumps(response_data, indent=2)}")
        except json.JSONDecodeError:
            print(f"Raw Response Text: {response.text}")
        
        # Analyze results
        if response.status_code == 201:
            print("\n✅ SUCCESS: Payment plan created successfully!")
            if 'payment_schedule' in response_data:
                schedule = response_data['payment_schedule']
                print(f"   Schedule ID: {schedule.get('id')}")
                print(f"   Title: {schedule.get('title')}")
                print(f"   Total Amount: {schedule.get('total_amount')}")
                print(f"   Total Receivers: {response_data.get('total_receivers')}")
        elif response.status_code == 400:
            print("\n❌ BAD REQUEST: Please check your payload")
            if 'error' in response_data:
                print(f"   Error: {response_data['error']}")
        elif response.status_code == 404:
            print("\n❌ NOT FOUND: Customer doesn't exist")
            print(f"   Make sure customer with email '{customer_email}' exists")
            print("   You may need to create the customer first")
        else:
            print(f"\n❌ ERROR: Unexpected status code {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR: Could not connect to the server")
        print(f"   Make sure your Django server is running on {BASE_URL}")
    except requests.exceptions.RequestException as e:
        print(f"❌ REQUEST ERROR: {e}")
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")

def validate_payload_structure():
    """Validate the payload structure against expected serializer"""
    print("Validating payload structure...")
    
    # Expected fields based on PaymentScheduleCreateSerializer
    expected_fields = {
        'email': 'EmailField',
        'title': 'CharField',
        'description': 'CharField (optional)',
        'frequency': 'CharField (optional)',
        'start_date': 'DateTimeField (optional)',
        'receivers': 'ListField'
    }
    
    expected_receiver_fields = {
        'name': 'CharField',
        'phone': 'CharField',
        'countryCode': 'CharField',
        'amountPerInstallment': 'DecimalField',
        'numberOfInstallments': 'IntegerField'
    }
    
    print("Expected payload structure:")
    print(json.dumps(expected_fields, indent=2))
    print("\nExpected receiver structure:")
    print(json.dumps(expected_receiver_fields, indent=2))
    print("-" * 50)

if __name__ == "__main__":
    print("Payment Plan API Test Script")
    print("=" * 50)
    
    validate_payload_structure()
    print()
    test_payment_plan_creation()
    
    print("\n" + "=" * 50)
    print("Test completed!")
    print("\nNotes:")
    print("1. Make sure your Django server is running")
    print("2. Update the BASE_URL and API_ENDPOINT if needed") 
    print("3. Ensure the customer exists before creating payment plans")
    print("4. Check your database for created records")
