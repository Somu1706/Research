from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from customers.models import Customer
from messaging.models import Outreach, OutreachLog
from messaging.tasks import trigger_outreach
from services.models import ServiceProvider
from subscriptions.models import Subscription, SubscriptionPlan


def make_provider(tier, whatsapp, facebook, reach=1000):
    user = get_user_model().objects.create_user(username=f"owner-{tier}", password="x-test-pass-123")
    provider = ServiceProvider.objects.create(
        user=user, business_name=f"{tier.title()} Plumbing", category="plumber", city="Ahmedabad"
    )
    plan = SubscriptionPlan.objects.create(
        tier=tier, name=tier.title(), price_monthly=100, reach_limit=reach,
        whatsapp_enabled=whatsapp, facebook_enabled=facebook,
    )
    Subscription.objects.create(provider=provider, plan=plan, is_active=True)
    return provider


class OutreachChannelTests(TestCase):
    def setUp(self):
        Customer.objects.create(name="In city", phone="+919800000001", city="Ahmedabad")
        Customer.objects.create(name="Other city", phone="+919800000002", city="Surat")
        Customer.objects.create(name="Opted out", phone="+919800000003", city="Ahmedabad", opted_in_whatsapp=False)

    @patch("messaging.integrations.send_whatsapp_text")
    def test_basic_plan_sends_nothing_and_creates_no_campaign(self, send):
        provider = make_provider("basic", whatsapp=False, facebook=False)
        trigger_outreach.run(provider.pk)
        send.assert_not_called()
        self.assertFalse(Outreach.objects.filter(provider=provider).exists())

    @patch("messaging.integrations.send_whatsapp_text", return_value={"success": True, "message_id": "wamid.1"})
    def test_pro_plan_messages_only_opted_in_customers_in_city(self, send):
        provider = make_provider("pro", whatsapp=True, facebook=False)
        trigger_outreach.run(provider.pk)
        self.assertEqual(send.call_count, 1)
        outreach = Outreach.objects.get(provider=provider)
        self.assertEqual(outreach.channel, Outreach.CHANNEL_WHATSAPP)
        self.assertEqual(OutreachLog.objects.filter(outreach=outreach, status=OutreachLog.STATUS_SENT).count(), 1)

    @patch("messaging.integrations.send_whatsapp_text", return_value={"success": False, "error": "timeout"})
    def test_failed_send_is_logged_not_raised(self, send):
        provider = make_provider("pro", whatsapp=True, facebook=False)
        trigger_outreach.run(provider.pk)
        log = OutreachLog.objects.get(outreach__provider=provider)
        self.assertEqual(log.status, OutreachLog.STATUS_FAILED)
        self.assertEqual(log.error_message, "timeout")


class ReachEstimateTests(TestCase):
    def test_counts_active_opted_in_customers_in_city(self):
        Customer.objects.create(name="A", phone="+919800000011", city="Ahmedabad")
        Customer.objects.create(name="B", phone="+919800000012", city="ahmedabad")
        Customer.objects.create(name="C", phone="+919800000013", city="Ahmedabad", is_active=False)
        Customer.objects.create(name="D", phone="+919800000014", city="Surat")
        res = self.client.get(reverse("services:reach_estimate"), {"city": "Ahmedabad"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["matched"], 2)

    def test_requires_city(self):
        res = self.client.get(reverse("services:reach_estimate"))
        self.assertEqual(res.status_code, 400)
