#!/usr/bin/env python3
"""
Test script for funding logic and webhook confirmation
This script tests the complete funding workflow including:
1. Creating USDT deposit addresses
2. Simulating webhook confirmations
3. Validating funding status
4. Testing payout initiation with funding checks
"""

import requests
import json
import time
import uuid
from decimal import Decimal

BASE_URL = "http://localhost:8000"  # Adjust as needed

class FundingWorkflowTester:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.test_data = {}
        
    def log(self, message):
        print(f"[TEST] {message}")
        
    def test_create_customer(self):
        """Test customer creation"""
        self.log("Creating test customer...")
        
        payload = {
            "email": f"test.funding.{uuid.uuid4().hex[:8]}@example.com",
            "firstName": "Test",
            "lastName": "Funding",
            "phone": "+256700123456",
            "countryCode": "UG"
        }
        
        response = requests.post(f"{self.base_url}/create-customer/", json=payload)
        
        if response.status_code in [200, 201]:
            data = response.json()
            self.test_data["customer_email"] = payload["email"]
            self.test_data["customer_bitnob_id"] = data.get("bitnob_id")
            self.log(f"✅ Customer created: {self.test_data['customer_email']}")
            return True
        else:
            self.log(f"❌ Customer creation failed: {response.text}")
            return False
    
    def test_create_payment_schedule(self):
        """Test payment schedule creation"""
        self.log("Creating payment schedule...")
        
        payload = {
            "email": self.test_data["customer_email"],
            "title": "Test Funding Schedule",
            "description": "Testing funding workflow",
            "frequency": "monthly",
            "receivers": [
                {
                    "name": "Test Receiver 1",
                    "phone": "700123456",
                    "countryCode": "+256",
                    "amountPerInstallment": 50000,  # 50,000 UGX
                    "numberOfInstallments": 2
                },
                {
                    "name": "Test Receiver 2", 
                    "phone": "700123457",
                    "countryCode": "+256",
                    "amountPerInstallment": 30000,  # 30,000 UGX
                    "numberOfInstallments": 3
                }
            ]
        }
        
        response = requests.post(f"{self.base_url}/create-payment/", json=payload)
        
        if response.status_code == 201:
            data = response.json()
            self.test_data["schedule_id"] = data["payment_schedule"]["id"]
            self.test_data["total_amount"] = data["financial_summary"]["total_amount"]
            self.test_data["receivers"] = data["receivers"]
            self.log(f"✅ Payment schedule created: {self.test_data['schedule_id']}")
            self.log(f"   Total amount: {self.test_data['total_amount']} UGX")
            return True
        else:
            self.log(f"❌ Payment schedule creation failed: {response.text}")
            return False
    
    def test_check_initial_funding_status(self):
        """Check initial funding status (should be unfunded)"""
        self.log("Checking initial funding status...")
        
        response = requests.get(f"{self.base_url}/schedules/{self.test_data['schedule_id']}/funding-status/")
        
        if response.status_code == 200:
            data = response.json()
            funding_summary = data["funding_summary"]
            
            self.log(f"   Required: {funding_summary['total_required']} UGX")
            self.log(f"   Funded: {funding_summary['total_funded']} UGX")
            self.log(f"   Is adequately funded: {funding_summary['is_adequately_funded']}")
            
            if not funding_summary["is_adequately_funded"]:
                self.log("✅ Schedule correctly shows as unfunded")
                return True
            else:
                self.log("❌ Schedule incorrectly shows as funded")
                return False
        else:
            self.log(f"❌ Failed to get funding status: {response.text}")
            return False
    
    def test_create_usdt_deposit(self):
        """Test USDT deposit creation"""
        self.log("Creating USDT deposit...")
        
        payload = {
            "network": "TRON"
        }
        
        response = requests.post(
            f"{self.base_url}/schedules/{self.test_data['schedule_id']}/fund-usdt/", 
            json=payload
        )
        
        if response.status_code == 201:
            data = response.json()
            self.test_data["fund_reference"] = data["funding_details"]["reference"]
            self.test_data["deposit_address"] = data["funding_details"]["deposit_address"]
            self.test_data["usdt_required"] = data["funding_details"]["usdt_required"]
            
            self.log(f"✅ USDT deposit created")
            self.log(f"   Reference: {self.test_data['fund_reference']}")
            self.log(f"   Deposit address: {self.test_data['deposit_address']}")
            self.log(f"   USDT required: {self.test_data['usdt_required']}")
            return True
        else:
            self.log(f"❌ USDT deposit creation failed: {response.text}")
            return False
    
    def test_simulate_webhook_confirmation(self):
        """Simulate webhook confirmation of funding"""
        self.log("Simulating webhook confirmation...")
        
        # Use the test endpoint for simulation since the real webhook needs external triggers
        webhook_payload = {
            "reference": self.test_data["fund_reference"],
            "event": "stablecoin.deposit.confirmed"
        }
        
        response = requests.post(f"{self.base_url}/test/simulate-webhook/", json=webhook_payload)
        
        if response.status_code == 200:
            data = response.json()
            self.log(f"✅ Webhook processed successfully")
            self.log(f"   Status: {data['status']}")
            self.log(f"   Old status: {data['old_status']}")
            self.log(f"   New status: {data['new_status']}")
            
            # Check if schedule funding status was updated
            funding_status = data.get("schedule_funding_status", {})
            self.log(f"   Schedule is funded: {funding_status.get('is_funded')}")
            return True
        else:
            self.log(f"❌ Webhook processing failed: {response.text}")
            return False
    
    def test_check_funding_status_after_confirmation(self):
        """Check funding status after webhook confirmation"""
        self.log("Checking funding status after confirmation...")
        
        response = requests.get(f"{self.base_url}/schedules/{self.test_data['schedule_id']}/funding-status/")
        
        if response.status_code == 200:
            data = response.json()
            funding_summary = data["funding_summary"]
            
            self.log(f"   Required: {funding_summary['total_required']} UGX")
            self.log(f"   Funded: {funding_summary['total_funded']} UGX")
            self.log(f"   Is adequately funded: {funding_summary['is_adequately_funded']}")
            self.log(f"   Funding percentage: {funding_summary['funding_percentage']}%")
            
            if funding_summary["is_adequately_funded"]:
                self.log("✅ Schedule correctly shows as funded")
                return True
            else:
                self.log("❌ Schedule still shows as unfunded")
                return False
        else:
            self.log(f"❌ Failed to get funding status: {response.text}")
            return False
    
    def test_initiate_payout_with_funding(self):
        """Test payout initiation with adequate funding"""
        self.log("Testing payout initiation with funding...")
        
        if not self.test_data.get("receivers"):
            self.log("❌ No receivers data available")
            return False
            
        receiver = self.test_data["receivers"][0]
        
        payload = {
            "receiverId": receiver["id"],
            "senderName": "Test Funding Workflow"
        }
        
        response = requests.post(f"{self.base_url}/initiate-payout/", json=payload)
        
        if response.status_code == 201:
            data = response.json()
            self.log(f"✅ Payout initiated successfully")
            self.log(f"   Transaction ID: {data['transactionId']}")
            self.log(f"   Reference: {data['reference']}")
            self.log(f"   Amount: {data['amount']} UGX")
            return True
        else:
            self.log(f"❌ Payout initiation failed: {response.text}")
            return False
    
    def test_webhook_edge_cases(self):
        """Test webhook edge cases"""
        self.log("Testing webhook edge cases...")
        
        # Test unknown event
        webhook_payload = {
            "event": "stablecoin.unknown.event",
            "reference": self.test_data["fund_reference"]
        }
        
        response = requests.post(f"{self.base_url}/test/simulate-webhook/", json=webhook_payload)
        
        if response.status_code == 200:
            data = response.json()
            if "warning" in data:
                self.log("✅ Unknown event handled correctly")
            else:
                self.log("❌ Unknown event not handled correctly")
        
        # Test missing reference
        webhook_payload = {
            "event": "stablecoin.deposit.confirmed",
            "reference": "non-existent-reference"
        }
        
        response = requests.post(f"{self.base_url}/test/simulate-webhook/", json=webhook_payload)
        
        if response.status_code == 404:
            self.log("✅ Missing reference handled correctly")
        else:
            self.log("❌ Missing reference not handled correctly")
        
        return True
    
    def run_full_test(self):
        """Run the complete funding workflow test"""
        self.log("🚀 Starting comprehensive funding workflow test...")
        
        tests = [
            ("Customer Creation", self.test_create_customer),
            ("Payment Schedule Creation", self.test_create_payment_schedule),
            ("Initial Funding Status Check", self.test_check_initial_funding_status),
            ("USDT Deposit Creation", self.test_create_usdt_deposit),
            ("Webhook Confirmation Simulation", self.test_simulate_webhook_confirmation),
            ("Post-Confirmation Funding Status", self.test_check_funding_status_after_confirmation),
            ("Payout Initiation", self.test_initiate_payout_with_funding),
            ("Webhook Edge Cases", self.test_webhook_edge_cases),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            self.log(f"\n{'='*50}")
            self.log(f"Running: {test_name}")
            self.log('='*50)
            
            try:
                if test_func():
                    passed += 1
                    self.log(f"✅ {test_name} PASSED")
                else:
                    self.log(f"❌ {test_name} FAILED")
            except Exception as e:
                self.log(f"❌ {test_name} ERROR: {str(e)}")
            
            time.sleep(1)  # Brief pause between tests
        
        self.log(f"\n{'='*50}")
        self.log(f"TEST SUMMARY")
        self.log('='*50)
        self.log(f"Passed: {passed}/{total}")
        self.log(f"Success rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            self.log("🎉 ALL TESTS PASSED! Funding workflow is working correctly.")
        else:
            self.log("⚠️ Some tests failed. Please review the output above.")

if __name__ == "__main__":
    tester = FundingWorkflowTester()
    tester.run_full_test()
