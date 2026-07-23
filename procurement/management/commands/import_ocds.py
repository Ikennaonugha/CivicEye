import ijson
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.dateparse import parse_datetime
from procurement.models import ContractingRelease

class Command(BaseCommand):
    help = 'Streams and imports massive OCDS procurement JSON files into SQLite'

    def add_arguments(self, parser):
        parser.add_argument(
            'json_file', 
            nargs='?', 
            type=str, 
            default=r'C:\Users\Admin\Desktop\ContractingRelease.json',
            help='Path to the JSON file'
        )

    def handle(self, *args, **kwargs):
        file_path = kwargs['json_file']

        self.stdout.write(f"Streaming JSON file from: {file_path}")
        
        batch_size = 1000
        objects_to_create = []
        count = 0

        try:
            with open(file_path, 'rb') as f:
                # FIXED: use_float=True converts numbers to floats so JSONField serialization won't crash
                releases = ijson.items(f, 'releases.item', use_float=True)

                for item in releases:
                    count += 1
                    buyer = item.get("buyer") or {}
                    planning = item.get("planning") or {}
                    budget = planning.get("budget") or {}
                    budget_amount_dict = budget.get("amount") or {}
                    
                    tender = item.get("tender") or {}
                    tender_value = tender.get("value") or {}

                    release_obj = ContractingRelease(
                        ocid=item.get("ocid"),
                        release_id=str(item.get("id")),
                        date=parse_datetime(item.get("date")) if item.get("date") else None,
                        initiation_type=item.get("initiationType"),
                        
                        # Buyer
                        buyer_id=buyer.get("id"),
                        buyer_name=buyer.get("name"),
                        
                        # Budget
                        budget_project=budget.get("project"),
                        budget_amount=budget_amount_dict.get("amount"),
                        budget_currency=budget_amount_dict.get("currency", "NGN"),
                        
                        # Tender
                        tender_title=tender.get("title") if tender else None,
                        tender_value_amount=tender_value.get("amount") if tender_value else None,
                        tender_status=tender.get("status") if tender else None,
                        
                        # Embedded JSON Data
                        tags=item.get("tag", []),
                        parties=item.get("parties", []),
                        planning_data=planning,
                        tender_data=tender,
                        awards_data=item.get("awards", []),
                    )

                    objects_to_create.append(release_obj)

                    # Insert in batches inside transactions
                    if len(objects_to_create) >= batch_size:
                        with transaction.atomic():
                            ContractingRelease.objects.bulk_create(
                                objects_to_create, 
                                ignore_conflicts=True
                            )
                        self.stdout.write(f"Processed {count} records...")
                        objects_to_create = []

                # Save remaining records
                if objects_to_create:
                    with transaction.atomic():
                        ContractingRelease.objects.bulk_create(
                            objects_to_create, 
                            ignore_conflicts=True
                        )

            self.stdout.write(self.style.SUCCESS(f"Successfully imported all {count} OCDS records!"))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"File not found at {file_path}"))