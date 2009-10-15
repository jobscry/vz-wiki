from django.conf.urls.defaults import *
from models import WikiPage

urlpatterns = patterns('vz_wiki.views',
    url(r'^pages:create/$', 'create_page', name='create_wikipage'),
    url(r'^pages:edit/(?P<page_id>\d+)/$', 'edit_page', name='edit_wikipage'),
    url(r'^pages:abandon/(?P<revision_id>\d+)/$', 'abandon_revision',
        name='abandon_wikipage_revision'),
    url(r'^pages:tags', 'page_tags', name='wikipage_tags'),
    url(r'^pages:history/(?P<page_id>\d+)/$', 'page_history',
        name='wikipage_history'),
    url(
        r'^pages:compare\-revisions/(?P<page_id>\d+)/$',
            'compare_revisions', name='compare_wikipage_revisions'),
)

urlpatterns += patterns('django.views.generic',
    url(
        r'^(?P<slug>[\w\-]+)/$',
        'list_detail.object_detail',
            {'queryset': WikiPage.objects.select_related().all(),
            'template_name': 'vz_wiki/page_detail.html',
            'template_object_name': 'wikipage', },
        name='wikipage_detail',
    ),
    url(
        r'^pages:index/$',
        'list_detail.object_list', {'queryset': WikiPage.objects.all(),
            'template_name': 'vz_wiki/page_list.html',
            'template_object_name': 'wikipage', },
        name='wikipage_list',
    ),
    url(
        r'^$',
        'simple.redirect_to',
        {'url': '/wiki/index/'},
        name='index',
    ),
)
