#! /usr/bin/env python

'''
Run this with $ python ./statomatic.py runserver and go to http://localhost:8000/
Deploy with $ python ./statomatic.py render and rsync your files to a public_html folder.
'''

import os, sys, itertools, argparse
from  django.conf.urls.defaults import patterns
from django.template.response import SimpleTemplateResponse
from django.template import TemplateDoesNotExist
from django.http import Http404
from BeautifulSoup import BeautifulSoup
from markdown2 import markdown
from datetime import datetime

BeautifulSoup.QUOTE_TAGS['code'] = None

# helper function to locate this dir
here = lambda x: os.path.join(os.path.abspath(os.curdir), x)
me = os.path.splitext(os.path.split(__file__)[1])[0]

# SETTINGS
DEBUG = TEMPLATE_DEBUG = True
ROOT_URLCONF = me
DATABASES = {'default': {}}  # required regardless of actual usage
CONTENT_DIR = here('content')
TEMPLATE_DIRS = (CONTENT_DIR, here('templates'),)
DEPLOY_DIR = here('')
INSTALLED_APPS = ('django.contrib.markup',)
ALLOWED_INCLUDE_ROOTS = (os.path.expanduser('~'),)


def smart_render(template, context={}):
    '''
    takes a path and tries to render it directly or the index file within it.
    TODO: can make pretty urls in the future by putting all files in folders and
    naming them index
    '''
    template = template.rstrip('/')
    for suffix in ['', '/index.html', 'index.html']:
        try:
            return SimpleTemplateResponse(template + suffix, context).render()
        except TemplateDoesNotExist:
            pass
    raise Http404


def markdownify(rendered_template):
    '''
    parse a rendered temaplte for tags that have class="md" and replace the
    contents of the tag withthe marked up results.
    '''
    html = BeautifulSoup(rendered_template)
    for md in html.findAll('', 'md'):
        md.contents = BeautifulSoup(markdown(md.renderContents()))
    return html.renderContents()


def content_list(directory):
    '''
    gives a list of urls and title in an absolute dir or reletive to the content dir
    '''
    real_directory = os.path.join(CONTENT_DIR, directory)
    for f in os.listdir(real_directory):
            # ignore hidden files
            f = os.path.join(real_directory, f)
            if os.path.isfile(f) and f[-4:] == 'html':
                post_path = os.path.join(real_directory, f)
                post = SimpleTemplateResponse(post_path).render()
                html = BeautifulSoup(post.rendered_content)
                title = html.find('title')
                published = html.find('time') or None
                if published:
                    published = datetime.strptime(published['datetime'], '%Y-%m-%d')
                url = post_path.replace(CONTENT_DIR, '')
                yield {
                    'title': title.contents[0].strip(),
                    'url': url,
                    'published': published}


# VIEW
def index(request, template):
    blog_posts = list(content_list('blog'))
    r = smart_render(template, context={
            'blog_posts': blog_posts,
            'request': request,
        })
    r.content = markdownify(r.rendered_content)
    return r


# URLS
urlpatterns = patterns('',
    (r'^(?P<template>[a-zA-Z0-9\-\.\/]*)$', index))


# RENDER
def render():
    '''
    Takes everything in the CONTENT folder and renders and writes it to the
    DEPLOY folder
    '''
    from django.test.client import Client
    client = Client()
    for root, dirs, files in os.walk(CONTENT_DIR):
        for f in files:
            # ignore hidden files
            if f[0] != '.':
                url = root.replace(CONTENT_DIR, '') + '/' + f
                response = client.get(url)
                out = os.path.join(DEPLOY_DIR, url[1:])
                d = os.path.dirname(out)
                if not os.path.exists(d):
                    os.makedirs(d)
                f = open(out, 'w')
                f.write(response.content)
                f.close()


if __name__ == '__main__':
    # parse args
    parser = argparse.ArgumentParser(description='Django-statomatic for the win.')
    parser.add_argument('--base',
                        help='''base of the site containing a ./content and
                        ./templates folder and deploying to this folder directly''',
                        default='0.0.0.0:8000')
    parser.add_argument('--address',
                        help='ip address and port to run on (default: 0.0.0.0:8000)',
                        default='0.0.0.0:8000')
    parser.add_argument('command', type=str,
                        choices=['runserver', 'render'],
                        help='Run the devserver or render content to the deploy folder, respectivly')

    args = parser.parse_args()
    from django.core import management
    # set the ENV
    sys.path += (here('.'),)
    os.environ['DJANGO_SETTINGS_MODULE'] = me
    if args.command == 'render':
        render()
    elif args.command == 'runserver':
        management.call_command('runserver', args.address)


