from celery.decorators import task

@task(ignore_result=True)
def update_all_partner_posts():
	return update_all_partner_posts_task(celery=True)
	
def update_all_partner_posts_task(celery=True):
	"""
	Fetch all partners, and for each one, pass the feed_url to update_posts_for_feed
	"""
	from partner_feeds.models import Partner
	from datetime import datetime

	partners = Partner.objects.all()
	for partner in partners:
		# find all the posts in the current partner feeds and update them
		if celery:
			update_posts_for_feed.delay(partner)
		else:
			update_posts_for_feed(partner)
			
		# Set the current time as when the partner feed was last retrieved
		Partner.objects.filter(pk=partner.pk).update(date_feed_updated=datetime.now())
		
@task(ignore_result=True)
def update_posts_for_feed(partner):
	return update_posts_for_feed_task(partner)
	
def update_posts_for_feed_task(partner):
	"""
	Load and parse the RSS or ATOM feed associated with the given feed url, and for each entry, parse out the individual
	entries and save each one as a partner_feeds.
	"""
	from feedparser import parse
	from partner_feeds.models import Post
	import timelib, re, time

	feed = parse(partner.feed_url)

	for entry in feed.entries:
		p = Post()
		try:
			
			p.partner_id = partner.id
			p.title = entry.title

			try:
				p.guid = entry.id
			except AttributeError:
				p.guid = entry.link

			p.url = entry.link

			# try to get the date of the entry from either 'date' or 'published', otherwise, try the date of the feed
			try:
				entry_date = re.sub('\|','', entry.date)
				entry_date = timelib.strtotime(entry_date) # convert to a timestamp
				entry_date = time.localtime(entry_date) # converts to a time.struct_time (with regards to local timezone)
				entry_date = time.strftime("%Y-%m-%d %H:%M:%S", entry_date) # converts to mysql date format
				p.date = entry_date
			except AttributeError:
				try:
					entry_date = re.sub('\|','', entry.published)
					entry_date = timelib.strtotime(entry_date) # convert to a timestamp
					entry_date = time.localtime(entry_date) # converts to a time.struct_time (with regards to local timezone)
					entry_date = time.strftime("%Y-%m-%d %H:%M:%S", entry_date) # converts to mysql date format
					p.date = entry_date
				except AttributeError:
					entry_date = timelib.strtotime(feed.date) # convert to a timestamp
					entry_date = time.localtime(entry_date) # converts to a time.struct_time (with regards to local timezone)					
					p.date =  time.strftime("%Y-%m-%d %H:%M:%S",entry_date)				

			# try to get the description if available
			try:
				p.description = entry.description
			except:
				pass

			# try to get the image url if available
			try:
				p.image_url = entry.media_content[0]['url']
			except:
				pass

			p.save()

		except AttributeError:
			# needs logging
			pass

@task(ignore_result=True)
def delete_old_posts(num_posts_to_keep=20):
	return delete_old_posts(num_posts_to_keep=20, celery=True)
	
def delete_old_posts(num_posts_to_keep=20, celery=True):
	""" 
	Fetch all partners, and for each partner,
	delete all but `num_posts_to_keep` number of posts
	"""
	from partner_feeds.models import Partner

	partners = Partner.objects.all()
	
	for partner in partners:
		if celery: 
			delete_old_posts_for_partner.delay(partner, num_posts_to_keep)
		else:
			delete_old_posts_for_partner(partner, num_posts_to_keep)
			
@task(ignore_result=True)
def delete_old_posts_for_partner(partner, num_posts_to_keep=20):
	"""
	Deletes all posts except for the most recent `num_posts_to_keep`
	Because Django won't let us do a delete of a query with an offset, we first find
	the IDs of the posts that we want to keep and then exclude them from the delete.	
	"""
	from partner_feeds.models import Post
	
	recent_posts = list(Post.objects.filter(partner=partner).values_list('id', flat=True)[:num_posts_to_keep])
	
	Post.objects.filter(partner=partner).exclude(pk__in=recent_posts).delete()
