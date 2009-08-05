from django.contrib.auth.decorators import permission_required
from django.http import HttpResponseForbidden
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from vz_wiki.models import Page, Revision
from vz_wiki.forms import PageForm, RevisionForm

def page_history(request, page_id):
    page = get_object_or_404(Page, pk=page_id)
    return render_to_response(
        'page_history.html',
        { 'page': page, },
        context_instance=RequestContext(request)
    ) 
    

def abandon_revision(request, revision_id):
    revision = get_object_or_404(Revision, pk=revision_id, is_published=False)
    if revision.author != request.user:
        return HttpResponseForbidden('You cannot abandon this revision, it does not belong to you.')
    page = revision.page
    revision.delete()
    page.check_in()
    request.user.message_set.create(message='Revision abandoned.')
    return redirect(page)

abandon_revision = permission_required('vz_wiki.page.can_change')(abandon_revision)

def edit_page(request, page_id):
    page = get_object_or_404(Page, pk=page_id)
    if page.is_checked_out:
        if page.who_checked_out() != request.user:
            request.user.message_set.create(message='This page is already checked out.')
            return redirect(page)
        revision = page.unpublished_revision()
    else:
        revision = page.check_out(user=request.user)

    if request.method == 'POST':
        form = RevisionForm(request.POST, instance=revision)
        if form.is_valid():
            revision = form.save(commit=False)
            if revision.is_published:
                revision.publish()
                request.user.message_set.create(message="Revision published.")
                return redirect(page)
            else:
                revision.save()
    else:
        form = RevisionForm(instance=revision)

    return render_to_response(
        'edit_page.html',
        {
            'form': form,
            'page': page,
        },
        context_instance=RequestContext(request)
    )       
            
edit_page = permission_required('vz_wiki.page.can_change')(edit_page)    

def create_page(request):
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            page = form.save(commit=False)
            page.creator = request.user
            page.save()
            return redirect(page)
    else:
        form = PageForm()

    return render_to_response(
        'create_page.html',
        { 'form': form },
        context_instance=RequestContext(request)
    )
create_page = permission_required('vz_wiki.page.can_add')(create_page)
