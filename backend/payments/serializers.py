# serializers.py
from rest_framework import serializers
from .models import BitnobCustomer, MobileReceiver, PaymentSchedule, MobileTransaction

class CustomerCreateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    firstName = serializers.CharField()
    lastName = serializers.CharField()
    phone = serializers.CharField()
    countryCode = serializers.CharField()

class ReceiverSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    phone = serializers.CharField(max_length=20)
    countryCode = serializers.CharField(max_length=5)
    amountPerInstallment = serializers.DecimalField(max_digits=12, decimal_places=2)
    numberOfInstallments = serializers.IntegerField(min_value=1)

class PaymentScheduleCreateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    title = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True)
    frequency = serializers.CharField(max_length=20, default='monthly')
    start_date = serializers.DateTimeField(required=False)
    receivers = serializers.ListField(
        child=ReceiverSerializer(),
        min_length=1,
        help_text="List of receivers for this payment schedule"
    )

    def validate_receivers(self, value):
        """Validate that all receivers have unique phone numbers within this schedule"""
        phones = [receiver['phone'] for receiver in value]
        if len(phones) != len(set(phones)):
            raise serializers.ValidationError("Duplicate phone numbers are not allowed in the same payment schedule.")
        return value

# Legacy serializer for backward compatibility
class ReceiverCreateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    receivers = serializers.ListField(
        child=serializers.DictField(child=serializers.CharField())
    )

class PaymentScheduleSerializer(serializers.ModelSerializer):
    """Serializer for reading PaymentSchedule objects"""
    total_receivers = serializers.ReadOnlyField()
    total_transactions = serializers.ReadOnlyField()
    completed_transactions = serializers.ReadOnlyField()
    progress_percentage = serializers.ReadOnlyField()
    processing_fee_percentage = serializers.ReadOnlyField()
    is_completed = serializers.ReadOnlyField()
    customer_name = serializers.SerializerMethodField()

    class Meta:
        model = PaymentSchedule
        fields = [
            'id', 'title', 'description', 'status', 'subtotal_amount', 
            'processing_fee', 'total_amount', 'frequency', 'start_date', 
            'end_date', 'created_at', 'updated_at', 'total_receivers', 
            'total_transactions', 'completed_transactions', 'progress_percentage', 
            'processing_fee_percentage', 'is_completed', 'customer_name'
        ]

    def get_customer_name(self, obj):
        return f"{obj.customer.first_name} {obj.customer.last_name}"

class MobileReceiverSerializer(serializers.ModelSerializer):
    """Serializer for reading MobileReceiver objects"""
    total_amount = serializers.ReadOnlyField()
    completed_installments = serializers.ReadOnlyField()
    progress_percentage = serializers.ReadOnlyField()
    payment_schedule_title = serializers.SerializerMethodField()

    class Meta:
        model = MobileReceiver
        fields = [
            'id', 'name', 'phone', 'country_code', 'amount_per_installment',
            'number_of_installments', 'created_at', 'total_amount',
            'completed_installments', 'progress_percentage', 'payment_schedule_title'
        ]

    def get_payment_schedule_title(self, obj):
        return obj.payment_schedule.title

class MobileTransactionSerializer(serializers.ModelSerializer):
    """Serializer for reading MobileTransaction objects"""
    receiver_name = serializers.SerializerMethodField()
    receiver_phone = serializers.SerializerMethodField()

    class Meta:
        model = MobileTransaction
        fields = [
            'id', 'amount', 'installment_number', 'status', 'reference',
            'sent_at', 'completed_at', 'failure_reason', 'created_at',
            'receiver_name', 'receiver_phone'
        ]

    def get_receiver_name(self, obj):
        return obj.receiver.name

    def get_receiver_phone(self, obj):
        return obj.receiver.phone
