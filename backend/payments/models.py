# models.py
from django.db import models
from django.utils import timezone
from datetime import timedelta
import uuid

class BitnobCustomer(models.Model):
    email = models.EmailField()
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    country_code = models.CharField(max_length=5)
    bitnob_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.email}"

class PaymentSchedule(models.Model):
    """
    Represents a payment plan created by a customer with multiple receivers
    and installment details. Groups related receivers and transactions.
    """
    SCHEDULE_STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('paused', 'Paused'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(BitnobCustomer, on_delete=models.CASCADE, related_name="payment_schedules")
    title = models.CharField(max_length=200, help_text="Descriptive name for this payment schedule")
    description = models.TextField(blank=True, help_text="Optional description of the payment plan")
    status = models.CharField(max_length=20, choices=SCHEDULE_STATUS_CHOICES, default='active')
    subtotal_amount = models.DecimalField(max_digits=15, decimal_places=2, help_text="Subtotal amount across all receivers and installments (before processing fee)")
    processing_fee = models.DecimalField(max_digits=15, decimal_places=2, default=0, help_text="Processing fee (1.5% of subtotal)")
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, help_text="Total amount including processing fee")
    frequency = models.CharField(max_length=20, default='monthly', help_text="Payment frequency (e.g., test_2min, weekly, monthly)")
    next_payment_date = models.DateTimeField(null=True, blank=True, help_text="When the next payment should be processed")
    last_payment_date = models.DateTimeField(null=True, blank=True, help_text="When the last payment was processed")
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True, help_text="Expected completion date")
    is_funded = models.BooleanField(default=False, help_text="Whether this schedule has been adequately funded")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.customer.email}"

    @property
    def total_receivers(self):
        return self.receivers.count()

    @property
    def processing_fee_percentage(self):
        """Return the processing fee as a percentage of subtotal"""
        if self.subtotal_amount > 0:
            return round((self.processing_fee / self.subtotal_amount) * 100, 2)
        return 0

    @property
    def total_transactions(self):
        return MobileTransaction.objects.filter(receiver__payment_schedule=self).count()

    @property
    def completed_transactions(self):
        return MobileTransaction.objects.filter(receiver__payment_schedule=self, status='success').count()

    @property
    def progress_percentage(self):
        total = self.total_transactions
        if total == 0:
            return 0
        return round((self.completed_transactions / total) * 100, 2)

    @property
    def is_completed(self):
        """Check if all transactions in this schedule are completed"""
        return self.total_transactions > 0 and self.completed_transactions == self.total_transactions

    @property
    def total_funded_amount(self):
        """Calculate total amount funded for this schedule"""
        from django.db.models import Sum
        return self.fund_transactions.filter(status="paid").aggregate(
            total=Sum('amount')
        )['total'] or 0

    @property
    def total_payments_made(self):
        """Calculate total amount of successful payments made from this schedule"""
        from django.db.models import Sum
        return MobileTransaction.objects.filter(
            receiver__payment_schedule=self,
            status='success'
        ).aggregate(total=Sum('amount'))['total'] or 0

    @property
    def available_balance(self):
        """Calculate available balance (funded amount minus successful payments)"""
        return self.total_funded_amount - self.total_payments_made

    @property 
    def funding_shortfall(self):
        """Calculate how much more funding is needed"""
        funded = self.total_funded_amount
        required = self.total_amount
        return max(0, required - funded)

    @property
    def is_adequately_funded(self):
        """Check if schedule has enough funds to proceed"""
        return self.total_funded_amount >= self.total_amount

    def has_sufficient_funds_for_amount(self, amount):
        """Check if there's enough available balance for a specific amount (e.g., one installment)"""
        return self.available_balance >= amount

    def update_funding_status(self):
        """Update the is_funded flag based on actual funding"""
        self.is_funded = self.is_adequately_funded
        self.save()
        return self.is_funded

    def get_frequency_timedelta(self):
        """Convert frequency to timedelta for calculating next payment dates"""
        frequency_map = {
            'test_30sec': timedelta(seconds=30),
            'test_2min': timedelta(minutes=2),
            'test_5min': timedelta(minutes=5),
            'hourly': timedelta(hours=1),
            'daily': timedelta(days=1),
            'weekly': timedelta(days=7),
            'biweekly': timedelta(days=14),
            'monthly': timedelta(days=30),
            'quarterly': timedelta(days=90),
            'annually': timedelta(days=365)
        }
        return frequency_map.get(self.frequency, timedelta(days=30))
    
    def calculate_next_payment_date(self, from_date=None):
        """Calculate when the next payment should occur"""
        if from_date is None:
            from_date = self.last_payment_date or self.start_date or timezone.now()
        
        return from_date + self.get_frequency_timedelta()
    
    def is_payment_due(self):
        """Check if a payment is due based on the schedule"""
        if not self.next_payment_date:
            # If no next payment date is set, calculate it
            self.next_payment_date = self.calculate_next_payment_date()
            self.save()
        
        return timezone.now() >= self.next_payment_date
    
    def update_payment_dates(self):
        """Update payment dates after a successful payment"""
        self.last_payment_date = timezone.now()
        self.next_payment_date = self.calculate_next_payment_date(self.last_payment_date)
        self.save()

    def save(self, *args, **kwargs):
        # Set initial next_payment_date if not set
        if not self.next_payment_date and self.start_date:
            self.next_payment_date = self.calculate_next_payment_date(self.start_date)
        super().save(*args, **kwargs)

