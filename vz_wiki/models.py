from django.db import models
from django.db.models.signals import post_save, pre_save
from django.contrib.auth.models import User
from exceptions import *
import tagging
from tagging.fields import TagField

import datetime
import difflib


class Page(models.Model):
    """
    Wiki pages are unique by title and slug.

    Pages are placeholder's for Revisions.  Each page can have many revisions.
    Upon creation a default hello world page is created and published.

    A Page can only have one unpublished Reversion.  A blank unpublished
    Revision is created when a Page is checked out.

    A Page cannot be checked in while an unblished Revision for it exists.
    """
    title = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True)
    tags = TagField()
    creator = models.ForeignKey(User)
    is_editable = models.BooleanField(default=True)
    is_checked_out = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True, editable=False)

    def check_out(self, user):
        """
        Before checking a page out, check if page is already checked out.  If
        the page is already checked out, raise PageAlreadyCheckedOut exception.

        If the page isn't checked out, create a skeleton revision, check out
        page.
        """
        if self.is_checked_out:
            raise PageAlreadyCheckedOut
        revision = Revision.objects.create(page=self, author=user,
            body=self.latest_revision().body)
        self.is_checked_out = True
        self.save()
        return revision

    def check_in(self):
        """
        When model is saved a pre_save signal will throw a
        UnpublishedRevisionExists exception if the unpublished revision isn't
        published or abandoned first.
        """
        self.is_checked_out = False
        self.save()

    def latest_revision(self):
        try:
            return Revision.objects.filter(page=self, is_published=True). \
            latest('published_on')
        except Revision.DoesNotExist:
            return None

    def history(self):
        return Revision.objects.filter(page=self, is_published=True). \
        order_by('-published_on')

    def unpublished_revision(self):
        try:
            return Revision.objects.filter(page=self, is_published=False). \
            latest('created_on')
        except Revision.DoesNotExist:
            return None

    def count_revisions(self):
        return Revision.objects.filter(page=self, is_published=True).count()

    def who_checked_out(self):
        try:
            return Revision.objects.filter(page=self, is_published=False). \
            latest('created_on').author
        except Revision.DoesNotExist:
            return None

    def compare(self, rev1, rev2):
        if rev1 == rev2:
            raise ComparingSameRevision
        revisions = Revision.objects.filter(page=self,
            pk__in=sorted([rev1, rev2]))
        if revisions.count() != 2:
            raise RevisionDoesNotExist

        comparison, created = Comparison.objects.get_or_create(page=self,
            rev1=revisions[0], rev2=revisions[1])
        return comparison

    @models.permalink
    def get_absolute_url(self):
        return ('page_detail', (), {'slug': self.slug})

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['title']


class Revision(models.Model):
    """
    All Revisions belong to a Page.

    A Revision is created only when a Page is checked out.

    A Revision can only be deleted before it is published, once published it
    cannot be changed.
    """
    page = models.ForeignKey(Page)
    author = models.ForeignKey(User)
    number = models.IntegerField(default=0, editable=False)
    body = models.TextField()
    is_published = models.BooleanField(default=False)
    published_on = models.DateTimeField(blank=True, null=True, editable=False)
    created_on = models.DateTimeField(auto_now_add=True, editable=False)
    edited_on = models.DateTimeField(auto_now=True, editable=False)

    def publish(self, check_in_page=True):
        self.is_published = True
        self.save()

        if check_in_page:
            self.page.check_in()

    def __unicode__(self):
        return '%s #%s' % (self.page.title, self.number)

    class Meta:
        ordering = ['number']
        unique_together = ("page", "number")


def create_first_revision(sender, instance, created, **kwargs):
    """Creates a "blank" revision for a new page."""
    if created:
        Revision.objects.create(page=instance, author=instance.creator,
            body="hello world!", is_published=True)


def check_page_already_checked_out(page_new, page_old):
    """Checks to see if page is checked out, can't be checked out again."""
    if page_old is not None and page_new.is_checked_out and \
        page_old.is_checked_out is True:
        raise PageAlreadyCheckedOut


def check_page_unpublished_revisions(page_new):
    """Before a page is checked in there can be no unpublished revisions"""
    if not page_new.is_checked_out and \
        Revision.objects.filter(page=page_new, is_published=False).count() > 0:
        raise UnpublishedRevisionExists


def check_revision_already_published(sender, instance, **kwargs):
    """Published revisions can not be unpublished"""
    if instance.pk != None:
        if instance.is_published:
            try:
                Revision.objects.get(pk=instance.pk, is_published=True)
            except Revision.DoesNotExist:
                return
            raise AlreadyPublishedRevision


def update_published_on(sender, instance, **kwargs):
    """If page goes from not published to published, update published_on
    date."""
    published_on = datetime.datetime.now()
    latest = instance.page.latest_revision()

    if latest is None:
        number = 1
    else:
        number = latest.number + 1

    try:
        original = Revision.objects.get(pk=instance.pk)
        if not original.is_published and instance.is_published:
            instance.published_on = published_on
            instance.number = number
    except Revision.DoesNotExist:
        if instance.is_published:
            instance.published_on = published_on
            instance.number = number


def page_pre_save_maintenance(sender, instance, **kwargs):
    if instance.pk:
        check_page_already_checked_out(instance,
            Page.objects.get(pk=instance.pk))
        check_page_unpublished_revisions(instance)

post_save.connect(create_first_revision, sender=Page)
pre_save.connect(page_pre_save_maintenance, sender=Page)
pre_save.connect(check_revision_already_published, sender=Revision)
pre_save.connect(update_published_on, sender=Revision)


class Comparison(models.Model):
    page = models.ForeignKey(Page)
    rev1 = models.ForeignKey(Revision, related_name='rev1')
    rev2 = models.ForeignKey(Revision, related_name='rev2')
    diff_text = models.TextField(default='blank')

    def __unicode__(self):
        return u'%s: %s vs %s' % (self.page.title, self.rev1.pk, self.rev2.pk)


def comparison_calculate_diff(sender, instance, created, **kwargs):
    if created:
        from utils.diff_match_patch import diff_match_patch
        diff = diff_match_patch()
        diff_array = diff.diff_main(instance.rev1.body, instance.rev2.body)
        diff.diff_cleanupSemantic(diff_array)
        instance.diff_text = diff.diff_prettyHtml(diff_array)
        instance.save()

post_save.connect(comparison_calculate_diff, sender=Comparison)
