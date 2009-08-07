from django.template.defaultfilters import stringfilter
from django import template

import re

WIKI_BASE = '/wiki'
wiki_link_pattern = re.compile('\[\[([^\]]+)\]\]')
white_space_pattern = re.compile('\s+')

register = template.Library()

@register.filter
@stringfilter
def wiki_link(text):
    """
    Search text for [[link_me]], replace with <a href="WIKI_BASE/link_me">link_me</a>
    """
    return wiki_link_pattern.sub(get_link, text)

wiki_link.is_safe = True

def get_link(match_obj):
    """
    Creates link text
    """
    text = match_obj.group(0)[2:-2]
    slug = white_space_pattern.sub('-', text.lower())
    return u'<a href="%s/%s" title="%s">%s</a>' % (WIKI_BASE, slug, text, text)
