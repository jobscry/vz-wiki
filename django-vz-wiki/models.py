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
        
        If the page isn't checked out, create a skeleton revision, check out page.
        """
        if self.is_checked_out:
            raise PageAlreadyCheckedOut
        revision = Revision.objects.create(
            page=self,
            author=user,
            body=self.latest_revision().body
        )
        self.is_checked_out = True
        self.save()
        return revision

    def check_in(self):
        """
        When model is saved a pre_save signal will throw a UnpublishedRevisionExists
        exception if the unpublished revision isn't published or abandoned first.
        """
        self.is_checked_out = False
        self.save()
    
    def latest_revision(self):
        try:
            return Revision.objects.filter(page=self,is_published=True).latest('published_on')
        except Revision.DoesNotExist:
            return None

    def history(self):
        return Revision.objects.filter(page=self, is_published=True).order_by('-published_on')

    def unpublished_revision(self):
        try:
            return Revision.objects.filter(page=self, is_published=False).latest('created_on')
        except Revision.DoesNotExist:
            return None
    
    def count_revisions(self):
        return Revision.objects.filter(page=self, is_published=True).count()

    def who_checked_out(self):
        try:
            return Revision.objects.filter(page=self, is_published=False).latest('created_on').author
        except Revision.DoesNotExist:
            return None

    def compare(self, rev1, rev2, display_type='inline'):
        if rev1 == rev2:
            raise ComparingSameRevision
        revisions = Revision.objects.filter(page=self, pk__in=sorted([rev1, rev2]))
        if revisions.count() != 2:
            raise RevisionDoesNotExist

        comparison, created = Comparison.objects.get_or_create(
            page=self,
            rev1=revisions[0],
            rev2=revisions[1],
            display_type=display_type
        )
        return comparison
        
    @models.permalink
    def get_absolute_url(self):
        return ('page_detail', (), { 'slug': self.slug })

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
        Revision.objects.create(
            page=instance,
            author=instance.creator,
            body="hello world!",
            is_published=True,
        )

def check_page_already_checked_out(sender, instance, **kwargs):
    """Checks to see if page is checked out, can't be checked out again."""
    if instance.is_checked_out and Page.objects.filter(pk=instance.pk, is_checked_out=True).count() > 0:
        raise PageAlreadyCheckedOut
   
def check_page_unpublished_revisions(sender, instance, **kwargs):
    """Before a page is checked in there can be no unpublished revisions"""
    if not instance.is_checked_out and Revision.objects.filter(page=instance, is_published=False).count() > 0:
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
    """If page goes from not published to published, update published_on date."""
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

post_save.connect(create_first_revision, sender=Page)
pre_save.connect(check_page_already_checked_out, sender=Page)
pre_save.connect(check_page_unpublished_revisions, sender=Page)
pre_save.connect(check_revision_already_published, sender=Revision)
pre_save.connect(update_published_on, sender=Revision)

class Comparison(models.Model):
    DISPLAY_TYPE_CHOICES = (
        (u'inline', 'Inline'),
        (u'table', 'Table'),    
    )

    page = models.ForeignKey(Page)
    rev1 = models.ForeignKey(Revision, related_name='rev1')
    rev2 = models.ForeignKey(Revision, related_name='rev2')
    display_type = models.CharField(max_length='6', choices=DISPLAY_TYPE_CHOICES, default='inline')
    diff_text = models.TextField(default='blank')
    
    def __unicode__(self):
        return u'%s: [%s] %s vs %s' % (self.page.title, self.display_type, self.rev1.pk, self.rev2.pk)

def comparison_calculate_diff(sender, instance, created, **kwargs):
    if created:
        if instance.display_type == 'inline':
            instance.diff_text = calculate_inline_diff(instance.rev1.body, instance.rev2.body)
        else:
            instance.diff_text = calculate_table_diff(instance.rev1.body, instance.rev2.body)
        instance.save()
        
post_save.connect(comparison_calculate_diff, sender=Comparison)

def calculate_inline_diff(text1, text2):
    """from http://stackoverflow.com/questions/774316/python-difflib-highlighting-differences-inline/788780#788780"""
    seqm = difflib.SequenceMatcher(None, text1, text2)
    output = []
    for opcode, a0, a1, b0, b1 in seqm.get_opcodes():
        if opcode == 'equal':
            output.append(seqm.a[a0:a1])
        elif opcode == 'insert':
            output.append('<ins>'+seqm.b[b0:b1]+'</ins>')
        elif opcode == 'delete':
            output.append('<del>'+seqm.a[a0:a1]+'</del>')
        elif opcode == 'replace':
            pass
        else:
            raise RuntimeError, "unexpected code"
    return u''.join(output)

def calculate_table_diff(text1, text2):
    """
    TODO:  table doesn't wrap, is this a Python problem?
    """
    html_differ = difflib.HtmlDiff(wrapcolumn=10)
    return html_differ.make_table(text1.splitlines(), text2.splitlines())
