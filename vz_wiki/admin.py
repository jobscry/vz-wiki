from django.contrib import admin
from models import Page, Revision, Comparison


def latest_revision_display(obj):
    latest_revision = obj.latest_revision()
    if latest_revision is None:
        return '0'
    return u'%s' % latest_revision.number
latest_revision_display.short_description = 'Version'


def who_checked_out(obj):
    return obj.who_checked_out()
who_checked_out.short_description = 'Checked out by'


def make_editable(modelAdmin, request, queryset):
    queryset.update(is_editable=True)
make_editable.short_description = 'Make the selected pages editable'


def make_not_editable(modelAdmin, request, queryset):
    queryset.update(is_editable=False)
make_not_editable.short_description = 'Make the selected pages not editable'


def make_checked_in(modelAdmin, request, queryset):
    queryset.update(is_checked_out=False)
make_checked_in.short_description = 'Check in the selected pages'


def make_checked_out(modelAdmin, request, queryset):
    queryset.update(is_checked_out=True)
make_checked_out.short_description = 'Check out the selected pages'


class RevisionInline(admin.StackedInline):
    model = Revision
    extra = 1


class PageAdmin(admin.ModelAdmin):
    actions = [make_editable, make_not_editable, make_checked_in,
        make_checked_out]
    inlines = [RevisionInline]
    prepopulated_fields = {'slug': ('title', )}
    list_display = ('title', latest_revision_display, 'is_editable',
        'is_checked_out', who_checked_out, 'created_on')
    list_filter = ('is_editable', 'is_checked_out')

admin.site.register(Page, PageAdmin)
admin.site.register(Revision)
admin.site.register(Comparison)
