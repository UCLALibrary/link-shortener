from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from shortlinks.models import Link, UsageStat
from shortlinks.views_utils import format_short_path, get_links, get_short_link


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


class RedirectTest(TestCase):
    fixtures = ["sample_data.json"]

    def test_redirect_is_followed(self):
        # Confirm Django redirects to the target URL.
        link = Link.objects.get(short_path="/lib")
        short_link = get_short_link(link.short_path)
        response = self.client.get(short_link)
        self.assertRedirects(
            response, link.target_url, status_code=302, fetch_redirect_response=False
        )

    def test_referer_is_added(self):
        # Confirm our referer field is added to the response headers.
        link = Link.objects.get(short_path="/lib")
        short_link = get_short_link(link.short_path)
        response = self.client.get(short_link)
        self.assertEqual(response.headers["Referer"], short_link)


class UsageStatTest(TestCase):
    fixtures = ["sample_data.json"]

    def test_usage_is_captured(self):
        link = Link.objects.get(short_path="/use")
        short_link = get_short_link(link.short_path)
        # No need to capture client's response for this test.
        self.client.get(short_link)
        stat = UsageStat.objects.last()
        self.assertEqual(stat.link, link)

    def test_referrer_is_captured(self):
        link = Link.objects.get(short_path="/use")
        short_link = get_short_link(link.short_path)
        # No need to capture client's response for this test.
        # Add Referer (sic) header to request.
        self.client.get(short_link, headers={"Referer": short_link})
        stat = UsageStat.objects.last()
        self.assertEqual(stat.referrer, short_link)

    def test_query_string_is_captured(self):
        link = Link.objects.get(short_path="/public?campaign=linklister&tracking=evil")
        short_link = get_short_link(link.short_path)
        # No need to capture client's response for this test.
        self.client.get(short_link)
        stat = UsageStat.objects.last()
        # Query string itself does not start with "?".
        self.assertEqual(stat.query_string, "campaign=linklister&tracking=evil")
