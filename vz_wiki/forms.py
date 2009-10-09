from django.forms import ModelForm
from tagging.forms import TagField
from models import Page, Revision


class PageForm(ModelForm):

    class Meta:
        model = Page
        exclude = ['creator', 'is_checked_out']


class RevisionForm(ModelForm):
    tags = TagField(label='Tags for Page')

    class Meta:
        model = Revision
        exclude = ['page', 'author']
