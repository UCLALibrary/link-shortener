from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser  # for type hints
from django.db.models import CharField, QuerySet, Value
from django.db.models.functions import Concat
from shortlinks.models import Link


def format_short_path(short_path: str) -> str:
    """Format short path for consistency."""
    # Prepend slash, if user did not supply one.
    if not short_path.startswith("/"):
        short_path = "/" + short_path
    # Remove trailing slash(es), if any.
    if short_path.endswith("/"):
        short_path = short_path.rstrip("/")
    return short_path


def get_links(owner: AbstractBaseUser = None) -> QuerySet:
    """Return a queryset of links, optionally filtered by owner."""
    link_prefix = settings.LINK_PREFIX

    if owner:
        links = Link.objects.filter(created_by=owner)
    else:
        links = Link.objects.all()

    links = links.annotate(
        short_link=Concat(Value(link_prefix), "short_path", output_field=CharField())
    ).order_by("-create_date")
    return links
