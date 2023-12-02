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
