from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from shortlinks.views_utils import format_short_path, get_links


class LinkTest(TestCase):
    fixtures = ["sample_data.json"]

    def test_get_links_all(self):
        # Confirm count of all links (no owner specified).
        links = get_links()
        self.assertEqual(len(links), 3)

    def test_get_links_by_owner(self):
        # Confirm count of links owner by user #2, a subset of all links.
        user = User.objects.get(pk=2)
        links = get_links(owner=user)
        self.assertEqual(len(links), 2)

    def test_short_path_is_formatted(self):
        # Confirm short paths are correctly formatted.
        short_path = format_short_path("abc")
        self.assertEqual(short_path, "/abc")
        short_path = format_short_path("/def")
        self.assertEqual(short_path, "/def")
        short_path = format_short_path("/ghi/")
        self.assertEqual(short_path, "/ghi")

    def test_short_link_is_correctly_built(self):
        # Confirm Django ORM/DB built short_link correctly.
        # This is done via get_links().

        # Grab first link only.
        link = get_links()[0]
        expected_short_link = settings.LINK_PREFIX + link.short_path
        self.assertEqual(expected_short_link, link.short_link)
