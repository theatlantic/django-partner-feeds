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


_link_template = u'<a href="{url}" class="rounded-button blue " target="_blank">{title}</a> '

def title(instance):
    return mark_safe(_link_template.format(url=escape(instance.url), title=escape(instance.title)))

title.short_description = "Title"
title.allow_tags = True


class PostAdmin(admin.ModelAdmin):
    list_display = [title, 'byline', 'date', 'partner']
    ordering = ['-date']
    list_filter = ['partner',]

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
