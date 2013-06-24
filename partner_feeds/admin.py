from django.contrib import admin
from django.conf import settings

from .models import Partner, Post

try:
    from ckeditor.widgets import CKEditorWidget
except ImportError:
    pass


class PartnerAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_logo', 'feed_url', 'date_feed_updated', ]

    def display_logo(self, instance):
        if instance.logo:
            return '<img src="{}{}" />'.format(settings.STATIC_URL, instance.logo)
        else:
            return ''
    display_logo.allow_tags = True
    display_logo.short_description = 'Logo'

    fields = ['name', 'logo', 'url', 'feed_url']


class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'byline', 'date', 'partner', ]
    ordering = ['-date']

    def formfield_for_dbfield(self, field, **kwargs):
        if field.name == 'description':
            try:
                kwargs['widget'] = CKEditorWidget()
            except NameError:
                pass
        return super(PostAdmin, self).formfield_for_dbfield(field, **kwargs)

admin.site.register(Partner, PartnerAdmin)
admin.site.register(Post, PostAdmin)
