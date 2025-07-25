#!/usr/bin/env python3
"""
Test script for 5-minute interval payments with Bitnob API integration
Run this script to test the 5-minute payment functionality
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api"
HEADERS = {"Content-Type": "application/json"}

def print_response(title, response):
    """Print formatted response"""
    print(f"\n{'='*50}")
    print(f"{title}")
    print(f"{'='*50}")
    print(f"Status Code: {response.status_code}")
    
    try:
        data = response.json()
        print(json.dumps(data, indent=2))
    except:
        print(response.text)

def test_bitnob_api_connectivity():
    """Test 1: Check Bitnob API connectivity"""
    print(f"\n🔍 Testing Bitnob API connectivity...")
    response = requests.get(f"{BASE_URL}/test/bitnob-api-status/")
    print_response("Bitnob API Status Check", response)
    return response.status_code == 200

def create_5min_test_schedule():
    """Test 2: Create a 5-minute test schedule with basic functionality"""
    print(f"\n📅 Creating 5-minute test schedule...")
    data = {"frequency": "test_5min"}
    response = requests.post(f"{BASE_URL}/test/create-schedule/", json=data, headers=HEADERS)
    print_response("5-Minute Test Schedule Creation", response)
    
    if response.status_code == 201:
        result = response.json()
        return result.get("schedule", {}).get("id"), result.get("receiver", {}).get("id")
    return None, None

def create_5min_payment_with_bitnob():
    """Test 3: Create 5-minute schedule and immediately trigger Bitnob API payment"""
    print(f"\n💸 Creating 5-minute schedule with immediate Bitnob API payment...")
    response = requests.post(f"{BASE_URL}/test/create-5min-payment/", headers=HEADERS)
    print_response("5-Minute Payment with Bitnob API", response)
    
    if response.status_code == 201:
        result = response.json()
        return (
            result.get("schedule", {}).get("id"),
            result.get("receiver", {}).get("id"),
            result.get("transaction", {}).get("id"),
            result.get("transaction", {}).get("reference")
        )
    return None, None, None, None

def check_payment_timing(receiver_id):
    """Test 4: Check payment timing for a receiver"""
    if not receiver_id:
        print("❌ No receiver ID provided")
        return
        
    print(f"\n⏰ Checking payment timing for receiver {receiver_id}...")
    response = requests.post(f"{BASE_URL}/test/check-payment-timing/{receiver_id}/", headers=HEADERS)
    print_response("Payment Timing Check", response)

def check_scheduled_payments_status():
    """Test 5: Check overall scheduled payments status"""
    print(f"\n📊 Checking scheduled payments status...")
    response = requests.get(f"{BASE_URL}/scheduled-payments-status/")
    print_response("Scheduled Payments Status", response)

def trigger_scheduled_payments():
    """Test 6: Trigger scheduled payments processing"""
    print(f"\n🚀 Triggering scheduled payments processing...")
    response = requests.post(f"{BASE_URL}/trigger-scheduled-payments/", headers=HEADERS)
    print_response("Trigger Scheduled Payments", response)

def main():
    """Run all tests"""
    print("🎯 Starting 5-Minute Interval Payment Tests with Bitnob API")
    print(f"🕐 Test started at: {datetime.now()}")
    
    # Test 1: API Connectivity
    api_ok = test_bitnob_api_connectivity()
    if not api_ok:
        print("⚠️  Warning: Bitnob API connectivity issues detected")
    
    # Test 2: Basic Schedule Creation
    schedule_id, receiver_id = create_5min_test_schedule()
    
    # Test 3: Full Bitnob Integration Test
    bitnob_schedule_id, bitnob_receiver_id, transaction_id, reference = create_5min_payment_with_bitnob()
    
    # Test 4: Payment Timing
    if bitnob_receiver_id:
        check_payment_timing(bitnob_receiver_id)
    elif receiver_id:
        check_payment_timing(receiver_id)
    
    # Test 5: Status Check
    check_scheduled_payments_status()
    
    # Test 6: Trigger Processing
    trigger_scheduled_payments()
    
    print(f"\n✅ Test Summary:")
    print(f"   📅 Basic 5-min schedule created: {schedule_id is not None}")
    print(f"   💸 Bitnob payment initiated: {transaction_id is not None}")
    print(f"   🔗 Transaction reference: {reference}")
    print(f"   🕐 Test completed at: {datetime.now()}")
    
    if bitnob_schedule_id:
        print(f"\n🔄 Next Steps:")
        print(f"   1. Wait 5 minutes for next payment cycle")
        print(f"   2. Check status: GET {BASE_URL}/scheduled-payments-status/")
        print(f"   3. Trigger payments: POST {BASE_URL}/trigger-scheduled-payments/")
        print(f"   4. Check receiver timing: POST {BASE_URL}/test/check-payment-timing/{bitnob_receiver_id}/")

if __name__ == "__main__":
    main()
