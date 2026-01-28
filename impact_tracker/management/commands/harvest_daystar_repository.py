import logging
from django.core.management.base import BaseCommand, CommandError
from datetime import datetime, date
from services.oai_harvester import DaystarOAIHarvester

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Harvests records from the Daystar University Research Repository via OAI-PMH.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--from',
            type=str,
            help='Start date for harvesting (YYYY-MM-DD). Harvests records from this date (inclusive).',
            dest='from_date' # Use a different name because 'from' is a Python keyword
        )
        parser.add_argument(
            '--until',
            type=str,
            help='End date for harvesting (YYYY-MM-DD). Harvests records up to this date (inclusive).',
            dest='until_date'
        )

    def handle(self, *args, **options):
        harvester = DaystarOAIHarvester()
        from_date_str = options['from_date']
        until_date_str = options['until_date']

        from_date = None
        until_date = None

        if from_date_str:
            try:
                from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
            except ValueError:
                raise CommandError('Invalid --from date format. Use YYYY-MM-DD.')

        if until_date_str:
            try:
                until_date = datetime.strptime(until_date_str, '%Y-%m-%d').date()
            except ValueError:
                raise CommandError('Invalid --until date format. Use YYYY-MM-DD.')

        if from_date and until_date and from_date > until_date:
            raise CommandError('--from date cannot be after --until date.')
        
        # Convert date objects to datetime objects for the harvester
        from_datetime = datetime.combine(from_date, datetime.min.time()) if from_date else None
        until_datetime = datetime.combine(until_date, datetime.max.time()) if until_date else None

        self.stdout.write(self.style.SUCCESS(f"Initiating OAI-PMH harvest for Daystar Repository..."))
        try:
            results = harvester.harvest_records(start_date=from_datetime, end_date=until_datetime)
            self.stdout.write(self.style.SUCCESS(
                f"Harvest completed: Processed {results['total_processed']} records. "
                f"New activities: {results['new_activities']}, Updated activities: {results['updated_activities']}."
            ))
        except Exception as e:
            raise CommandError(f'OAI Harvest failed: {e}')