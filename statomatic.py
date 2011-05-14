'''
Run this with $ python ./statomatic.py and go to http://localhost:8000/
'''

import os, sys, itertools
from  django.conf.urls.defaults import patterns
from django.template.response import SimpleTemplateResponse
from django.template import TemplateDoesNotExist
from django.http import Http404
from BeautifulSoup import BeautifulSoup
from markdown2 import markdown


me = os.path.splitext(os.path.split(__file__)[1])[0]
# helper function to locate this dir
here = lambda x: os.path.join(os.path.abspath(os.path.dirname(__file__)), x)

# SETTINGS
DEBUG=TEMPLATE_DEBUG=True
ROOT_URLCONF = me
DATABASES = { 'default': {} } #required regardless of actual usage
CONTENT_DIR = here('content')
TEMPLATE_DIRS = (CONTENT_DIR, here('templates'),)
DEPLOY_DIR = here('deploy')
INSTALLED_APPS = ('django.contrib.markup',)

def smart_render(template, context={}):
    template = template.rstrip('/')
    for suffix in ['','/index.html','index.html']:
        try:
            return SimpleTemplateResponse(template+suffix, context).render()
        except TemplateDoesNotExist:
            pass
    raise Http404

def markdownify(rendered_template):
    html = BeautifulSoup(rendered_template)
    for md in html.findAll('','md'):
        md.contents = BeautifulSoup(markdown(md.renderContents()))
    return html.renderContents() 

# VIEW
def index(request, template):
    r = smart_render(template)
    r.content  = markdownify(r.rendered_content)
    return r


def blog(request,template):
    template = 'blog/'+template.rstrip('/')
    return smart_render(template, context={'name':'bill'})

# URLS
urlpatterns = patterns('',
    # do something different with blog stuff
    #(r'^blog/(?P<template>[a-zA-Z0-9\-\.\/]*)$', blog), 
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
        print "Current directory", root
        print "Sub directories", dirs
        print "Files", files 
        for f in files:
             if f[0] != '.':
                url = root.replace(CONTENT_DIR,'')+'/'+f
                response = client.get(url)
                out = os.path.join(DEPLOY_DIR,url[1:])
                d = os.path.dirname(out)
                if not os.path.exists(d):
                    os.makedirs(d)
                f = open(out, 'w')
                f.write(response.content)
                f.close()
def run():
    sys.path += (here('.'),)
    # set the ENV
    os.environ['DJANGO_SETTINGS_MODULE'] = me
    #run the development server
    from django.core import management
    # management.call_command('runserver','0.0.0.0:8000' )
    management.execute_from_command_line()

if __name__ == '__main__':
    run()
