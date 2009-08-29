from django.forms import ModelForm
from models import Page, Revision

class PageForm(ModelForm):
    class Meta:
        model = Page
        exclude = ['creator',]

class RevisionForm(ModelForm):
    class Meta:
        model = Revision
        exclude = ['page', 'author']
