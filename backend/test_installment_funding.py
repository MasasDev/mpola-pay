#!/usr/bin/env python
"""
Test script to verify installment-based funding logic works correctly.
This script tests that payments can be made when there's enough funding for individual installments,
rather than requiring the full schedule to be funded.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mpola.settings')
django.setup()

from payments.models import BitnobCustomer, PaymentSchedule, MobileReceiver, FundTransaction, MobileTransaction
from django.utils import timezone
from decimal import Decimal
import uuid

def create_test_data():
    """Create test payment schedule with partial funding"""
    print("Creating test data...")
    
    # Create test customer
    customer, created = BitnobCustomer.objects.get_or_create(
        email="test_installment@example.com",
        defaults={
            "first_name": "Test",
            "last_name": "Installment",
            "phone": "+256700000000",
            "country_code": "UG",
            "bitnob_id": "test_installment_customer"
        }
    )
    
    # Create payment schedule
    schedule = PaymentSchedule.objects.create(
        customer=customer,
        title="Installment Funding Test",
        description="Test schedule for installment-based funding",
        frequency="daily",
        subtotal_amount=Decimal('1000'),  # 1000 UGX
        processing_fee=Decimal('15'),     # 1.5%
        total_amount=Decimal('1015'),     # Total
        start_date=timezone.now()
    )
    
    # Create receiver with 100 UGX per installment, 10 installments
    receiver = MobileReceiver.objects.create(
        payment_schedule=schedule,
        customer=customer,
        name="Test Receiver",
        phone="+256700000001",
        country_code="UG",
        amount_per_installment=Decimal('100'),  # 100 UGX per installment
        number_of_installments=10
    )
    
    # Add partial funding - only enough for 3 installments (300 UGX)
    fund_txn = FundTransaction.objects.create(
        schedule=schedule,
        reference=str(uuid.uuid4()),
        amount=Decimal('300'),  # Only 300 UGX funded
        currency="UGX",
        status="paid"
    )
    
    print(f"Created schedule {schedule.id} with partial funding")
    print(f"Receiver: {receiver.name} - {receiver.amount_per_installment} UGX per installment")
    print(f"Funding: {fund_txn.amount} UGX")
    
    return schedule, receiver, fund_txn

def test_funding_logic(schedule, receiver):
    """Test the funding logic"""
    print("\n=== Testing Funding Logic ===")
    
    print(f"Schedule total amount: {schedule.total_amount}")
    print(f"Total funded: {schedule.total_funded_amount}")
    print(f"Available balance: {schedule.available_balance}")
    print(f"Total payments made: {schedule.total_payments_made}")
    print(f"Is adequately funded (full): {schedule.is_adequately_funded}")
    print(f"Has funds for one installment: {schedule.has_sufficient_funds_for_amount(receiver.amount_per_installment)}")
    
    # Test receiver logic
    can_pay, message = receiver.can_receive_next_installment()
    print(f"\nReceiver can receive payment: {can_pay}")
    print(f"Message: {message}")
    
    return can_pay

def simulate_payments(receiver, num_payments=3):
    """Simulate making payments to test balance tracking"""
    print(f"\n=== Simulating {num_payments} Payments ===")
    
    for i in range(num_payments):
        print(f"\nPayment {i+1}:")
        print(f"  Available balance before: {receiver.payment_schedule.available_balance}")
        
        # Check if payment can be made
        can_pay, message = receiver.can_receive_next_installment()
        print(f"  Can pay: {can_pay} - {message}")
        
        if can_pay:
            # Create a successful transaction
            txn = MobileTransaction.objects.create(
                receiver=receiver,
                amount=receiver.amount_per_installment,
                installment_number=receiver.next_installment(),
                status="success",
                reference=f"test_ref_{i+1}",
                sent_at=timezone.now(),
                completed_at=timezone.now()
            )
            print(f"  Created transaction {txn.id} for installment {txn.installment_number}")
            print(f"  Available balance after: {receiver.payment_schedule.available_balance}")
        else:
            print(f"  Payment blocked: {message}")
            break

def main():
    """Run the test"""
    print("=== Installment Funding Test ===")
    
    # Clean up any existing test data
    PaymentSchedule.objects.filter(title="Installment Funding Test").delete()
    BitnobCustomer.objects.filter(email="test_installment@example.com").delete()
    
    # Create test data
    schedule, receiver, fund_txn = create_test_data()
    
    # Test initial funding logic
    can_pay_initially = test_funding_logic(schedule, receiver)
    
    if can_pay_initially:
        print("\n✅ SUCCESS: Payment allowed with partial funding!")
        
        # Simulate payments
        simulate_payments(receiver, 3)
        
        # Check final state
        print(f"\n=== Final State ===")
        print(f"Total payments made: {schedule.total_payments_made}")
        print(f"Available balance: {schedule.available_balance}")
        print(f"Completed installments: {receiver.completed_installments}")
        
        # Try one more payment (should fail if balance is exhausted)
        can_pay_final, message_final = receiver.can_receive_next_installment()
        print(f"Can make another payment: {can_pay_final} - {message_final}")
        
        if not can_pay_final and "Insufficient" in message_final:
            print("✅ SUCCESS: Payment correctly blocked when balance exhausted!")
        else:
            print("❌ ISSUE: Payment logic may not be working correctly")
            
    else:
        print("❌ FAILED: Payment not allowed with partial funding")
        print(f"   Error: {test_funding_logic(schedule, receiver)}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    main()
