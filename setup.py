try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages


setup(
    name='django-partner-feeds',
    version='2.0.15',
    author_email='ATMOprogrammers@theatlantic.com',
    packages=find_packages(),
    url='https://github.com/theatlantic/django-partner-feeds',
    description='Consume partner RSS or ATOM feeds',
    long_description=open('README.rst').read(),
    include_package_data=True,
    install_requires=[
        "Django >= 1.2",
        "celery >= 2.1.4",
        "django-celery >= 2.1.4",
        "feedparser >= 5",
        "timelib",
    ],
)