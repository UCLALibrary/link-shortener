from django.urls import path, re_path
from . import views

urlpatterns = [
    path("", views.add_link, name="add_link"),
    path("add_link/", views.add_link, name="add_link"),
    path("my_links/", views.my_links, name="my_links"),
    path("all_links/", views.all_links, name="all_links"),
    path("delete_link/<int:link_id>", views.delete_link, name="delete_link"),
    path("show_usage/<int:link_id>", views.show_usage, name="show_usage"),
    path("logs/", views.show_log, name="show_log"),
    path("logs/<int:line_count>", views.show_log, name="show_log"),
    path("release_notes/", views.release_notes, name="release_notes"),
    # Everything else is treated as a short link for (possible) redirection.
    # Match full path, which must consist of at least one non-whitespace character.
    re_path(r"^\S+$", views.redirect_link, name="redirect_link"),
]
