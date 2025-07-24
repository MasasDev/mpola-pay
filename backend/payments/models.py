# models.py
from django.db import models
from django.utils import timezone
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
    frequency = models.CharField(max_length=20, default='monthly', help_text="Payment frequency (e.g., weekly, monthly)")
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True, help_text="Expected completion date")
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

    @property
    def completed_installments(self):
        return self.transactions.filter(status='success').count()

    @property
    def progress_percentage(self):
        if self.number_of_installments == 0:
            return 0
        return round((self.completed_installments / self.number_of_installments) * 100, 2)

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
