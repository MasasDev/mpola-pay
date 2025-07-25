# views.py
import requests
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.db.models import Sum
from .serializers import (
    CustomerCreateSerializer, 
    ReceiverCreateSerializer, 
    PaymentScheduleCreateSerializer,
    PaymentScheduleSerializer
)
from django.conf import settings
from .models import BitnobCustomer, MobileTransaction, MobileReceiver, PaymentSchedule
from .services.bitnob import lookup_mobile, request_mobile_invoice, pay_mobile_invoice

from .models import PaymentSchedule, FundTransaction
import uuid




BITNOB_BASE = "https://sandboxapi.bitnob.co/api/v1"
HEADERS = {
    "Authorization": f"Bearer {settings.BITNOB_API_KEY}",
    "Content-Type": "application/json",
    "Accept": "application/json",
}

class CreateBitnobCustomer(APIView):
    def post(self, request):
        serializer = CustomerCreateSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            
            # Check if customer already exists locally
            existing_customer = BitnobCustomer.objects.filter(email=data["email"]).first()
            if existing_customer:
                return Response({
                    "message": "Customer already exists", 
                    "bitnob_id": existing_customer.bitnob_id
                }, status=200)
            
            # Prepare payload for Bitnob
            payload = {
                "email": data["email"],
                "firstName": data["firstName"],
                "lastName": data["lastName"],
                "phone": data["phone"],
                "countryCode": data["countryCode"],
            }
            
            try:
                # Call Bitnob API
                res = requests.post(f"{BITNOB_BASE}/customers", headers=HEADERS, json=payload)
                
                # Check if Bitnob API was successful (200 or 201)
                if res.status_code in [200, 201]:
                    response_data = res.json()
                    
                    # Check if the response indicates success
                    if response_data.get('status') == True and 'data' in response_data:
                        customer_id = response_data['data']['id']
                        customer_id = response_data['data']['id']
                        
                        # Create local customer object (but don't save yet)
                        customer = BitnobCustomer(
                            email=data["email"],
                            first_name=data["firstName"],
                            last_name=data["lastName"],
                            phone=data["phone"],
                            country_code=data["countryCode"],
                            bitnob_id=customer_id
                        )
                        
                        try:
                            # Save to local database
                            customer.save()
                            return Response({
                                "message": "Customer created successfully", 
                                "bitnob_id": customer_id,
                                "local_id": customer.id
                            }, status=201)
                        
                        except Exception as db_error:
                            # Local save failed - we should handle this
                            # Option 1: Log error and return the Bitnob customer ID anyway
                            # Option 2: Try to delete from Bitnob (if they have delete API)
                            return Response({
                                "error": "Customer created in Bitnob but failed to save locally",
                                "bitnob_id": customer_id,
                                "detail": str(db_error)
                            }, status=500)
                    
                    else:
                        # Bitnob API returned success status but no data
                        return Response({
                            "error": "Unexpected response from Bitnob API",
                            "detail": response_data
                        }, status=500)
                
                else:
                    # Bitnob API failed
                    return Response({
                        "error": "Failed to create customer in Bitnob",
                        "detail": res.json()
                    }, status=res.status_code)
                    
            except requests.exceptions.RequestException as api_error:
                # Network or API error
                return Response({
                    "error": "Failed to connect to Bitnob API",
                    "detail": str(api_error)
                }, status=500)
                
        return Response(serializer.errors, status=400)

