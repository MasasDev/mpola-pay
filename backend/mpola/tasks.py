# tasks.py
from celery import shared_task
from django.utils import timezone
from django.db import transaction
from datetime import datetime, timedelta
import logging
from payments.models import PaymentSchedule, MobileReceiver, MobileTransaction
from payments.services.bitnob import request_mobile_invoice, pay_mobile_invoice, create_and_pay_mobile_invoice

logger = logging.getLogger(__name__)

@shared_task
def process_scheduled_payments():
    """
    Main task to process all due scheduled payments
    This should be run periodically (e.g., every hour or daily)
    """
    logger.info("Starting scheduled payments processing...")
    
    # Get all active, funded schedules
    active_schedules = PaymentSchedule.objects.filter(
        status='active',
        is_funded=True
    )
    
    processed_count = 0
    success_count = 0
    error_count = 0
    
    for schedule in active_schedules:
        try:
            result = process_schedule_payments.delay(str(schedule.id))
            processed_count += 1
            logger.info(f"Queued schedule {schedule.id} for processing")
        except Exception as e:
            error_count += 1
            logger.error(f"Failed to queue schedule {schedule.id}: {str(e)}")
    
    logger.info(f"Scheduled payments processing complete. Processed: {processed_count}, Errors: {error_count}")
    return {
        "processed_schedules": processed_count,
        "errors": error_count,
        "timestamp": timezone.now().isoformat()
    }

@shared_task
def process_schedule_payments(schedule_id):
    """
    Process payments for a specific schedule
    """
    try:
        schedule = PaymentSchedule.objects.get(id=schedule_id)
    except PaymentSchedule.DoesNotExist:
        logger.error(f"Schedule {schedule_id} not found")
        return {"error": "Schedule not found"}
    
    logger.info(f"Processing payments for schedule: {schedule.title} ({schedule_id})")
    
    # Check if schedule is adequately funded
    if not schedule.is_adequately_funded:
        logger.warning(f"Schedule {schedule_id} is not adequately funded. Skipping.")
        return {"error": "Insufficient funding", "schedule_id": schedule_id}
    
    results = []
    
    # Process each receiver
    for receiver in schedule.receivers.all():
        try:
            result = process_receiver_payment.delay(receiver.id)
            results.append({
                "receiver_id": receiver.id,
                "receiver_name": receiver.name,
                "status": "queued"
            })
        except Exception as e:
            logger.error(f"Failed to queue receiver {receiver.id}: {str(e)}")
            results.append({
                "receiver_id": receiver.id,
                "receiver_name": receiver.name,
                "status": "error",
                "error": str(e)
            })
    
    return {
        "schedule_id": schedule_id,
        "schedule_title": schedule.title,
        "receivers_processed": len(results),
        "results": results,
        "timestamp": timezone.now().isoformat()
    }

@shared_task
def process_receiver_payment(receiver_id):
    """
    Process the next payment for a specific receiver
    """
    try:
        receiver = MobileReceiver.objects.get(id=receiver_id)
    except MobileReceiver.DoesNotExist:
        logger.error(f"Receiver {receiver_id} not found")
        return {"error": "Receiver not found"}
    
    # Check if receiver has completed all installments
    if receiver.completed_installments >= receiver.number_of_installments:
        logger.info(f"Receiver {receiver.name} has completed all installments")
        return {
            "receiver_id": receiver_id,
            "status": "completed",
            "message": "All installments completed"
        }
    
    # Check if there's already a pending/processing transaction
    next_installment = receiver.next_installment()
    existing_txn = MobileTransaction.objects.filter(
        receiver=receiver,
        installment_number=next_installment,
        status__in=['pending', 'processing']
    ).first()
    
    if existing_txn:
        logger.info(f"Receiver {receiver.name} already has a pending transaction for installment {next_installment}")
        return {
            "receiver_id": receiver_id,
            "status": "skipped",
            "message": f"Installment {next_installment} already pending",
            "transaction_id": existing_txn.id
        }
    
    # Determine if payment is due based on frequency
    if not is_payment_due(receiver):
        logger.info(f"Payment not yet due for receiver {receiver.name}")
        return {
            "receiver_id": receiver_id,
            "status": "not_due",
            "message": "Payment not yet due"
        }
    
    # Process the payment
    return initiate_automated_payment(receiver, next_installment)

