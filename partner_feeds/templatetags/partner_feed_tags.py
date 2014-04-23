from django import template
from partner_feeds.models import Partner, Post
register = template.Library()


@register.assignment_tag
def get_partners(*partner_names):
    """
    Given a list of partner names, return those partners with posts attached to
    them in the order that they were passed to this function

    """
    partners = list(Partner.objects.filter(name__in=partner_names))
    for partner in partners:
        partner.posts = Post.objects.filter(partner=partner)
    partners.sort(key=lambda p: partner_names.index(p.name))
    return partners
