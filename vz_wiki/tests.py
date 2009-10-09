import unittest
import random
from django.contrib.auth.models import User
from vz_wiki.models import Page, Revision
from vz_wiki.exceptions import *

TEST_SIZE = 50
random.seed()


class WikiTestCase(unittest.TestCase):

    def setUp(self):
        self.user = User.objects.create(username='wiki_admin',
            email='wiki_admin@localhost')
        self.user2 = User.objects.create(username='wiki_user',
            email='wiki_user@localhost')
        self.pages = []
        for x in range(TEST_SIZE):
            self.pages.append(Page.objects.create(
                title=u'test page number %s'%x,
                slug=u'test-page-number-%s'%x, tags='test', creator=self.user))

    def testWiki(self):
        for y in range(TEST_SIZE/2):
            page1 = random.choice(self.pages)
            #self.assertEqual(page1.count_revisions(), 1)
            if page1.is_checked_out:
                self.failUnlessRaises(UnpublishedRevisionExists,
                    page1.check_in)
                revivsion = page1.unpublished_revision()
                revivsion.publish()
                self.failUnlessRaises(AlreadyPublishedRevision,
                    revivsion.publish)
                page1.check_in()
            page1.check_out(user=self.user2)
            self.failUnlessRaises(PageAlreadyCheckedOut,
                page1.check_out, self.user)
            page2 = random.choice(self.pages)
