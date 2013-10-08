from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'TestHarness.views.home', name='home'),
    url(r'^assuranceimage$', 'TestHarness.views.assuranceimage', name='assuranceimage'),
    url(r'^cardimage$', 'TestHarness.views.cardimage', name='cardimage'),
    url(r'^sha1$', 'TestHarness.views.sha1', name='sha1')
)
