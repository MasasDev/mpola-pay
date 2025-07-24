# views.py
import requests
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .serializers import (
    CustomerCreateSerializer, 
    ReceiverCreateSerializer, 
    PaymentScheduleCreateSerializer,
    PaymentScheduleSerializer
)
from django.conf import settings
from .models import BitnobCustomer, MobileTransaction, MobileReceiver, PaymentSchedule
from .services.bitnob import lookup_mobile, request_mobile_invoice, pay_mobile_invoice


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
                payment_schedule = PaymentSchedule.objects.create(
                    customer=customer,
                    title=data["title"],
                    description=data.get("description", ""),
                    frequency=data.get("frequency", "monthly"),
                    subtotal_amount=subtotal_amount,
                    processing_fee=round(processing_fee, 2),
                    total_amount=round(total_amount, 2),
                    start_date=data.get("start_date")  # This will use default if None
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

        # 1. Optional lookup
        lookup = lookup_mobile(country, number)
        if not lookup.get("status"):
            return Response({"error": "Lookup failed", "detail": lookup}, status=400)

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
