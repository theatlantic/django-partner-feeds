from django.conf import settings
from django.db import models
from partner_feeds import tasks

# If we can import caching (IE, CacheMachine is installed) then use it
try:
	from caching.base import CachingManager, CachingMixin
	class BaseModel(CachingMixin, models.Model):
		""" Base class WITH Cache Machine caching """
		
		objects = CachingManager()
		
		class Meta:
			abstract = True
		
# Otherwise, just use the standard Django model without a mixin
except ImportError:
	class BaseModel(models.Model):
		""" Base class WITHOUT Cache Machine caching """
		class Meta:
			abstract = True
			
# set the upload path 
try:
	PARTNERS_UPLOAD_PATH = settings.PARTNER_FEED_UPLOAD_PATH
except AttributeError:
	PARTNERS_UPLOAD_PATH = settings.UPLOAD_PATH + 'partner_logos'

class Partner(BaseModel):
	""" 
	The partner who's RSS or ATOM formated content we want to retrieve and save in the database
	"""
	
	logo = models.ImageField(upload_to=PARTNERS_UPLOAD_PATH, blank=True)
	name = models.CharField(max_length=75)
	url  = models.URLField('URL', help_text='Partner Website')
	feed_url = models.URLField('Feed URL', help_text='URL of a RSS or ATOM feed', unique=True)
	date_feed_updated = models.DateTimeField('Feed last updated', null=True, blank=True)

	def __unicode__(self):
		return u"%s" % self.name

	def get_absolute_url(self):
		return self.url

	def save(self, *args, **kwargs):
		""" 
		When saving a parter update it's related posts as an asynchronous Celery task
		"""
		super(Partner, self).save(*args, **kwargs)
		tasks.update_posts_for_feed.apply_async([self, ])
		
class Post(BaseModel):
	""" 
	Post retrieved from syndicated RSS or ATOM feed
	"""
	
	partner = models.ForeignKey(Partner)
	title = models.CharField(max_length=255)
	url = models.URLField(verify_exists=False)
	guid = models.CharField(max_length=255, unique=True)
	date = models.DateTimeField()

	def __unicode__(self):
		return self.title

	def get_absolute_url(self):
		return self.url

	def save(self, *args, **kwargs):
		""" 
		If a post with the same GUID already exists, 
		then it is the same post so we should use it's ID when saving.
		"""

		if not self.pk:
			old_post = Post.objects.filter(guid=self.guid)
			if len(old_post) > 0:
				self.pk = old_post[0].pk

		super(Post, self).save(*args, **kwargs)

	class Meta:
		ordering = ('-date', )