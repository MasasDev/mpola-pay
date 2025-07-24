#!/usr/bin/env python
"""
Test script to verify phone number uniqueness validation in payment schedules.
This script tests that:
1. Phone numbers cannot be duplicated within the same payment schedule
2. Phone numbers CAN be used across different payment schedules
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append('/Users/arthur/developer_zone/mpola')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mpola.settings')
django.setup()

from payments.models import BitnobCustomer, PaymentSchedule, MobileReceiver
from django.db import IntegrityError
from decimal import Decimal
import json

def test_phone_uniqueness():
    print("🧪 Testing phone number uniqueness validation...")
    
    # Create a test customer
    try:
        customer = BitnobCustomer.objects.create(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            phone="+1234567890",
            country_code="US",
            bitnob_id="test_123456"
        )
        print(f"✅ Created test customer: {customer.email}")
    except Exception as e:
        # Customer might already exist
        customer = BitnobCustomer.objects.get(email="test@example.com")
        print(f"✅ Using existing test customer: {customer.email}")
    
    # Create first payment schedule
    schedule1 = PaymentSchedule.objects.create(
        customer=customer,
        title="Test Schedule 1",
        description="First test schedule",
        subtotal_amount=Decimal('1000.00'),
        processing_fee=Decimal('15.00'),
        total_amount=Decimal('1015.00')
    )
    print(f"✅ Created payment schedule 1: {schedule1.title}")
    
    # Create first receiver in schedule 1
    receiver1 = MobileReceiver.objects.create(
        payment_schedule=schedule1,
        customer=customer,
        name="John Doe",
        phone="+1555123456",
        country_code="US",
        amount_per_installment=Decimal('100.00'),
        number_of_installments=5
    )
    print(f"✅ Created receiver 1 in schedule 1: {receiver1.name} ({receiver1.phone})")
    
    # Try to create another receiver with the same phone number in the same schedule
    try:
        receiver2 = MobileReceiver.objects.create(
            payment_schedule=schedule1,
            customer=customer,
            name="Jane Smith",
            phone="+1555123456",  # Same phone as receiver1
            country_code="US",
            amount_per_installment=Decimal('200.00'),
            number_of_installments=3
        )
        print("❌ ERROR: Should not have been able to create duplicate phone in same schedule!")
        return False
    except IntegrityError as e:
        print(f"✅ Correctly prevented duplicate phone in same schedule: {str(e)}")
    
    # Create second payment schedule
    schedule2 = PaymentSchedule.objects.create(
        customer=customer,
        title="Test Schedule 2",
        description="Second test schedule",
        subtotal_amount=Decimal('500.00'),
        processing_fee=Decimal('7.50'),
        total_amount=Decimal('507.50')
    )
    print(f"✅ Created payment schedule 2: {schedule2.title}")
    
    # Create receiver with same phone number but in different schedule (should work)
    try:
        receiver3 = MobileReceiver.objects.create(
            payment_schedule=schedule2,
            customer=customer,
            name="John Doe Alternative",
            phone="+1555123456",  # Same phone as receiver1 but different schedule
            country_code="US",
            amount_per_installment=Decimal('150.00'),
            number_of_installments=2
        )
        print(f"✅ Successfully created receiver with same phone in different schedule: {receiver3.name}")
    except IntegrityError as e:
        print(f"❌ ERROR: Should have been able to use same phone in different schedule: {str(e)}")
        return False
    
    # Cleanup
    schedule1.delete()
    schedule2.delete()
    try:
        customer.delete()
    except Exception:
        pass  # Customer might have other dependencies
    
    print("🎉 All tests passed! Phone number uniqueness validation is working correctly.")
    return True

if __name__ == "__main__":
    success = test_phone_uniqueness()
    if success:
        print("\n✅ SUCCESS: Phone number validation is implemented correctly!")
        print("- Phone numbers are unique within each payment schedule")
        print("- Same phone numbers can be used across different payment schedules")
    else:
        print("\n❌ FAILURE: Phone number validation needs fixing!")
        sys.exit(1)
