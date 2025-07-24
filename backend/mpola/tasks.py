# tasks.py
from celery import shared_task
from django.utils import timezone
from .models import PaymentSchedule, MobileTransaction
from .services.bitnob import request_mobile_invoice, pay_mobile_invoice

@shared_task
def process_due_payments():
    now = timezone.now()
    schedules = PaymentSchedule.objects.filter(next_run__lte=now, is_funded=True)

    for schedule in schedules:
        for receiver in schedule.receivers.all():
            amount_cents = int(receiver.amount * 100)
            invoice = request_mobile_invoice(
                country=receiver.contact[:3],  # Adjust if countryCode stored separately
                number=receiver.contact,
                sender_name=schedule.user.username,
                amount_cents=amount_cents,
            )
            if not invoice.get("status"):
                continue

            reference = invoice["data"]["reference"]
            payment_result = pay_mobile_invoice(schedule.user.email, reference)

            txn = MobileTransaction.objects.create(
                schedule=schedule,
                receiver=receiver,
                status="pending" if payment_result.get("status") else "failed",
                platform_cut=receiver.amount * 0.05,  # 5% fee
                amount=receiver.amount,
            )

        # Update next run
        schedule.next_run = schedule.next_run + schedule.interval
        schedule.save()
