from celery.decorators import task

@task(ignore_result=True)
def update_all_partner_posts():
	"""
	Fetch all partners, and for each one, pass the feed_url to update_posts_for_feed
	"""
	from partner_feeds.models import Partner
	from datetime import datetime

	partners = Partner.objects.all()
	for partner in partners:
		# find all the posts in the current partner feeds and update them
		update_posts_for_feed.delay(partner)

		# Set the current time as when the partner feed was last retrieved
		Partner.objects.filter(pk=partner.pk).update(date_feed_updated=datetime.now())

@task(ignore_result=True)
def update_posts_for_feed(partner):
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

			# try to get the date of the entry, otherwise, try the date of the feed
			try:
				p.date = timelib.strtodatetime(re.sub('\|','', entry.date)).strftime("%Y-%m-%d %H:%M:%S")
			except AttributeError:
				p.date =  time.strftime("%Y-%m-%d %H:%M:%S",feed.date)

			p.save()
		except AttributeError:
			# needs logging
			pass

@task(ignore_result=True)
def delete_old_posts(num_posts_to_keep=20):
	""" 
	Fetch all partners, and for each partner,
	delete all but `num_posts_to_keep` number of posts
	"""
	from partner_feeds.models import Partner

	partners = Partner.objects.all()
	for partner in partners:
		delete_old_posts_for_partner.delay(partner, num_posts_to_keep)
		
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