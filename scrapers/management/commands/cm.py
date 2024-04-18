from django.core.management import BaseCommand

from scrapers.defs_farsnews import farsnews_scrap


class Command(BaseCommand):
    def handle(self, *args, **options):
        farsnews_scrap()
