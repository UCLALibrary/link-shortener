from django.urls import path, re_path
from . import views

urlpatterns = [
    path("add_link/", views.add_link, name="add_link"),
    path("show_links/", views.show_links, name="show_links"),
    path("logs/", views.show_log, name="show_log"),
    path("logs/<int:line_count>", views.show_log, name="show_log"),
    path("release_notes/", views.release_notes, name="release_notes"),
    # Everything else is treated as a short link for (possible) redirection.
    # Match full path, which must consist of at least one non-whitespace character.
    re_path(r"^\S+$", views.redirect_link, name="redirect_link"),
]
