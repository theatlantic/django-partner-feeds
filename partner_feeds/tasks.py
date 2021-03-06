from celery.decorators import task


@task(ignore_result=True)
def update_all_partner_posts(async=True):
    """ Fetch all partners, and for each one, pass the feed_url to update_posts_for_feed
    """
    from partner_feeds.models import Partner

    partners = Partner.objects.all()
    for partner in partners:
        # find all the posts in the current partner feeds and update them
        if async:
            update_posts_for_feed.delay(partner)
        else:
            update_posts_for_feed(partner)


@task(ignore_result=True)
def update_posts_for_feed(partner):
    """ Load and parse the RSS or ATOM feed associated with the given feed url, and
    for each entry, parse out the individual entries and save each one as a partner_feeds.

    feedparser does a good job normalizing the data, but for a couple of fields we need to
    do a little more work
    """
    from feedparser import parse
    from partner_feeds.models import Post, Partner
    import timelib
    import time
    from datetime import datetime
    from django.utils.text import get_text_list

    feed = parse(partner.feed_url)

    for entry in feed.entries:

        # Required: title, link, skip the entry if it doesn't have them
        if 'title' in entry or 'link' in entry:
            p = Post(partner_id=partner.id, title=entry.title)

            # Links and GUID
            if 'id' in entry:
                p.guid = entry.id
            else:
                p.guid = entry.link
            p.url = entry.link

            # Date
            if 'date' in entry:
                entry_date = entry.date
            elif 'published' in entry:
                entry_date = entry.published
            elif 'date' in feed:
                entry_date = feed.date
            else:
                entry_date = None

            # entry.date and entry.published appear to be strings while
            # feed.date is a time.struct_time for some reason
            if type(entry_date) is not time.struct_time:
                entry_date = timelib.strtotime(entry_date)  # convert to a timestamp
                entry_date = time.localtime(entry_date)  # converts to a time.struct_time (with regards to local timezone)

            if entry_date is not None:
                entry_date = time.strftime("%Y-%m-%d %H:%M:%S", entry_date)  # converts to mysql date format
            else:
                entry_date = time.strftime("%Y-%m-%d %H:%M:%S")

            p.date = entry_date

            # feedparser doesn't seem to save the ATOM summary tag to
            # entry.description, but the summary is saved as one of the
            # rows in the entry.content list
            #
            # To find the summary, we loop through the list and
            # use the smallest field
            if 'content' in entry and len(entry.content) > 1:
                summary = entry.content.pop(0)['value']
                for content in entry.content:
                    if len(content['value']) < len(summary):
                        summary = content['value']
                p.description = summary
            elif 'description' in entry:
                p.description = entry.description

            if 'media_content' in entry and 'url' in entry.media_content[0]:
                p.image_url = entry.media_content[0]['url']

            if 'authors' in entry and entry.authors[0]:
                authors = [a['name'] for a in entry.authors if 'name' in a]
                p.byline = get_text_list(authors, 'and')
            elif 'author' in entry:
                p.byline = entry.author

            p.save()

    # Set the current time as when the partner feed was last retrieved
    # Needs to be an UPDATE and not a SAVE or else we will get an infinite loop
    Partner.objects.filter(
        pk=partner.pk).update(date_feed_updated=datetime.now())


@task(ignore_result=True)
def delete_old_posts(num_posts_to_keep=20, async=True):
    """ Fetch all partners, and for each partner,
    delete all but `num_posts_to_keep` number of posts
    """
    from partner_feeds.models import Partner

    partners = Partner.objects.all()

    for partner in partners:
        if async:
            delete_old_posts_for_partner.delay(partner, num_posts_to_keep)
        else:
            delete_old_posts_for_partner(partner, num_posts_to_keep)


@task(ignore_result=True)
def delete_old_posts_for_partner(partner, num_posts_to_keep=20):
    """ Deletes all posts except for the most recent `num_posts_to_keep`
    Because Django won't let us do a delete of a query with an offset, we first find
    the IDs of the posts that we want to keep and then exclude them from the delete.
    """
    from partner_feeds.models import Post

    recent_posts = list(Post.objects.filter(
        partner=partner).values_list('id', flat=True)[:num_posts_to_keep])

    Post.objects.filter(partner=partner).exclude(pk__in=recent_posts).delete()
