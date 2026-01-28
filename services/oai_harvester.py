import os
import requests
import logging
import sys
from datetime import datetime
from sickle import Sickle

# --- Django Setup for Standalone Execution ---
if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "daystar_sdg.settings")
    import django
    django.setup()

from django.conf import settings
from django.db import transaction
from impact_tracker.models import Activity, User

logger = logging.getLogger(__name__)

class DaystarOAIHarvester:
    """
    Harvester for Daystar University Research Repository using OAI-PMH.
    """
    BASE_URL = "https://repository.daystar.ac.ke/server/oai/request"
    METADATA_PREFIX = "oai_dc"

    def __init__(self):
        self.harvester = Sickle(self.BASE_URL)
        
        try:
            username = os.getenv("DEFAULT_SCRAPER_USERNAME", "admin")
            self.default_lead_author = User.objects.filter(username=username).first()
            if not self.default_lead_author:
                logger.warning(f"Default scraper user '{username}' not found. Lead author will be None.")
        except Exception as e:
            logger.error(f"Error getting default scraper user: {e}")
            self.default_lead_author = None

    def _extract_field(self, record, key, default=None):
        """Helper to extract a field from Sickle record metadata."""
        values = record.metadata.get(key, [])
        if values:
            if isinstance(values, list):
                # Filter out None values before processing
                clean_values = [v for v in values if v is not None]
                if not clean_values:
                    return default
                return clean_values[0] if len(clean_values) == 1 else "; ".join(clean_values)
            return values
        return default

    def _parse_record_to_activity_data(self, record) -> dict:
        """Parses an OAI record into an Activity dictionary."""
        data = {}
        
        # 1. Title
        data['title'] = self._extract_field(record, "title", "No Title Provided")

        # 2. Description
        data['description'] = self._extract_field(record, "description", "No Description Provided")

        # 3. Authors
        data['authors'] = self._extract_field(record, "creator", "Anonymous")

        # 4. Date
        date_str = self._extract_field(record, "date")
        data['original_publication_date'] = None
        
        if date_str:
            try:
                clean_date = date_str.split('T')[0]
                if len(clean_date) == 4:
                    data['original_publication_date'] = datetime.strptime(clean_date, "%Y").date()
                else:
                    data['original_publication_date'] = datetime.strptime(clean_date, "%Y-%m-%d").date()
            except ValueError:
                # Use header identifier for error logging safely
                logger.warning(f"Could not parse date '{date_str}' for record {record.header.identifier}")

        # 5. External URL
        identifiers = record.metadata.get("identifier", [])
        found_url = None
        
        for ident in identifiers:
            if ident.startswith("http"):
                found_url = ident
                break
        
        # Fallback to the OAI ID (accessed via header) if no HTTP link is found
        data['external_url'] = found_url if found_url else record.header.identifier

        # 6. Activity Type
        types = record.metadata.get("type", [])
        type_str = ""
        if types and types[0] is not None:
            type_str = types[0].lower()

        if any(x in type_str for x in ["thesis", "dissertation"]):
            data['activity_type'] = 'Research'
        elif any(x in type_str for x in ["article", "journal", "publication"]):
            data['activity_type'] = 'Publication'
        elif "report" in type_str:
            data['activity_type'] = 'Publication'
        else:
            data['activity_type'] = 'Publication'

        # 7. System Defaults
        data['is_scraped'] = True
        data['lead_author'] = self.default_lead_author
        data['ai_classified'] = False

        return data

    def harvest_records(self, start_date=None, end_date=None, limit=None):
        """
        Harvests records and saves them to the DB.
        """
        print(f"Starting harvest from {self.BASE_URL}...")
        
        kwargs = {
            'metadataPrefix': self.METADATA_PREFIX, 
            'ignore_deleted': True
        }
        
        if start_date:
            kwargs['from'] = start_date.strftime('%Y-%m-%d')
        if end_date:
            kwargs['until'] = end_date.strftime('%Y-%m-%d')

        try:
            records = self.harvester.ListRecords(**kwargs)
            
            count = 0
            new_count = 0
            updated_count = 0

            for record in records:
                if limit and count >= limit:
                    break
                
                try:
                    activity_data = self._parse_record_to_activity_data(record)
                    
                    obj, created = Activity.objects.update_or_create(
                        external_url=activity_data['external_url'],
                        defaults=activity_data
                    )
                    
                    if created:
                        new_count += 1
                        # Optional: Print less frequently to speed up large harvests
                        if new_count % 50 == 0: 
                            print(f"[NEW] {activity_data['title'][:60]}...")
                    else:
                        updated_count += 1
                        
                    count += 1
                    
                except Exception as e:
                    rec_id = getattr(record.header, 'identifier', 'Unknown ID')
                    print(f"Error processing record {rec_id}: {e}")

            print(f"\nHarvest Complete. Total Processed: {count}, New: {new_count}, Updated: {updated_count}")
            
            # --- FIX IS HERE: Return a dictionary, not a string ---
            return {
                "total_processed": count,
                "new_activities": new_count,
                "updated_activities": updated_count
            }

        except Exception as e:
            print(f"Critical Harvest Error: {e}")
            raise e

if __name__ == "__main__":
    harvester = DaystarOAIHarvester()
    harvester.harvest_records(limit=5)