import unittest
from django.contrib.auth.models import User
from vz_wiki.models import Page, Revision
from vz_wiki.exceptions import *

class WikiTestCase(unittest.TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username='wiki_admin',
            email='wiki_admin@localhost',
        )
        self.user2 = User.objects.create(
            username='wiki_user',
            email='wiki_user@localhost',
        )
        self.page = Page.objects.create(
            title='unit test page',
            slug='unit-test-page',
            tags='unit-test',
            creator=self.user,
        )

    def testWiki(self):
        latest = self.page.latest_revision()
        unpublished = self.page.unpublished_revision()
        self.assertEquals(latest.number, 1)
        self.assertEquals(latest.is_published, True)
        self.assertEquals(unpublished, None)
        self.assertEquals(self.page.history().count(), 1)
        
        self.page.check_out(user=self.user)
        latest = self.page.latest_revision()
        unpublished = self.page.unpublished_revision()
        self.assertEquals(latest.number, 1)
        self.assertEquals(latest.is_published, True)
        self.assertEquals(self.page.who_checked_out(), self.user)
        self.assertNotEquals(unpublished, None)
        self.assertEquals(self.page.is_checked_out, True)
        self.assertRaises(PageAlreadyCheckedOut, self.page.check_out, self.user2)
        self.assertEquals(self.page.count_revisions(), 1)        
        self.assertRaises(UnpublishedRevisionExists, self.page.check_in)
        unpublished.publish()
        self.assertEquals(self.page.is_checked_out, False)
        self.assertEquals(self.page.history().count(), 2)
        
        self.assertEquals(self.page.count_revisions(), 2)
        self.assertEquals(self.page.unpublished_revision(), None)
