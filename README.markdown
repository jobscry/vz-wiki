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

Add the follwing to *INSTALED_APPS*

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
