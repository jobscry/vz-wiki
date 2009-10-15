from django.forms import ModelForm
from tagging.forms import TagField
from models import WikiPage, Revision


class WikiPageForm(ModelForm):

    class Meta:
        model = WikiPage
        exclude = ['creator', 'is_checked_out']


class RevisionForm(ModelForm):
    tags = TagField(label='Tags for WikiPage')

    class Meta:
        model = Revision
        exclude = ['wikipage', 'author']
