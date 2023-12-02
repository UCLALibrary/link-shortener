import logging
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.decorators import login_required
from shortlinks.forms import LinkForm
from shortlinks.models import Link

logger = logging.getLogger(__name__)


@login_required
def add_link(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = LinkForm(request.POST)
        if form.is_valid():
            # User must be logged in, so is present in request.
            user = request.user
            target_url = form.cleaned_data["target_url"]
            short_path = form.cleaned_data["short_path"]
            # Prepend slash, if user did not supply one.
            if not short_path.startswith("/"):
                short_path = "/" + short_path
            # Remove trailing slash(es), if any.
            if short_path.endswith("/"):
                short_path = short_path.rstrip("/")

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


def show_links(request: HttpRequest) -> HttpResponse:
    links = Link.objects.all().order_by("-create_date")
    return render(request, "shortlinks/show_links.html", {"links": links})


def redirect_link(request: HttpRequest) -> HttpResponse:
    # Get target URL matching short link (if any).
    # Raise HTTP 404 if not found.

    # Remove trailing slash(es) in requested path, if any.
    short_path = request.path.rstrip("/")
    # TODO: Friendly 404 page?
    link = get_object_or_404(Link, short_path=short_path)
    # If we get here, the link was found.
    return redirect(link.target_url)


@login_required
def show_log(request, line_count: int = 200) -> HttpResponse:
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
    return render(request, "shortlinks/release_notes.html")