class CreatePaymentPlan(APIView):
    def post(self, request):
        serializer = PaymentScheduleCreateSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            
            try:
                customer = BitnobCustomer.objects.get(email=data["email"])
            except BitnobCustomer.DoesNotExist:
                return Response({"error": "Customer not found"}, status=404)

            # Calculate total amount across all receivers
            subtotal_amount = 0
            receivers_data = data["receivers"]
            
            # Validate receivers data and calculate subtotal
            phone_numbers_in_schedule = set()
            for r in receivers_data:
                try:
                    amount_per_installment = float(r["amountPerInstallment"])
                    number_of_installments = int(r["numberOfInstallments"])
                    subtotal_amount += amount_per_installment * number_of_installments
                    
                    # Check for duplicate phone numbers within this payment schedule
                    phone = str(r["phone"]).strip()
                    if phone in phone_numbers_in_schedule:
                        return Response({
                            "error": f"Duplicate phone number {phone} found in payment schedule. Each phone number can only appear once per schedule.",
                            "detail": "Phone numbers must be unique within a payment schedule"
                        }, status=400)
                    phone_numbers_in_schedule.add(phone)
                    
                except (ValueError, TypeError) as e:
                    return Response({
                        "error": f"Invalid amount or installments for receiver {r.get('name', 'Unknown')}",
                        "detail": str(e)
                    }, status=400)

            # Add 1.5% processing fee
            processing_fee = subtotal_amount * 0.015
            total_amount = subtotal_amount + processing_fee

            try:
                # Create the payment schedule with proper start_date handling
                start_date = data.get("start_date")
                if not start_date:
                    start_date = timezone.now()
                    
                payment_schedule = PaymentSchedule.objects.create(
                    customer=customer,
                    title=data["title"],
                    description=data.get("description", ""),
                    frequency=data.get("frequency", "monthly"),
                    subtotal_amount=subtotal_amount,
                    processing_fee=round(processing_fee, 2),
                    total_amount=round(total_amount, 2),
                    start_date=start_date
                )

                # Create receivers for this payment schedule
                created_receivers = []
                for r in receivers_data:
                    try:
                        # Validate phone number format
                        phone = str(r["phone"]).strip()
                        country_code = str(r["countryCode"]).strip()
                        
                        if not phone or not country_code:
                            raise ValueError("Phone number and country code are required")
                        
                        receiver = MobileReceiver.objects.create(
                            payment_schedule=payment_schedule,
                            customer=customer,
                            name=r["name"],
                            phone=phone,
                            country_code=country_code,
                            amount_per_installment=r["amountPerInstallment"],
                            number_of_installments=r["numberOfInstallments"]
                        )
                        created_receivers.append({
                            "id": receiver.id,
                            "name": receiver.name,
                            "phone": receiver.phone,
                            "country_code": receiver.country_code,
                            "total_amount": str(receiver.total_amount),
                            "amount_per_installment": str(receiver.amount_per_installment),
                            "installments": receiver.number_of_installments
                        })
                    except Exception as receiver_error:
                        # If receiver creation fails, clean up the payment schedule
                        payment_schedule.delete()
                        
                        # Check if it's a duplicate phone number error
                        if "UNIQUE constraint failed" in str(receiver_error) or "unique_together" in str(receiver_error).lower():
                            return Response({
                                "error": f"Phone number {phone} is already used in this payment schedule",
                                "detail": "Each phone number can only appear once per payment schedule"
                            }, status=400)
                        
                        return Response({
                            "error": f"Failed to create receiver {r.get('name', 'Unknown')}",
                            "detail": str(receiver_error)
                        }, status=400)

                # Return payment schedule details
                schedule_serializer = PaymentScheduleSerializer(payment_schedule)
                return Response({
                    "message": "Payment schedule created successfully",
                    "payment_schedule": schedule_serializer.data,
                    "receivers": created_receivers,
                    "financial_summary": {
                        "subtotal_amount": str(subtotal_amount),
                        "processing_fee": str(round(processing_fee, 2)),
                        "processing_fee_percentage": "1.5%",
                        "total_amount": str(round(total_amount, 2))
                    },
                    "total_receivers": len(created_receivers)
                }, status=201)
                
            except Exception as schedule_error:
                return Response({
                    "error": "Failed to create payment schedule",
                    "detail": str(schedule_error)
                }, status=500)
                
        return Response(serializer.errors, status=400)


class PaymentScheduleListView(APIView):
    """View to list all payment schedules for a customer or all schedules"""
    def get(self, request):
        customer_email = request.query_params.get('customer_email')
        status_filter = request.query_params.get('status')
        
        queryset = PaymentSchedule.objects.all()
        
        if customer_email:
            try:
                customer = BitnobCustomer.objects.get(email=customer_email)
                queryset = queryset.filter(customer=customer)
            except BitnobCustomer.DoesNotExist:
                return Response({"error": "Customer not found"}, status=404)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        serializer = PaymentScheduleSerializer(queryset, many=True)
        return Response({
            "payment_schedules": serializer.data,
            "count": len(serializer.data)
        })


