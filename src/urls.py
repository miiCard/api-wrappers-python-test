from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'TestHarness.views.home', name='home'),
    url(r'^assuranceimage$', 'TestHarness.views.assuranceimage', name='assuranceimage')
)
