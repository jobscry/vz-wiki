from django.contrib.auth.decorators import permission_required
from django.http import HttpResponseForbidden, HttpResponseBadRequest, Http404
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from tagging.models import Tag, TaggedItem
from tagging.utils import parse_tag_input
from models import Page, Revision
from forms import PageForm, RevisionForm
from exceptions import RevisionDoesNotExist


def page_tags(request):
    tags_string = request.GET.get('tags', None)
    if tags_string is not None:
        tag_list = parse_tag_input(tags_string)
        page_list = TaggedItem.objects.get_union_by_model(Page, tags_string)
    else:
        page_list = None
        tag_list = None
    return render_to_response('vz_wiki/page_tags.html',
        {'page_list': page_list, 'tag_list': tag_list},
        context_instance=RequestContext(request))


def compare_revisions(request, page_id):
    """
    Compare revisions from page using Python's Difflib.

    Page is page_id, revision number to compare are from GET.  Revision numbers
    are rev1 and rev2.

    Templates: ``compare_revisions.html``
    Context:
        page
            Page object
        comparision
            Comparision object from page, rev1 and rev2
    """
    page = get_object_or_404(Page, pk=page_id)
    rev1 = request.GET.get('rev1', None)
    rev2 = request.GET.get('rev2', None)
    if rev1 is None or rev2 is None:
        return HttpResponseBadRequest('Missing rev1 and rev2.')
    try:
        comparison = page.compare(rev1, rev2)
    except RevisionDoesNotExist:
        raise Http404
    return render_to_response('vz_wiki/compare_revisions.html',
        {'page': page, 'comparison': comparison},
        context_instance=RequestContext(request))


def page_history(request, page_id):
    """
    List of page history.

    Templates: ``page_history.html``
    Context:
        page
            Page object
    """
    page = get_object_or_404(Page, pk=page_id)
    return render_to_response('vz_wiki/page_history.html',
        {'page': page},
        context_instance=RequestContext(request))


def abandon_revision(request, revision_id):
    """
    Abandons revision, deletes it without publishing it.

    Redirects to revision's parent page.

    Templates: none
    Context:
        none
    """
    revision = get_object_or_404(Revision, pk=revision_id, is_published=False)
    if revision.author != request.user:
        return HttpResponseForbidden(
            'You cannot abandon this revision, it does not belong to you.')
    page = revision.page
    revision.delete()
    page.check_in()
    request.user.message_set.create(message='Revision abandoned.')
    return redirect(page)

abandon_revision = permission_required(
    'vz_wiki.page.can_change')(abandon_revision)


def edit_page(request, page_id):
    """
    Creates/saves/publishes a page's revision.

    If page is checked out and current user isn't the "checker outer",
    don't allow edit.  Otherwise open the Page.unpublished_revision().

    Templates: ``edit_page.html``
    Context:
        page
            Page object
        form
            RevisionForm ojbect
    """
    page = get_object_or_404(Page, pk=page_id)
    if page.is_checked_out:
        if page.who_checked_out() != request.user:
            request.user.message_set.create(
                message='This page is already checked out.')
            return redirect(page)
        unpublished_revision = page.unpublished_revision()
    else:
        unpublished_revision = page.check_out(user=request.user)

    if request.method == 'POST':
        form = RevisionForm(request.POST, instance=unpublished_revision)
        if form.is_valid():
            Tag.objects.update_tags(page, form.cleaned_data['tags'])
            unpublished_revision = form.save(commit=False)
            if unpublished_revision.is_published:
                unpublished_revision.publish()
                request.user.message_set.create(message="Revision published.")
                return redirect(page)
            else:
                unpublished_revision.save()
    else:
        form = RevisionForm(initial={'tags': page.tags},
            instance=unpublished_revision)

    return render_to_response('vz_wiki/edit_page.html',
        {'form': form, 'page': page,
        'unpublished_revision': unpublished_revision},
        context_instance=RequestContext(request))

edit_page = permission_required('vz_wiki.page.can_change')(edit_page)


def create_page(request):
    """
    Creates a new page.

    Templates: ``create_page.html``
    Context:
        form
            PageForm object
    """
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            page = form.save(commit=False)
            page.creator = request.user
            page.save()
            return redirect(page)
    else:
        form = PageForm()

    return render_to_response('vz_wiki/create_page.html',
        {'form': form}, context_instance=RequestContext(request))

create_page = permission_required('vz_wiki.page.can_add')(create_page)