class PaymentScheduleDetailView(APIView):
    """View to get, update, or delete a specific payment schedule"""
    def get(self, request, schedule_id):
        try:
            schedule = PaymentSchedule.objects.get(id=schedule_id)
        except PaymentSchedule.DoesNotExist:
            return Response({"error": "Payment schedule not found"}, status=404)
        
        serializer = PaymentScheduleSerializer(schedule)
        
        # Also include receivers and their transactions
        receivers = schedule.receivers.all()
        receivers_data = []
        for receiver in receivers:
            receiver_data = {
                "id": receiver.id,
                "name": receiver.name,
                "phone": receiver.phone,
                "amount_per_installment": str(receiver.amount_per_installment),
                "number_of_installments": receiver.number_of_installments,
                "completed_installments": receiver.completed_installments,
                "progress_percentage": receiver.progress_percentage,
                "transactions": [
                    {
                        "id": txn.id,
                        "installment_number": txn.installment_number,
                        "amount": str(txn.amount),
                        "status": txn.status,
                        "sent_at": txn.sent_at,
                        "completed_at": txn.completed_at,
                        "reference": txn.reference
                    }
                    for txn in receiver.transactions.order_by('installment_number')
                ]
            }
            receivers_data.append(receiver_data)
        
        return Response({
            "payment_schedule": serializer.data,
            "receivers": receivers_data
        })
    
    def patch(self, request, schedule_id):
        """Update payment schedule status or other fields"""
        try:
            schedule = PaymentSchedule.objects.get(id=schedule_id)
        except PaymentSchedule.DoesNotExist:
            return Response({"error": "Payment schedule not found"}, status=404)
        
        # Allow updating status, title, description
        allowed_fields = ['status', 'title', 'description']
        for field in allowed_fields:
            if field in request.data:
                setattr(schedule, field, request.data[field])
        
        schedule.save()
        serializer = PaymentScheduleSerializer(schedule)
        return Response({
            "message": "Payment schedule updated successfully",
            "payment_schedule": serializer.data
        })


class InitiatePayout(APIView):
    def post(self, request):
        r = request.data
        
        # Validate required fields - now only need receiverId and senderName
        required_fields = ["receiverId", "senderName"]
        for field in required_fields:
            if field not in r or not r[field]:
                return Response({"error": f"Missing required field: {field}"}, status=400)
        
        receiver_id = r["receiverId"]
        sender = r["senderName"]
        
        # Get the receiver directly by ID
        try:
            receiver = MobileReceiver.objects.get(id=receiver_id)
        except MobileReceiver.DoesNotExist:
            return Response({"error": "Receiver not found"}, status=404)
        
        # Check if the schedule has enough funding for this specific installment
        schedule = receiver.payment_schedule
        installment_amount = receiver.amount_per_installment
        
        # Check if there's enough funding for this specific installment
        if not schedule.has_sufficient_funds_for_amount(installment_amount):
            return Response({
                "error": "Insufficient available balance for this installment",
                "funding_details": {
                    "installment_amount": str(installment_amount),
                    "available_balance": str(schedule.available_balance),
                    "total_funded": str(schedule.total_funded_amount),
                    "total_payments_made": str(schedule.total_payments_made),
                    "total_required_for_schedule": str(schedule.total_amount),
                    "shortfall": str(schedule.funding_shortfall),
                    "is_fully_funded": schedule.is_adequately_funded
                },
                "schedule_id": str(schedule.id),
                "schedule_title": schedule.title
            }, status=400)
        
        # Extract phone and country info from receiver
        country = receiver.country_code
        number = receiver.phone
        
        # Use receiver's amount per installment as the payment amount
        amount = int(float(receiver.amount_per_installment) * 100)  # Convert to cents

        # Check if receiver has completed all installments
        if receiver.completed_installments >= receiver.number_of_installments:
            return Response({
                "error": "All installments for this receiver have been completed"
            }, status=400)

        # Check if the payment is due based on schedule timing
        can_pay, timing_message = receiver.can_receive_next_installment()
        if not can_pay:
            payment_info = receiver.get_next_payment_info()
            return Response({
                "error": "Payment not allowed at this time",
                "reason": timing_message,
                "payment_schedule_info": {
                    "frequency": payment_info["schedule_frequency"],
                    "next_payment_date": payment_info["next_payment_date"],
                    "current_time": payment_info["current_time"],
                    "time_until_next_payment_seconds": payment_info["time_until_next_payment"],
                    "next_installment_number": payment_info["next_installment_number"]
                }
            }, status=400)

        # 1. Optional lookup (skip if not supported)
        try:
            lookup = lookup_mobile(country, number)
            if not lookup.get("status"):
                print(f"Warning: Lookup failed for {country} {number}, but continuing with payment: {lookup}")
        except Exception as e:
            print(f"Warning: Lookup exception for {country} {number}, but continuing with payment: {str(e)}")

        # 2. Request invoice
        invoice = request_mobile_invoice(country, number, sender, amount, callback_url=None)
        if not invoice.get("status"):
            return Response({"error": "Invoice failed", "detail": invoice}, status=400)

        ref = invoice["data"]["reference"]
        payment_req = invoice["data"]["paymentRequest"]

        # 3. Record transaction and pay
        next_installment = receiver.next_installment()
        
        # Check if this installment already exists
        existing_txn = MobileTransaction.objects.filter(
            receiver=receiver, 
            installment_number=next_installment
        ).first()
        
        if existing_txn and existing_txn.status in ['pending', 'processing', 'success']:
            return Response({
                "error": f"Installment {next_installment} already exists with status: {existing_txn.status}",
                "transaction_id": existing_txn.id
            }, status=400)

        try:
            txn = MobileTransaction.objects.create(
                receiver=receiver, 
                amount=amount/100,  # Convert back to original amount
                installment_number=next_installment,
                sent_at=timezone.now()
            )
            
            # Use the receiver's customer email for the payment
            customer_email = receiver.customer.email
            pay = pay_mobile_invoice(customer_email, ref, wallet="USD")
            if not pay.get("status"):
                txn.status = "failed"
                txn.failure_reason = pay.get("message", "Payment failed")
            else:
                txn.status = "processing"
                
            txn.reference = ref
            txn.save()

            return Response({
                "message": "Payout initiated successfully",
                "reference": ref, 
                "paymentRequest": payment_req, 
                "transactionId": txn.id,
                "installment_number": next_installment,
                "amount": str(amount/100),
                "receiver": {
                    "id": receiver.id,
                    "name": receiver.name,
                    "phone": receiver.phone,
                    "country_code": receiver.country_code
                },
                "customer": {
                    "email": receiver.customer.email,
                    "name": f"{receiver.customer.first_name} {receiver.customer.last_name}"
                },
                "payment_schedule": {
                    "id": str(receiver.payment_schedule.id),
                    "title": receiver.payment_schedule.title
                }
            }, status=201)
            
        except Exception as e:
            return Response({
                "error": "Failed to create transaction",
                "detail": str(e)
            }, status=500)


