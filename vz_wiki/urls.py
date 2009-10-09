from django.conf.urls.defaults import *
from models import Page

urlpatterns = patterns('vz_wiki.views',
    url(r'^pages:create/$', 'create_page', name='create_page'),
    url(r'^pages:edit/(?P<page_id>\d+)/$', 'edit_page', name='edit_page'),
    url(r'^pages:abandon/(?P<revision_id>\d+)/$', 'abandon_revision',
        name='abandon_revision'),
    url(r'^pages:tags', 'page_tags', name='page_tags'),
    url(r'^pages:history/(?P<page_id>\d+)/$', 'page_history',
        name='page_history'),
    url(
        r'^pages:compare\-revisions/(?P<page_id>\d+)/$',
            'compare_revisions', name='compare_revisions'),
)

urlpatterns += patterns('django.views.generic',
    url(
        r'^(?P<slug>[\w\-]+)/$',
        'list_detail.object_detail',
            {'queryset': Page.objects.select_related().all(),
            'template_name': 'vz_wiki/page_detail.html',
            'template_object_name': 'page', },
        name='page_detail',
    ),
    url(
        r'^pages:index/$',
        'list_detail.object_list', {'queryset': Page.objects.all(),
            'template_name': 'vz_wiki/page_list.html',
            'template_object_name': 'page', },
        name='page_list',
    ),
    url(
        r'^$',
        'simple.redirect_to',
        {'url': '/wiki/index/'},
        name='index',
    ),
)
