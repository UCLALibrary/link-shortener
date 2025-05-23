import logging
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import QuerySet  # for type hints
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from shortlinks.forms import LinkForm
from shortlinks.models import Link, UsageStat
from shortlinks.views_utils import (
    capture_usage_stats,
    format_short_path,
    get_links,
    get_short_link,
)

logger = logging.getLogger(__name__)


@login_required
def add_link(request: HttpRequest) -> HttpResponse:
    """Add a user-entered Link record to the database."""
    if request.method == "POST":
        form = LinkForm(request.POST)
        if form.is_valid():
            # User must be logged in, so is present in request.
            user = request.user
            target_url = form.cleaned_data["target_url"]
            short_path = format_short_path(form.cleaned_data["short_path"])

            # Check to see if link already exists and notify user if so.
            if Link.objects.filter(short_path=short_path).exists():
                messages.error(request, f"Short path {short_path} already exists!")
            else:
                # Create new link.
                new_link = Link(
                    short_path=short_path,
                    target_url=target_url,
                    created_by=user,
                )
                new_link.save()
                messages.success(request, "Your link was saved.")
    else:
        form = LinkForm()
    return render(request, "shortlinks/add_link.html", {"form": form})


@login_required
def display_links(request: HttpRequest, links: QuerySet) -> HttpResponse:
    """Display a list of links, provided by calling view."""
    return render(request, "shortlinks/show_links.html", {"links": links})


@login_required
def all_links(request: HttpRequest) -> HttpResponse:
    """Display a list of all Links."""
    links = get_links()
    return display_links(request, links)


@login_required
def my_links(request: HttpRequest) -> HttpResponse:
    """Display a list of just the current user's Links."""
    # User must be logged in, so is present in request.
    user = request.user
    links = get_links(owner=user)
    return display_links(request, links)


@login_required
def delete_link(request: HttpRequest, link_id: int) -> HttpResponse:
    """Delete the link with the given link_id."""
    link = get_object_or_404(Link, pk=link_id)
    link.delete()
    # Go back to the calling page
    return HttpResponseRedirect(request.headers.get("referer"))


@login_required
def show_usage(request: HttpRequest, link_id: int) -> HttpResponse:
    """Show usage info for the given link_id."""
    usage_stats = UsageStat.objects.filter(link_id=link_id).order_by("-usage_date")
    link = get_object_or_404(Link, pk=link_id)
    short_link = get_short_link(link.short_path)
    return render(
        request,
        "shortlinks/show_usage.html",
        {"usage_stats": usage_stats, "short_link": short_link},
    )


@login_required
def show_log(request, line_count: int = 200) -> HttpResponse:
    """Display log."""
    log_file = "logs/application.log"
    try:
        with open(log_file, "r") as f:
            # Get just the last line_count lines in the log.
            lines = f.readlines()[-line_count:]
            # Template prints these as a single block, so join lines into one chunk.
            log_data = "".join(lines)
    except FileNotFoundError:
        log_data = f"Log file {log_file} not found"

    return render(request, "shortlinks/log.html", {"log_data": log_data})


@login_required
def release_notes(request: HttpRequest) -> HttpResponse:
    """Display release notes."""
    return render(request, "shortlinks/release_notes.html")


# This view does not require login, as it handles anonymous redirects.
def redirect_link(request: HttpRequest) -> HttpResponse:
    """Get target URL matching short link (if any).
    # Raise HTTP 404 if not found.
    """
    requested_path = request.META.get("PATH_INFO", "")
    query_string = request.META.get("QUERY_STRING", "")
    if query_string != "":
        requested_path = f"{requested_path}?{query_string}"
    short_path = format_short_path(requested_path)

    # Let target site handle 404s, since web editors manage these links.
    link = get_object_or_404(Link, short_path=short_path)

    # If we get here, the link was found.
    response = HttpResponseRedirect(link.target_url)

    # Capture usage statistics
    capture_usage_stats(link, request)

    # Add a referer (sic) HTTP header with the full URL of the short link.
    requested_short_url = get_short_link(short_path)
    response.headers["Referer"] = requested_short_url
    return response