@api_view(['POST'])
@csrf_exempt
def bitnob_webhook(request):
    """Handle Bitnob webhook notifications for transaction status updates"""
    data = request.data
    event = data.get("event")
    ref = data.get("reference")
    
    # Validate required fields
    if not event or not ref:
        return Response({
            "error": "Missing required fields: event or reference"
        }, status=400)

    # Handle stablecoin/funding transaction webhooks
    if event.startswith("stablecoin"):
        return handle_fund_transaction_webhook(data, event, ref)
    
    # Handle mobile payment transaction webhooks
    try:
        txn = MobileTransaction.objects.get(reference=ref)
    except MobileTransaction.DoesNotExist:
        return Response({
            "error": "Transaction not found",
            "reference": ref
        }, status=404)

    # Store original status for logging
    original_status = txn.status
    
    # Update transaction status based on webhook event
    if event == "mobilepayment.settlement.success":
        txn.status = "success"
        txn.completed_at = timezone.now()
        
        # Update the payment schedule's payment dates when a transaction succeeds
        schedule = txn.receiver.payment_schedule
        schedule.update_payment_dates()
        
    elif event == "mobilepayment.settlement.failed":
        txn.status = "failed"
        txn.failure_reason = data.get("message", "Payment failed via webhook")
    elif event == "mobilepayment.settlement.pending":
        txn.status = "pending"
    else:
        # Log unknown event but don't update status
        return Response({
            "warning": f"Unknown event type: {event}",
            "status": "received"
        })
    
    txn.save()
    
    # Log the status change for debugging
    print(f"Webhook: Transaction {txn.id} status changed from {original_status} to {txn.status}")
    
    return Response({
        "status": "received",
        "transaction_id": txn.id,
        "old_status": original_status,
        "new_status": txn.status,
        "event": event
    })


