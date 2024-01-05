from django.db import models
from django.conf import settings
from django.utils import timezone


class Link(models.Model):
    short_path = models.CharField(blank=False, null=False)
    target_url = models.URLField(blank=False, null=False)
    create_date = models.DateTimeField(blank=False, null=False, default=timezone.now)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        blank=False,
        null=False,
        # No backwards relation to User model
        related_name="+",
    )

    class Meta:
        indexes = [
            models.Index(fields=["short_path"]),
        ]


class UsageStat(models.Model):
    link = models.ForeignKey(Link, on_delete=models.CASCADE, blank=False, null=False)
    client_ip = models.GenericIPAddressField(null=False)
    query_string = models.CharField(blank=True, null=False)
    referrer = models.CharField(blank=True, null=False)
    user_agent = models.CharField(blank=True, null=False)
    usage_date = models.DateTimeField(blank=False, null=False, default=timezone.now)
