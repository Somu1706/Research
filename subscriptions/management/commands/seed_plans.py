"""
python manage.py seed_plans

Creates / updates the three subscription tiers.
"""
from django.core.management.base import BaseCommand
from subscriptions.models import SubscriptionPlan

PLANS = [
    {
        "tier": "basic",
        "name": "Basic",
        "price_monthly": 100,
        "reach_limit": 1000,
        "whatsapp_enabled": False,
        "facebook_enabled": False,
        "description": (
            "Get your business listed on LocalPro and found by customers "
            "in your city."
        ),
    },
    {
        "tier": "pro",
        "name": "Pro",
        "price_monthly": 500,
        "reach_limit": 5000,
        "whatsapp_enabled": True,
        "facebook_enabled": False,
        "description": (
            "We reach up to 5,000 customers in your city "
            "through WhatsApp."
        ),
    },
    {
        "tier": "max",
        "name": "Max",
        "price_monthly": 1500,
        "reach_limit": 10000,
        "whatsapp_enabled": True,
        "facebook_enabled": True,
        "description": (
            "We reach up to 10,000 customers in your city "
            "through WhatsApp and Facebook."
        ),
    },
]


class Command(BaseCommand):
    help = "Seed Basic / Pro / Max subscription plans"

    def handle(self, *args, **options):
        for data in PLANS:
            plan, created = SubscriptionPlan.objects.update_or_create(
                tier=data["tier"], defaults=data
            )
            verb = "Created" if created else "Updated"
            self.stdout.write(self.style.SUCCESS(f"{verb}: {plan}"))