def handle_fund_transaction_webhook(data, event, ref):
    """Handle stablecoin/funding transaction webhook events"""
    try:
        fund_txn = FundTransaction.objects.get(reference=ref)
    except FundTransaction.DoesNotExist:
        return Response({
            "error": "Fund transaction not found",
            "reference": ref
        }, status=404)

    # Store original status for logging
    original_status = fund_txn.status
    
    # Update fund transaction status based on webhook event
    if event in [
        "stablecoin.settlement.success", 
        "stablecoin.deposit.confirmed",
        "stablecoin.transaction.confirmed",
        "deposit.confirmed"
    ]:
        fund_txn.status = "paid"
        fund_txn.updated_at = timezone.now()
        
        # Update the associated payment schedule funding status
        schedule = fund_txn.schedule
        schedule.update_funding_status()
        
        # Log successful funding
        print(f"Fund Webhook: Schedule {schedule.id} funded. Total funded: {schedule.total_funded_amount}")
        
    elif event in [
        "stablecoin.settlement.failed", 
        "stablecoin.deposit.failed",
        "stablecoin.transaction.failed",
        "deposit.failed"
    ]:
        fund_txn.status = "failed"
        fund_txn.updated_at = timezone.now()
        
        # Log failure reason if provided
        failure_reason = data.get("message", "Funding failed via webhook")
        print(f"Fund Webhook: Transaction {fund_txn.id} failed: {failure_reason}")
        
    elif event in [
        "stablecoin.settlement.expired", 
        "stablecoin.deposit.expired",
        "stablecoin.transaction.expired",
        "deposit.expired"
    ]:
        fund_txn.status = "expired"
        fund_txn.updated_at = timezone.now()
        
    elif event in [
        "stablecoin.settlement.pending",
        "stablecoin.deposit.pending", 
        "deposit.pending"
    ]:
        fund_txn.status = "pending"
        fund_txn.updated_at = timezone.now()
        
    else:
        # Log unknown stablecoin event but don't update status
        print(f"Unknown stablecoin event: {event} for reference: {ref}")
        return Response({
            "warning": f"Unknown stablecoin event type: {event}",
            "status": "received",
            "reference": ref
        })
    
    fund_txn.save()
    
    # Log the status change for debugging
    print(f"Fund Webhook: Transaction {fund_txn.id} status changed from {original_status} to {fund_txn.status}")
    
    return Response({
        "status": "received",
        "fund_transaction_id": str(fund_txn.id),
        "schedule_id": str(fund_txn.schedule.id),
        "old_status": original_status,
        "new_status": fund_txn.status,
        "event": event,
        "schedule_funding_status": {
            "is_funded": fund_txn.schedule.is_funded,
            "total_funded": str(fund_txn.schedule.total_funded_amount),
            "total_required": str(fund_txn.schedule.total_amount),
            "shortfall": str(fund_txn.schedule.funding_shortfall)
        }
    })


@api_view(['GET'])
def get_schedule_progress(request, receiver_id):
    """Get the progress of a payment schedule for a receiver"""
    try:
        receiver = MobileReceiver.objects.get(id=receiver_id)
    except MobileReceiver.DoesNotExist:
        return Response({"error": "Receiver not found"}, status=404)
    
    transactions = receiver.transactions.all()
    total_installments = receiver.number_of_installments
    completed_installments = transactions.filter(status="success").count()
    pending_installments = transactions.filter(status="pending").count()
    failed_installments = transactions.filter(status="failed").count()
    
    total_amount = receiver.amount_per_installment * receiver.number_of_installments
    completed_amount = receiver.amount_per_installment * completed_installments
    
    progress_data = {
        "receiver_id": receiver.id,
        "receiver_name": receiver.name,
        "receiver_phone": receiver.phone,
        "total_installments": total_installments,
        "completed_installments": completed_installments,
        "pending_installments": pending_installments,
        "failed_installments": failed_installments,
        "total_amount": str(total_amount),
        "completed_amount": str(completed_amount),
        "progress_percentage": round((completed_installments / total_installments) * 100, 2) if total_installments > 0 else 0,
        "transactions": [
            {
                "id": txn.id,
                "installment_number": txn.installment_number,
                "amount": str(txn.amount),
                "status": txn.status,
                "sent_at": txn.sent_at
            }
            for txn in transactions.order_by('installment_number')
        ]
    }
    
    return Response(progress_data)


