from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from decimal import Decimal
import json
from payments.models import BitnobCustomer, PaymentSchedule, MobileReceiver

class Command(BaseCommand):
    help = 'Test payment plan creation with sample data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            default='test@example.com',
            help='Customer email to use for testing'
        )
        parser.add_argument(
            '--create-customer',
            action='store_true',
            help='Create test customer if it doesn\'t exist'
        )
        parser.add_argument(
            '--cleanup',
            action='store_true',
            help='Clean up test data after creation'
        )

    def handle(self, *args, **options):
        email = options['email']
        
        self.stdout.write(
            self.style.SUCCESS(f'Testing payment plan creation for: {email}')
        )
        
        # Check if customer exists
        try:
            customer = BitnobCustomer.objects.get(email=email)
            self.stdout.write(
                self.style.SUCCESS(f'Found existing customer: {customer}')
            )
        except BitnobCustomer.DoesNotExist:
            if options['create_customer']:
                self.stdout.write('Creating test customer...')
                customer = BitnobCustomer.objects.create(
                    email=email,
                    first_name='Test',
                    last_name='Customer',
                    phone='1234567890',
                    country_code='+1',
                    bitnob_id=f'test_{email.replace("@", "_").replace(".", "_")}'
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Created customer: {customer}')
                )
            else:
                raise CommandError(
                    f'Customer with email {email} does not exist. '
                    'Use --create-customer to create one.'
                )
        
        # Test data - your original payload
        test_data = {
            "title": "Monthly Family Support",
            "description": "Monthly payments to family members",
            "frequency": "monthly",
            "receivers": [
                {
                    "name": "Jane Doe",
                    "phone": "778520941",
                    "countryCode": "+256",
                    "amountPerInstallment": Decimal('5000'),
                    "numberOfInstallments": 2
                },
                {
                    "name": "Mike Smith",
                    "phone": "705902042",
                    "countryCode": "+256",
                    "amountPerInstallment": Decimal('3000'),
                    "numberOfInstallments": 2
                }
            ]
        }
        
        self.stdout.write('Creating payment schedule...')
        
        try:
            # Calculate total amount
            subtotal_amount = Decimal('0')
            for receiver_data in test_data["receivers"]:
                subtotal_amount += (
                    receiver_data["amountPerInstallment"] * 
                    receiver_data["numberOfInstallments"]
                )
            
            # Add 1.5% processing fee
            processing_fee = subtotal_amount * Decimal('0.015')
            total_amount = subtotal_amount + processing_fee
            
            # Create payment schedule
            payment_schedule = PaymentSchedule.objects.create(
                customer=customer,
                title=test_data["title"],
                description=test_data["description"],
                frequency=test_data["frequency"],
                subtotal_amount=subtotal_amount,
                processing_fee=processing_fee,
                total_amount=total_amount,
                start_date=timezone.now()
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Created payment schedule: {payment_schedule.id}'
                )
            )
            
            # Create receivers
            created_receivers = []
            for receiver_data in test_data["receivers"]:
                receiver = MobileReceiver.objects.create(
                    payment_schedule=payment_schedule,
                    customer=customer,
                    name=receiver_data["name"],
                    phone=receiver_data["phone"],
                    country_code=receiver_data["countryCode"],
                    amount_per_installment=receiver_data["amountPerInstallment"],
                    number_of_installments=receiver_data["numberOfInstallments"]
                )
                created_receivers.append(receiver)
                
                self.stdout.write(
                    f'  ✓ Created receiver: {receiver.name} ({receiver.phone})'
                )
            
            # Display results
            self.stdout.write(
                self.style.SUCCESS('\n📊 Payment Schedule Created Successfully!')
            )
            self.stdout.write(f'ID: {payment_schedule.id}')
            self.stdout.write(f'Title: {payment_schedule.title}')
            self.stdout.write(f'Subtotal Amount: ${subtotal_amount}')
            self.stdout.write(f'Processing Fee (1.5%): ${processing_fee:.2f}')
            self.stdout.write(f'Total Amount: ${payment_schedule.total_amount}')
            self.stdout.write(f'Total Receivers: {len(created_receivers)}')
            self.stdout.write(f'Customer: {customer.email}')
            
            self.stdout.write('\n📋 Receivers:')
            for receiver in created_receivers:
                self.stdout.write(
                    f'  • {receiver.name} ({receiver.phone}): '
                    f'${receiver.amount_per_installment} × {receiver.number_of_installments} = '
                    f'${receiver.total_amount}'
                )
            
            # Test model properties
            self.stdout.write('\n🔍 Testing model properties:')
            self.stdout.write(f'Schedule progress: {payment_schedule.progress_percentage}%')
            self.stdout.write(f'Total transactions: {payment_schedule.total_transactions}')
            self.stdout.write(f'Completed transactions: {payment_schedule.completed_transactions}')
            self.stdout.write(f'Is completed: {payment_schedule.is_completed}')
            
            for receiver in created_receivers:
                self.stdout.write(
                    f'Receiver {receiver.name} - Next installment: {receiver.next_installment()}'
                )
            
            # Cleanup if requested
            if options['cleanup']:
                self.stdout.write('\n🧹 Cleaning up test data...')
                payment_schedule.delete()  # Will cascade delete receivers
                if options['create_customer']:
                    customer.delete()
                self.stdout.write(
                    self.style.SUCCESS('Test data cleaned up successfully!')
                )
            else:
                self.stdout.write(
                    f'\n💡 To clean up test data, run:'
                    f'\n  python manage.py test_payment_plan --email {email} --cleanup'
                )
                
        except Exception as e:
            raise CommandError(f'Failed to create payment plan: {str(e)}')
            
        self.stdout.write(
            self.style.SUCCESS('\n✅ Test completed successfully!')
        )
