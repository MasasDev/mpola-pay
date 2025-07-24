# management/commands/run_scheduled_payments.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from mpola.tasks import process_scheduled_payments

class Command(BaseCommand):
    help = 'Manually trigger scheduled payments processing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--schedule-id',
            type=str,
            help='Process specific schedule by ID',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be processed without executing',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS(f'Starting scheduled payments at {timezone.now()}')
        )

        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No payments will be executed')
            )
            # TODO: Implement dry run logic
            return

        if options['schedule_id']:
            from mpola.tasks import process_schedule_payments
            result = process_schedule_payments.delay(options['schedule_id'])
            self.stdout.write(
                self.style.SUCCESS(f'Queued specific schedule: {options["schedule_id"]}')
            )
        else:
            result = process_scheduled_payments.delay()
            self.stdout.write(
                self.style.SUCCESS('Queued all scheduled payments for processing')
            )

        self.stdout.write(
            self.style.SUCCESS('Scheduled payments command completed')
        )