class CreateUSDTDepositView(APIView):
    def post(self, request, schedule_id):
        network = request.data.get("network", "TRON").upper()
        
        # Validate network
        allowed_networks = ["TRON", "ETHEREUM", "BSC", "POLYGON"]
        if network not in allowed_networks:
            return Response({
                "error": f"Unsupported network: {network}",
                "allowed_networks": allowed_networks
            }, status=400)
        
        try:
            schedule = PaymentSchedule.objects.get(id=schedule_id)
        except PaymentSchedule.DoesNotExist:
            return Response({"error": "Payment schedule not found"}, status=404)

        # Check if schedule is already fully funded
        if schedule.is_adequately_funded:
            return Response({
                "error": "Payment schedule is already adequately funded",
                "funding_details": {
                    "required": str(schedule.total_amount),
                    "funded": str(schedule.total_funded_amount),
                    "excess": str(schedule.total_funded_amount - schedule.total_amount)
                }
            }, status=400)

        # Check for existing pending transactions
        pending_transactions = FundTransaction.objects.filter(
            schedule=schedule, 
            status="pending"
        )
        if pending_transactions.exists():
            pending_txn = pending_transactions.first()
            return Response({
                "error": "A pending fund transaction already exists for this schedule.",
                "existing_transaction": {
                    "id": str(pending_txn.id),
                    "reference": pending_txn.reference,
                    "amount": str(pending_txn.amount),
                    "created_at": pending_txn.created_at,
                    "deposit_address": pending_txn.stablecoin_address,
                    "network": pending_txn.stablecoin_network,
                    "usdt_required": str(pending_txn.usdt_required)
                }
            }, status=400)

        # Calculate remaining amount needed
        remaining_amount = schedule.funding_shortfall

        # 1. Get UGX to USD rate (with fallback for testing)
        try:
            rate_resp = requests.get(f"{BITNOB_BASE}/exchange-rates", headers=HEADERS)
            rate_resp.raise_for_status()
            rate_data = rate_resp.json().get("data", [])
            ugx_rate = next((item["rate"] for item in rate_data if item["currency"] == "UGX"), None)
            
            if not ugx_rate:
                raise ValueError("UGX rate not found in response")
                
        except Exception as e:
            # Fallback rate for testing (approximate UGX to USD rate)
            print(f"Warning: Using fallback exchange rate due to API error: {str(e)}")
            ugx_rate = 3700  # Approximate UGX to USD rate for testing
            print(f"Using fallback UGX rate: {ugx_rate}")

        usd_amount = float(remaining_amount) / float(ugx_rate)
        usdt_amount = round(usd_amount, 6)

        # 2. Generate deposit address (with mock for testing)
        try:
            addr_resp = requests.post(
                f"{BITNOB_BASE}/stablecoins/generate-address",
                headers=HEADERS,
                json={"currency": "USDT", "network": network}
            )
            addr_resp.raise_for_status()
            address_data = addr_resp.json()
            
            if not address_data.get("status") or "data" not in address_data:
                raise ValueError(f"Invalid response: {address_data}")
                
            address = address_data["data"]["address"]
            
        except Exception as e:
            # Generate a mock address for testing
            print(f"Warning: Using mock deposit address due to API error: {str(e)}")
            mock_addresses = {
                "TRON": "TQMfFzQQQQQQQQQQQQQQQQQQQQQQQQTest",
                "ETHEREUM": "0x1234567890123456789012345678901234567890",
                "BSC": "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd",
                "POLYGON": "0x9876543210987654321098765432109876543210"
            }
            address = mock_addresses.get(network, "mock_address_for_testing")

        # 3. Save FundTransaction
        ref = str(uuid.uuid4())
        fund_txn = FundTransaction.objects.create(
            schedule=schedule,
            reference=ref,
            amount=remaining_amount,  # Only the remaining amount needed
            currency="UGX",
            stablecoin_address=address,
            stablecoin_network=network,
            usdt_required=usdt_amount,
            status="pending"
        )

        return Response({
            "message": "Funding transaction created successfully.",
            "funding_details": {
                "reference": fund_txn.reference,
                "network": network,
                "usdt_required": str(usdt_amount),
                "ugx_amount": str(remaining_amount),
                "usd_rate": str(ugx_rate),
                "deposit_address": address
            },
            "schedule_info": {
                "id": str(schedule.id),
                "title": schedule.title,
                "total_required": str(schedule.total_amount),
                "already_funded": str(schedule.total_funded_amount),
                "remaining_needed": str(remaining_amount)
            },
            "instructions": {
                "step_1": f"Send exactly {usdt_amount} USDT to the address below",
                "step_2": "Use the correct network (TRC20 for TRON, ERC20 for Ethereum, etc.)",
                "step_3": "Wait for confirmation (usually 1-5 minutes)",
                "step_4": "Your payment schedule will be automatically activated when funds are confirmed"
            }
        }, status=201)


@api_view(['GET'])
def get_funding_status(request, schedule_id):
    """Get detailed funding status for a payment schedule"""
    try:
        schedule = PaymentSchedule.objects.get(id=schedule_id)
    except PaymentSchedule.DoesNotExist:
        return Response({"error": "Payment schedule not found"}, status=404)
    
    # Get all fund transactions for this schedule
    fund_transactions = schedule.fund_transactions.all().order_by('-created_at')
    
    transactions_data = []
    for txn in fund_transactions:
        transactions_data.append({
            "id": str(txn.id),
            "reference": txn.reference,
            "amount": str(txn.amount),
            "currency": txn.currency,
            "status": txn.status,
            "usdt_required": str(txn.usdt_required) if txn.usdt_required else None,
            "stablecoin_address": txn.stablecoin_address,
            "stablecoin_network": txn.stablecoin_network,
            "created_at": txn.created_at,
            "updated_at": txn.updated_at
        })
    
    return Response({
        "schedule": {
            "id": str(schedule.id),
            "title": schedule.title,
            "total_amount": str(schedule.total_amount),
            "currency": "UGX"
        },
        "funding_summary": {
            "total_required": str(schedule.total_amount),
            "total_funded": str(schedule.total_funded_amount),
            "total_payments_made": str(schedule.total_payments_made),
            "available_balance": str(schedule.available_balance),
            "shortfall": str(schedule.funding_shortfall),
            "is_adequately_funded": schedule.is_adequately_funded,
            "is_funded_flag": schedule.is_funded,
            "funding_percentage": round((schedule.total_funded_amount / schedule.total_amount * 100), 2) if schedule.total_amount > 0 else 0
        },
        "fund_transactions": transactions_data,
        "transaction_count": len(transactions_data)
    })


