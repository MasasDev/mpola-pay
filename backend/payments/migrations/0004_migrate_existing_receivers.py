# Generated by Django 5.2.4 on 2025-07-24 13:15

from django.db import migrations
import uuid
from django.utils import timezone


def create_default_payment_schedules(apps, schema_editor):
    """
    Create default payment schedules for existing receivers that don't have one
    """
    MobileReceiver = apps.get_model('payments', 'MobileReceiver')
    PaymentSchedule = apps.get_model('payments', 'PaymentSchedule')
    BitnobCustomer = apps.get_model('payments', 'BitnobCustomer')
    MobileTransaction = apps.get_model('payments', 'MobileTransaction')
    
    # First, update any existing transactions with null created_at
    now = timezone.now()
    MobileTransaction.objects.filter(created_at__isnull=True).update(created_at=now)
    
    # Group receivers by customer to create consolidated payment schedules
    customers_with_receivers = {}
    
    for receiver in MobileReceiver.objects.filter(payment_schedule__isnull=True):
        customer_id = receiver.customer_id
        if customer_id not in customers_with_receivers:
            customers_with_receivers[customer_id] = []
        customers_with_receivers[customer_id].append(receiver)
    
    # Create payment schedules for each customer
    for customer_id, receivers in customers_with_receivers.items():
        try:
            customer = BitnobCustomer.objects.get(id=customer_id)
            
            # Calculate total amount for all receivers
            total_amount = sum(
                receiver.amount_per_installment * receiver.number_of_installments 
                for receiver in receivers
            )
            
            # Create a default payment schedule
            payment_schedule = PaymentSchedule.objects.create(
                id=uuid.uuid4(),
                customer=customer,
                title=f"Legacy Payment Plan - {customer.first_name} {customer.last_name}",
                description="Migrated from existing receivers",
                status='active',
                total_amount=total_amount,
                frequency='monthly',
                start_date=now,
                created_at=now,
                updated_at=now
            )
            
            # Associate all receivers with this payment schedule
            for receiver in receivers:
                receiver.payment_schedule = payment_schedule
                receiver.save()
                
        except Exception as e:
            print(f"Error migrating receivers for customer {customer_id}: {e}")


def reverse_migration(apps, schema_editor):
    """
    Reverse the migration by removing payment_schedule references
    """
    MobileReceiver = apps.get_model('payments', 'MobileReceiver')
    PaymentSchedule = apps.get_model('payments', 'PaymentSchedule')
    
    # Remove payment schedule references from receivers
    MobileReceiver.objects.all().update(payment_schedule=None)
    
    # Delete payment schedules created during migration
    PaymentSchedule.objects.filter(
        title__startswith="Legacy Payment Plan"
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("payments", "0003_alter_mobiletransaction_options_and_more"),
    ]

    operations = [
        migrations.RunPython(
            create_default_payment_schedules,
            reverse_migration
        ),
    ]
