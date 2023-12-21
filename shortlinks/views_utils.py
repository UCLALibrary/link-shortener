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

    # Add a "short_link" field: link_prefix+short_path
    # so the template doesn't have to assemble this.
    links = links.annotate(
        short_link=Concat(Value(link_prefix), "short_path", output_field=CharField())
    ).order_by("-create_date")
    return links


def get_short_link(short_path: str) -> str:
    """Return a short_link: an absolute URL using the short_path.
    This duplicates the simple concatenation logic in get_links(),
    but uses different access logic and does not hit the database.
    """
    return settings.LINK_PREFIX + short_path