def is_payment_due(receiver):
    """
    Check if a payment is due for a receiver based on schedule frequency
    """
    schedule = receiver.payment_schedule
    last_successful_txn = receiver.transactions.filter(status='success').order_by('-completed_at').first()
    
    if not last_successful_txn:
        # First payment is always due if funded
        return True
    
    # Calculate next due date based on frequency
    frequency = schedule.frequency.lower()
    last_payment_date = last_successful_txn.completed_at
    
    if frequency == 'weekly':
        next_due = last_payment_date + timedelta(weeks=1)
    elif frequency == 'monthly':
        next_due = last_payment_date + timedelta(days=30)  # Approximate
    elif frequency == 'quarterly':
        next_due = last_payment_date + timedelta(days=90)
    elif frequency == 'daily':
        next_due = last_payment_date + timedelta(days=1)
    else:
        # Default to monthly
        next_due = last_payment_date + timedelta(days=30)
    
    return timezone.now() >= next_due

def initiate_automated_payment(receiver, installment_number):
    """
    Initiate an automated payment for a receiver
    """
    try:
        with transaction.atomic():
            # Create transaction record
            amount = receiver.amount_per_installment
            amount_cents = int(float(amount) * 100)
            
            txn = MobileTransaction.objects.create(
                receiver=receiver,
                amount=amount,
                installment_number=installment_number,
                status="pending",
                sent_at=timezone.now()
            )
            
            logger.info(f"Created transaction {txn.id} for receiver {receiver.name}, installment {installment_number}")
            
            # Request invoice from Bitnob
            try:
                invoice = request_mobile_invoice(
                    country=receiver.country_code,
                    number=receiver.phone,
                    sender_name=f"Automated Payment - {receiver.payment_schedule.title}",
                    amount_cents=amount_cents,
                    callback_url=None
                )
                
                if not invoice.get("success"):
                    raise Exception(f"Invoice failed: {invoice}")
                
                ref = invoice["reference"]
                invoice_id = invoice["id"]
                
                # Pay the invoice
                customer_email = receiver.customer.email
                pay = pay_mobile_invoice(customer_email, reference=ref, invoice_id=invoice_id, wallet="USD")
                
                if not pay.get("status"):
                    txn.status = "failed"
                    txn.failure_reason = pay.get("message", "Payment failed")
                    logger.error(f"Payment failed for transaction {txn.id}: {pay}")
                else:
                    txn.status = "processing"
                    logger.info(f"Payment initiated successfully for transaction {txn.id}")
                
                txn.reference = ref
                txn.save()
                
                return {
                    "receiver_id": receiver.id,
                    "receiver_name": receiver.name,
                    "transaction_id": txn.id,
                    "installment_number": installment_number,
                    "amount": str(amount),
                    "status": txn.status,
                    "reference": ref,
                    "timestamp": timezone.now().isoformat()
                }
                
            except Exception as e:
                txn.status = "failed"
                txn.failure_reason = f"Automated payment error: {str(e)}"
                txn.save()
                logger.error(f"Failed to process payment for transaction {txn.id}: {str(e)}")
                
                return {
                    "receiver_id": receiver.id,
                    "receiver_name": receiver.name,
                    "transaction_id": txn.id,
                    "status": "failed",
                    "error": str(e),
                    "timestamp": timezone.now().isoformat()
                }
                
    except Exception as e:
        logger.error(f"Failed to create transaction for receiver {receiver.id}: {str(e)}")
        return {
            "receiver_id": receiver.id,
            "status": "error",
            "error": str(e),
            "timestamp": timezone.now().isoformat()
        }
