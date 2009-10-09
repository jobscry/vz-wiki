VZ_WIKI
===============

VZ_Wiki is a Django powered wiki app.

TODO
----

* Search
* Tag filtering
* File/Attachments

Installation
------------

`sudo easy_install django_vz_wiki`

Add the following to *urls.py*

`(r'^wiki/', include('vz_wiki.urls')),`

Add the following to *INSTALED_APPS*

`'django_vz_wiki',`

Integration Into Existing Templates
-----------------------------------

**Be sure to uncomment the the egg based templated loader in *TEMPLATE_LOADERS***

`django.template.loaders.eggs.load_template_source`

All wiki templates have the following:

`{% extends "base.html" %}`

The block tags match the suggested best practices by [Lincoln Loop](http://lincolnloop.com/django-best-practices/apps/modules/templates.html)

Template blocks include:

* **title** - full page title
* **extra_head** - for extra css/javascript
* **body** - wraps everything inside body tag
* **content_title** - title for wiki page
* **content** - wiki page contents
* **block vz_wiki_page_menu** - this is required for page options, it should be wrapped
inside `<ul></ul>`.

Settings
--------

You can add default allowed tags.  By adding **WIKI_ALLOWED_TAGS** to your settings file.  The  setting should be in form 'tag2:attr1:attr2 tag2:attr1 tag3', where tags are allowed HTML tags, and attrs are the allowed attributes for that tag.  Default is an empty string.

You can also change the default Wiki page link base (*/wiki*) by adding **WIKI_BASE** to your settings file.

Linking to Wiki Pages
---------------------

First, include **wiki_tags** template tags.

`{% load markup wiki_tags %}`

Second, link to the desired wiki page by putting something like the following inside
your text:

`Blah blah blah [[title of the wiki page]]`

Finally, add the *wiki_link* filter like this:

`{{ latest_revision.body|sanitize|wiki_link|markdown }}`

Extra Template Stuff
--------------------

You can add:

`{% block vz_wiki_page_menu %}{% endblock %}`

This will add:

`<ul>`

`    <li><a href="{% url page_list %}" title="page list">Page List</a></li>`

`    {% if perms.page.can_add %}`

`    <li><a href="{% url create_page %}" title="create a page">Create a Page</a></li>`

`    {% endif %}`

`</ul>`

You can also do this manually.

Dependencies
--------------

* [Django](http://djangoproject.com)
* [Python Markdown](http://www.freewisdom.org/projects/python-markdown)
* [Beautiful Soup](http://www.crummy.com/software/BeautifulSoup)
* [Django Tagging](http://code.google.com/p/django-tagging/)
