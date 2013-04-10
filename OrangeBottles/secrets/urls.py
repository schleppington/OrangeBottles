from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('secrets.views',
#- homepage will display all recently published blackmails
    url(r'^$', 'index'), 
    
#- details for single item
    url(r'^details/(?P<bm_id>\d+)/$', 'details'),
    
#- create a new item
    url(r'^create/$', 'create'),
    
#- edit an item
    url(r'^edit/(?P<bm_id>\d+)/$', 'edit'),
    
#- sign into your account
    url(r'^signin/$', 'signin'),
    
#- create an account
    url(r'^signup/$', 'signup'),
    
#- sign out of an account
    url(r'^signout/$', 'signout'),

#- edit an account
    url(r'^editaccount/$', 'editaccount'),
        
)
