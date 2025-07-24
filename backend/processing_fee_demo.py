#!/usr/bin/env python3
"""
Processing Fee Demonstration
Shows the calculation of 1.5% processing fee for payment plans.
"""

def calculate_payment_totals(receivers):
    """Calculate subtotal, processing fee, and total amount"""
    print("📊 Payment Plan Processing Fee Calculation")
    print("=" * 50)
    
    # Calculate subtotal
    subtotal = 0
    print("💰 Receiver Breakdown:")
    for i, receiver in enumerate(receivers, 1):
        name = receiver['name']
        amount_per = receiver['amountPerInstallment']
        installments = receiver['numberOfInstallments']
        receiver_total = amount_per * installments
        subtotal += receiver_total
        
        print(f"   {i}. {name}:")
        print(f"      Amount per installment: ${amount_per:,}")
        print(f"      Number of installments: {installments}")
        print(f"      Receiver total: ${receiver_total:,}")
        print()
    
    # Calculate processing fee (1.5%)
    processing_fee_rate = 0.015  # 1.5%
    processing_fee = subtotal * processing_fee_rate
    total_amount = subtotal + processing_fee
    
    print("💳 Financial Summary:")
    print(f"   Subtotal Amount: ${subtotal:,.2f}")
    print(f"   Processing Fee ({processing_fee_rate*100}%): ${processing_fee:,.2f}")
    print(f"   Final Total: ${total_amount:,.2f}")
    print()
    
    # Show the impact
    print("📈 Processing Fee Impact:")
    percentage_of_total = (processing_fee / total_amount) * 100
    print(f"   Processing fee represents {percentage_of_total:.2f}% of final total")
    print(f"   Customer pays an additional ${processing_fee:.2f} for processing")
    
    return {
        'subtotal': subtotal,
        'processing_fee': processing_fee,
        'total': total_amount,
        'fee_percentage': processing_fee_rate * 100
    }

def demonstrate_scenarios():
    """Show processing fee calculation for different scenarios"""
    
    # Scenario 1: Your original example
    print("🔍 SCENARIO 1: Your Original Payment Plan")
    print("-" * 50)
    receivers_1 = [
        {
            "name": "Jane Doe",
            "amountPerInstallment": 5000,
            "numberOfInstallments": 2
        },
        {
            "name": "Mike Smith",
            "amountPerInstallment": 3000,
            "numberOfInstallments": 2
        }
    ]
    
    result_1 = calculate_payment_totals(receivers_1)
    print("\n" + "="*70 + "\n")
    
    # Scenario 2: Smaller amounts
    print("🔍 SCENARIO 2: Smaller Payment Plan")
    print("-" * 50)
    receivers_2 = [
        {
            "name": "Family Member 1",
            "amountPerInstallment": 1000,
            "numberOfInstallments": 3
        },
        {
            "name": "Family Member 2",
            "amountPerInstallment": 800,
            "numberOfInstallments": 2
        }
    ]
    
    result_2 = calculate_payment_totals(receivers_2)
    print("\n" + "="*70 + "\n")
    
    # Scenario 3: Larger amounts
    print("🔍 SCENARIO 3: Larger Payment Plan")
    print("-" * 50)
    receivers_3 = [
        {
            "name": "Main Beneficiary",
            "amountPerInstallment": 10000,
            "numberOfInstallments": 6
        },
        {
            "name": "Secondary Beneficiary",
            "amountPerInstallment": 5000,
            "numberOfInstallments": 4
        }
    ]
    
    result_3 = calculate_payment_totals(receivers_3)
    print("\n" + "="*70 + "\n")
    
    # Comparison
    print("📊 SCENARIO COMPARISON")
    print("-" * 50)
    scenarios = [
        ("Your Original Plan", result_1),
        ("Smaller Plan", result_2),
        ("Larger Plan", result_3)
    ]
    
    for name, result in scenarios:
        print(f"{name}:")
        print(f"   Subtotal: ${result['subtotal']:,.2f}")
        print(f"   Processing Fee: ${result['processing_fee']:,.2f}")
        print(f"   Total: ${result['total']:,.2f}")
        print()

def generate_json_with_fee():
    """Generate properly formatted JSON showing the fee calculation"""
    print("📄 JSON PAYLOAD WITH PROCESSING FEE CALCULATION")
    print("-" * 50)
    
    payload = {
        "email": "test@example.com",
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
    
    import json
    print("Request Payload:")
    print(json.dumps(payload, indent=2))
    
    # Calculate expected response
    subtotal = 16000
    processing_fee = 240.00
    total = 16240.00
    
    expected_response = {
        "message": "Payment schedule created successfully",
        "financial_summary": {
            "subtotal_amount": str(subtotal),
            "processing_fee": str(processing_fee),
            "processing_fee_percentage": "1.5%",
            "total_amount": str(total)
        },
        "total_receivers": 2
    }
    
    print("\nExpected Response (Financial Summary):")
    print(json.dumps(expected_response, indent=2))

if __name__ == "__main__":
    print("Payment Plan Processing Fee Calculator")
    print("=" * 70)
    print("This script demonstrates the 1.5% processing fee calculation")
    print("for payment plans in the Mpola API.\n")
    
    demonstrate_scenarios()
    print()
    generate_json_with_fee()
    
    print("\n" + "=" * 70)
    print("✅ Processing fee calculation complete!")
    print("\nKey Points:")
    print("• Processing fee is always 1.5% of the subtotal")
    print("• Fee is calculated before adding to the final total")
    print("• Database now tracks subtotal and processing fee separately")
    print("• API response includes detailed financial breakdown")
    print("• All amounts are rounded to 2 decimal places")