@api_view(['POST'])
def manual_fund_confirmation(request, fund_transaction_id):
    """Manually confirm a fund transaction (admin use)"""
    try:
        fund_txn = FundTransaction.objects.get(id=fund_transaction_id)
    except FundTransaction.DoesNotExist:
        return Response({"error": "Fund transaction not found"}, status=404)
    
    if fund_txn.status == "paid":
        return Response({
            "message": "Transaction already confirmed",
            "status": fund_txn.status
        })
    
    # Manually mark as paid
    original_status = fund_txn.status
    fund_txn.status = "paid"
    fund_txn.updated_at = timezone.now()
    fund_txn.save()
    
    # Update schedule funding status
    schedule = fund_txn.schedule
    schedule.update_funding_status()
    
    return Response({
        "message": "Fund transaction manually confirmed",
        "fund_transaction_id": str(fund_txn.id),
        "old_status": original_status,
        "new_status": fund_txn.status,
        "schedule_funding_status": {
            "is_funded": schedule.is_funded,
            "total_funded": str(schedule.total_funded_amount),
            "total_required": str(schedule.total_amount)
        }
    })


@csrf_exempt
@api_view(['POST'])
def test_simulate_webhook(request):
    """Test endpoint to simulate webhook confirmation (for testing only)"""
    fund_reference = request.data.get('reference')
    event = request.data.get('event', 'stablecoin.deposit.confirmed')
    
    if not fund_reference:
        return Response({"error": "Reference is required"}, status=400)
    
    # Simulate the webhook call
    webhook_data = {
        "event": event,
        "reference": fund_reference,
        "message": "Test webhook simulation",
        "network": "TRON"
    }
    
    # Call our webhook handler
    return handle_fund_transaction_webhook(webhook_data, event, fund_reference)


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def trigger_scheduled_payments(request):
    """Manually trigger scheduled payments processing"""
    schedule_id = request.data.get('schedule_id')
    
    # For demo purposes, let's try to call the task directly if Celery is not available
    try:
        from mpola.tasks import process_scheduled_payments
        
        if schedule_id:
            from mpola.tasks import process_schedule_payments
            result = process_schedule_payments.delay(schedule_id)
            return Response({
                "message": f"Queued specific schedule for processing: {schedule_id}",
                "task_id": result.id,
                "schedule_id": schedule_id
            })
        else:
            result = process_scheduled_payments.delay()
            return Response({
                "message": "Queued all scheduled payments for processing",
                "task_id": result.id
            })
    except Exception as celery_error:
        # If Celery is not available, run the task synchronously for demo
        try:
            from mpola.tasks import process_scheduled_payments, process_schedule_payments
            
            if schedule_id:
                # Import the actual function without using .delay()
                result = process_schedule_payments(schedule_id)
                return Response({
                    "message": f"Processed specific schedule directly (Celery unavailable): {schedule_id}",
                    "result": result,
                    "schedule_id": schedule_id,
                    "note": "Executed synchronously - Celery broker not available"
                })
            else:
                result = process_scheduled_payments()
                return Response({
                    "message": "Processed all scheduled payments directly (Celery unavailable)",
                    "result": result,
                    "note": "Executed synchronously - Celery broker not available"
                })
        except Exception as task_error:
            return Response({
                "error": "Failed to process scheduled payments",
                "celery_error": str(celery_error),
                "task_error": str(task_error),
                "note": "Both Celery queuing and direct execution failed"
            }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
@csrf_exempt
def get_scheduled_payments_status(request):
    """Get status of scheduled payments"""
    from payments.models import PaymentSchedule, MobileTransaction
    from django.db.models import Count, Q
    
    # Get all active, funded schedules
    active_schedules = PaymentSchedule.objects.filter(
        status='active',
        is_funded=True
    )
    
    schedule_summaries = []
    
    for schedule in active_schedules:
        # Get transaction counts
        total_transactions = MobileTransaction.objects.filter(
            receiver__payment_schedule=schedule
        ).count()
        
        pending_transactions = MobileTransaction.objects.filter(
            receiver__payment_schedule=schedule,
            status__in=['pending', 'processing']
        ).count()
        
        successful_transactions = MobileTransaction.objects.filter(
            receiver__payment_schedule=schedule,
            status='success'
        ).count()
        
        failed_transactions = MobileTransaction.objects.filter(
            receiver__payment_schedule=schedule,
            status='failed'
        ).count()
        
        # Calculate expected total transactions
        expected_total = sum(receiver.number_of_installments for receiver in schedule.receivers.all())
        
        schedule_summaries.append({
            "schedule_id": str(schedule.id),
            "title": schedule.title,
            "frequency": schedule.frequency,
            "is_funded": schedule.is_funded,
            "next_payment_date": schedule.next_payment_date,
            "last_payment_date": schedule.last_payment_date,
            "is_payment_due": schedule.is_payment_due(),
            "total_receivers": schedule.receivers.count(),
            "expected_total_transactions": expected_total,
            "actual_total_transactions": total_transactions,
            "pending_transactions": pending_transactions,
            "successful_transactions": successful_transactions,
            "failed_transactions": failed_transactions,
            "completion_percentage": round((successful_transactions / expected_total * 100), 2) if expected_total > 0 else 0,
            "created_at": schedule.created_at,
            "funding_status": {
                "total_required": str(schedule.total_amount),
                "total_funded": str(schedule.total_funded_amount),
                "is_adequately_funded": schedule.is_adequately_funded
            }
        })
    
    return Response({
        "active_schedules_count": len(schedule_summaries),
        "schedules": schedule_summaries,
        "summary": {
            "total_schedules": len(schedule_summaries),
            "total_pending": sum(s["pending_transactions"] for s in schedule_summaries),
            "total_successful": sum(s["successful_transactions"] for s in schedule_summaries),
            "total_failed": sum(s["failed_transactions"] for s in schedule_summaries),
        },
        "current_time": timezone.now()
    })


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def create_test_schedule(request):
    """Create a test payment schedule with 2-minute frequency for testing"""
    # Get or create a test customer
    test_customer, created = BitnobCustomer.objects.get_or_create(
        email="test@example.com",
        defaults={
            "first_name": "Test",
            "last_name": "User",
            "phone": "+256700000000",
            "country_code": "UG",
            "bitnob_id": "test_customer_id"
        }
    )
    
    # Create test payment schedule with 2-minute frequency
    schedule = PaymentSchedule.objects.create(
        customer=test_customer,
        title="Test 30-Second Schedule",
        description="Test schedule with 30-second intervals for testing",
        frequency="test_30sec",
        subtotal_amount=1000,
        processing_fee=15,
        total_amount=1015,
        start_date=timezone.now(),
        is_funded=True  # Mark as funded for testing
    )
    
    # Create test receiver
    receiver = MobileReceiver.objects.create(
        payment_schedule=schedule,
        customer=test_customer,
        name="Test Receiver",
        phone="+256700000001",
        country_code="UG",
        amount_per_installment=100,
        number_of_installments=10
    )
    
    # Create a mock fund transaction to make the schedule actually funded
    from .models import FundTransaction
    import uuid
    fund_txn = FundTransaction.objects.create(
        schedule=schedule,
        reference=str(uuid.uuid4()),
        amount=1015,  # Full amount
        currency="UGX",
        status="paid"  # Mark as paid
    )
    
    return Response({
        "message": "Test schedule created successfully",
        "schedule": {
            "id": str(schedule.id),
            "title": schedule.title,
            "frequency": schedule.frequency,
            "next_payment_date": schedule.next_payment_date,
            "is_payment_due": schedule.is_payment_due(),
            "current_time": timezone.now()
        },
        "receiver": {
            "id": receiver.id,
            "name": receiver.name,
            "phone": receiver.phone,
            "can_receive_payment": receiver.can_receive_next_installment()
        }
    }, status=201)


@api_view(['GET'])
@permission_classes([AllowAny])
@csrf_exempt
def check_payment_timing(request, receiver_id):
    """Check if a receiver can receive a payment right now"""
    try:
        receiver = MobileReceiver.objects.get(id=receiver_id)
    except MobileReceiver.DoesNotExist:
        return Response({"error": "Receiver not found"}, status=404)
    
    can_pay, message = receiver.can_receive_next_installment()
    payment_info = receiver.get_next_payment_info()
    
    return Response({
        "receiver": {
            "id": receiver.id,
            "name": receiver.name,
            "phone": receiver.phone
        },
        "payment_status": {
            "can_pay_now": can_pay,
            "message": message,
            "next_installment_number": payment_info["next_installment_number"],
            "completed_installments": receiver.completed_installments,
            "total_installments": receiver.number_of_installments
        },
        "timing_info": {
            "schedule_frequency": payment_info["schedule_frequency"],
            "next_payment_date": payment_info["next_payment_date"],
            "current_time": payment_info["current_time"],
            "time_until_next_payment_seconds": payment_info["time_until_next_payment"],
            "is_payment_due": receiver.payment_schedule.is_payment_due()
        }
    })
