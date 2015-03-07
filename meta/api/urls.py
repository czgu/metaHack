from django.conf.urls import patterns, url

from api import views

urlpatterns = patterns(
    '',
    url(r'^image/$', views.image_handler, name='image'),
    url(r'^recipe/$', views.recipe_handler, name='recipe'),
    url(r'^list/$', views.list_handler, name='list')
)
