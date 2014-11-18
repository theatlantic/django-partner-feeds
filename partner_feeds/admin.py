from django.contrib import admin
from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils.html import escape

from .models import Partner, Post

try:
    from ckeditor.widgets import CKEditorWidget
except ImportError:
    pass


class PartnerAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_logo', 'feed_url', 'date_feed_updated', ]

    def display_logo(self, instance):
        if instance.logo:
            return '<img src="{}{}" />'.format(settings.MEDIA_URL, instance.logo)
        else:
            return ''
    display_logo.allow_tags = True
    display_logo.short_description = 'Logo'

    fields = ['name', 'logo', 'url', 'feed_url']


class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'byline', 'date', 'partner', 'link']
    ordering = ['-date']
    list_filter = ['partner',]

    def link(self, instance):
        return mark_safe(
            u'<a href="{url}" class="rounded-button small" target="_blank">'
            u'<img src="{static_url}custom_admin/img/icons/icon-tools-viewsite-link.png" alt="Link">'
            u'</a>'.format(url=escape(instance.url), static_url=settings.STATIC_URL))

    link.short_description = "Link"
    link.allow_tags = True

    def formfield_for_dbfield(self, field, **kwargs):
        if field.name == 'description':
            try:
                kwargs['widget'] = CKEditorWidget()
            except NameError:
                pass
        return super(PostAdmin, self).formfield_for_dbfield(field, **kwargs)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        # Django sends an obj of None to ask whether you're allowed to
        # see the change list at all, so kick the question upstairs
        if obj is None:
            return super(PostAdmin, self).has_change_permission(request, obj)
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Partner, PartnerAdmin)
admin.site.register(Post, PostAdmin)
