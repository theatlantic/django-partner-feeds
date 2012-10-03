================
Partner Feeds 2
================

``Partner Feeds`` is Django application which will read posts from an RSS or ATOM feeds and save them into a database for
easy retrieval.

Installation
------------
Add ``partner_feeds`` to the ``INSTALLED_APPS`` in ``settings.py``::

	# settings.py
	INSTALLED_APPS = (
		...
		"partner_feeds",
		...
	)
	PARTNER_FEED_UPLOAD_PATH = 'path/to/logo/uploads/'
	
Each feed has a partner logo which is saved in the location specified in ``settings.PARTNER_FEED_UPLOAD_PATH``.
If no value is specified for ``PARTNER_FEED_UPLOAD_PATH`` PartnerFeeds will instead use
``settings.UPLOAD_PATH + 'partner_logos'`` when saving and retrieving partner logo files.

Usage
-----
Each partner has a feed and posts for that feed are automatically retrieved each time a partner is saved into the
database.  In order to get this syndicated content to continue updating, ``partner_feeds.tasks.update_all_partner_posts``
should be added as a periodic task in ``Djcelery``.


Data Model
----------
**Partner**
	* ``name`` - CharField, max 75 characters
	* ``logo`` - ImageField, partner's logo
	* ``feed_url`` - URLField, URL of ATOM or RSS Feed
	* ``date_last_updated`` - DateTimeField, automatically updated on save
	
**Post**
	* ``partner`` - ForeignKey
	* ``title`` - CharField
	* ``url`` - URLField
	* ``guid`` - CharField, used to identify the posts for updates
	* ``date`` - DateTimeField, date published of post, or of the feed, or failing that, the date the date the post was updated
	* ``byline`` - CharField, human formated string of any authors for this article
	

