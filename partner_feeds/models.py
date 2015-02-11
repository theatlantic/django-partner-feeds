import os

from django.conf import settings
from django.db import models
from django.template.defaultfilters import slugify

from .tasks import update_posts_for_feed

# If we can import caching (IE, CacheMachine is installed) then use it
try:
    from caching.base import CachingManager as Manager, CachingMixin as Mixin
# Otherwise, just use the standard Django model without a mixin
except ImportError:
    from django.db.models import Manager

    class Mixin(object):
        pass


class Partner(Mixin, models.Model):
    """ The partner who's RSS or ATOM formated content we want to retrieve and save in the database
    """

    logo = models.ImageField(upload_to='img/partner-logos/', blank=True)
    name = models.CharField(max_length=75)
    url = models.URLField('URL', help_text='Partner Website')
    feed_url = models.URLField(
        'Feed URL', help_text='URL of a RSS or ATOM feed', unique=True)
    date_feed_updated = models.DateTimeField(
        'Feed last updated', null=True, blank=True)

    @property
    def slug(self):
        return slugify(self.name)

    def __unicode__(self):
        return u"%s" % self.name

    def get_absolute_url(self):
        return self.url

    def save(self, *args, **kwargs):
        """ When saving a parter update it's related posts as an asynchronous Celery task
        """
        super(Partner, self).save(*args, **kwargs)
        update_posts_for_feed.delay(self)


class Post(Mixin, models.Model):
    """ Post retrieved from syndicated RSS or ATOM feed
    """

    partner = models.ForeignKey(Partner)
    title = models.CharField(max_length=255)
    url = models.URLField('URL')
    guid = models.CharField('GUID', max_length=255)
    byline = models.CharField(max_length=255, blank=True, default='')
    date = models.DateTimeField()
    image_url = models.URLField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ("guid", "partner")

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return self.url

    def save(self, *args, **kwargs):
        """
        If a post with the same partner_id and GUID already exists,
        then it is the same post so we should use it's ID when saving.
        """

        if not self.pk:
            old_post = Post.objects.filter(partner__id=self.partner.id, guid=self.guid)
            if len(old_post) > 0:
                self.pk = old_post[0].pk
        super(Post, self).save(*args, **kwargs)

    class Meta:
        ordering = ('-date', )
