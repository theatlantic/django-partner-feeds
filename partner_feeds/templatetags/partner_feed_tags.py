from django import template
from partner_feeds.models import Partner
register = template.Library()

@register.assignment_tag
def get_partners(*args):
    partners = []
    for name in args:
        partner = Partner.objects.get(name=name)
        partner.posts = partner.post_set.all().order_by('-date')
        partners.append(partner)
    return partners