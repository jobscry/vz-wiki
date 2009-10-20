from haystack import indexes, site

from models import WikiPage, Revision

class WikiPageIndex(indexes.SearchIndex):
    title = indexes.CharField(model_attr='title')
    tags = indexes.CharField()
    latest_revision_number = indexes.IntegerField()
    text = indexes.CharField(document=True, use_template=True)
    url = indexes.CharField()
    created_on = indexes.DateTimeField(model_attr='created_on')
    last_edited_on = indexes.DateTimeField()
    rendered = indexes.CharField(use_template=True, indexed=False)

    def prepare(self, object):
        self.prepared_data = super(WikiPageIndex, self).prepare(object)

        self.prepared_data['url'] = object.get_absolute_url()

        revision = object.latest_revision()

        self.prepared_data['latest_revision_number'] = revision.number
        self.prepared_data['last_edited_on'] = revision.published_on
        self.prepared_data['text'] = revision.body

        return self.prepared_data

site.register(WikiPage, WikiPageIndex)