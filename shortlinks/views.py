import logging
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import QuerySet  # for type hints
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from shortlinks.forms import LinkForm
from shortlinks.models import Link
from shortlinks.views_utils import format_short_path, get_links

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


def redirect_link(request: HttpRequest) -> HttpResponse:
    """Get target URL matching short link (if any).
    # Raise HTTP 404 if not found.
    """
    short_path = format_short_path(request.path)

    # TODO: Friendly 404 page here, or just let target site handle 404s?
    link = get_object_or_404(Link, short_path=short_path)
    # If we get here, the link was found.
    return redirect(link.target_url)


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
