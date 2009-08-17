from django.template.defaultfilters import stringfilter
from django import template

from BeautifulSoup import BeautifulSoup, Comment

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

@register.filter
def sanitize(value, allowed_tags):
    """
    Jacked from: http://www.djangosnippets.org/snippets/1655/
    
    Argument should be in form 'tag2:attr1:attr2 tag2:attr1 tag3', where tags
    are allowed HTML tags, and attrs are the allowed attributes for that tag.
    """
    js_regex = re.compile(r'[\s]*(&#x.{1,7})?'.join(list('javascript')))
    allowed_tags = [tag.split(':') for tag in allowed_tags.split()]
    allowed_tags = dict((tag[0], tag[1:]) for tag in allowed_tags)

    soup = BeautifulSoup(value)
    for comment in soup.findAll(text=lambda text: isinstance(text, Comment)):
        comment.extract()

    for tag in soup.findAll(True):
        if tag.name not in allowed_tags:
            tag.hidden = True
        else:
            tag.attrs = [(attr, js_regex.sub('', val)) for attr, val in tag.attrs
                         if attr in allowed_tags[tag.name]]

    return soup.renderContents().decode('utf8')
