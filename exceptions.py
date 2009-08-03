class PageAlreadyCheckedOut(Exception):
    "Paged check out, please check it in"
    pass

class UnpublishedRevisionExists(Exception):
    "This page has an unpublished revision, please publish or discard any drafts"
    pass

class AlreadyPublishedRevision(Exception):
    "This revision has already been published, this cannot be undone."
    pass
