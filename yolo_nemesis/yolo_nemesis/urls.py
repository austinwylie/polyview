from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView

from cparse import views


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'yolo_nemesis.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(
        r'^favicon.ico$',
        RedirectView.as_view(
            url=staticfiles_storage.url('assets/img/favicon.ico'),
            permanent=False),
        name="favicon"
    ),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', views.index, name='index'),
    url(r'^yolo_nemesis/', views.index, name='index'),
    url(r'^faq/', views.index, name='index'),
    url(r'^search/', views.index, name='index'),
    url(r'^advsearch/', views.index, name='index'),
    url(r'^filter/', views.index, name='index'),
    url(r'^course/(?P<major>[a-zA-Z]{2,4})/(?P<number>\d{3})/$', views.index, name='index'),
    url(r'^course/$', views.index, name='index'),

    url(r'^instructor/(?P<alias>\w*)/$', views.index, name='index'),
    url(r'^instructor/$', views.index, name='index'),

    url(r'^building/(?P<code>\w*)/$', views.index, name='index'),
    url(r'^building/$', views.index, name='index'),

)