class MobileReceiver(models.Model):
    payment_schedule = models.ForeignKey(PaymentSchedule, on_delete=models.CASCADE, related_name="receivers", null=True, blank=True)
    customer = models.ForeignKey(BitnobCustomer, on_delete=models.CASCADE, related_name="receivers")
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    country_code = models.CharField(max_length=5)
    amount_per_installment = models.DecimalField(max_digits=12, decimal_places=2)
    number_of_installments = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Ensure phone numbers are unique within a payment schedule
        unique_together = [('payment_schedule', 'phone')]

    def __str__(self):
        return f"{self.name} - {self.phone}"

    @property
    def total_amount(self):
        return self.amount_per_installment * self.number_of_installments

    def next_installment(self):
        """Get the next installment number for this receiver"""
        last_transaction = self.transactions.order_by('-installment_number').first()
        if last_transaction:
            return last_transaction.installment_number + 1
        return 1

    def can_receive_next_installment(self):
        """Check if this receiver can receive the next installment based on schedule timing and funding"""
        # Check if all installments are completed
        if self.completed_installments >= self.number_of_installments:
            return False, "All installments completed"
        
        # Check if there's enough funding for this specific installment
        schedule = self.payment_schedule
        if not schedule.has_sufficient_funds_for_amount(self.amount_per_installment):
            return False, f"Insufficient available balance for this installment. Need {self.amount_per_installment}, have {schedule.available_balance} available"
        
        # Check if the schedule allows payments right now
        if not schedule.is_payment_due():
            time_remaining = schedule.next_payment_date - timezone.now()
            return False, f"Next payment not due yet. Wait {time_remaining.total_seconds():.0f} seconds"
        
        # Check if there's already a pending transaction for the next installment
        next_installment_num = self.next_installment()
        existing_txn = self.transactions.filter(
            installment_number=next_installment_num,
            status__in=['pending', 'processing']
        ).first()
        
        if existing_txn:
            return False, f"Installment {next_installment_num} already in progress"
        
        return True, "Ready for next installment"

    def get_next_payment_info(self):
        """Get information about the next payment for this receiver"""
        can_pay, message = self.can_receive_next_installment()
        schedule = self.payment_schedule
        
        return {
            "can_pay_now": can_pay,
            "message": message,
            "next_installment_number": self.next_installment(),
            "next_payment_date": schedule.next_payment_date,
            "current_time": timezone.now(),
            "schedule_frequency": schedule.frequency,
            "time_until_next_payment": (schedule.next_payment_date - timezone.now()).total_seconds() if schedule.next_payment_date else 0
        }

    @property
    def completed_installments(self):
        return self.transactions.filter(status='success').count()

    @property
    def progress_percentage(self):
        if self.number_of_installments == 0:
            return 0
        return round((self.completed_installments / self.number_of_installments) * 100, 2)

    @property
    def schedule(self):
        """Alias for payment_schedule for backward compatibility"""
        return self.payment_schedule

class MobileTransaction(models.Model):
    TRANSACTION_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    receiver = models.ForeignKey(MobileReceiver, on_delete=models.CASCADE, related_name="transactions")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    installment_number = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUS_CHOICES, default="pending")
    reference = models.CharField(max_length=100, unique=True, null=True, blank=True, help_text="Bitnob transaction reference")
    sent_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    failure_reason = models.TextField(blank=True, help_text="Reason for failure if transaction failed")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        unique_together = ['receiver', 'installment_number']  # Prevent duplicate installments
        ordering = ['receiver', 'installment_number']

    def __str__(self):
        return f"{self.receiver.name} - Installment {self.installment_number} - {self.status}"

    def save(self, *args, **kwargs):
        # Auto-set completed_at when status changes to success
        if self.status == 'success' and not self.completed_at:
            self.completed_at = timezone.now()
        # Set created_at if not set (for existing records)
        if not self.created_at:
            self.created_at = timezone.now()
        super().save(*args, **kwargs)
# models.py

from django.db import models
import uuid

class FundTransaction(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("expired", "Expired"),
        ("failed", "Failed"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    schedule = models.ForeignKey("PaymentSchedule", on_delete=models.CASCADE, related_name="fund_transactions")
    reference = models.CharField(max_length=100, unique=True)
    
    amount = models.DecimalField(max_digits=20, decimal_places=2)  # UGX
    currency = models.CharField(max_length=10, default="UGX")

    stablecoin_address = models.CharField(max_length=200, blank=True, null=True)
    stablecoin_network = models.CharField(max_length=20, blank=True, null=True)
    usdt_required = models.DecimalField(max_digits=20, decimal_places=6, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
