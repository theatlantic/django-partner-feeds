from distutils.core import setup

setup(
    name='Partner Feeds',
    version=__import__('partner_feeds').__version__,
    author_email='ATMOprogrammers@theatlantic.com',
    packages=['partner_feeds'],
    url='https://github.com/theatlantic/django-partner-feeds',
    description='Consume partner RSS or ATOM feeds',
    long_description=open('README.rst').read(),
    install_requires=[
        "Django >= 1.2",
        "celery >= 2.1.4",
        "django-celery >= 2.1.4",
        "feedparser >= 5",
        "timelib",
    ],
)