from django.conf.urls import url
from weekly import views

urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'^(?P<date>\d{4}-\d{2}-\d{2})$', views.view_by_date, name="view_by_date"),
    url(r'^(?P<year>\d{4})/(?P<week>\d{1,2})$', views.index, name="view"),
    url(r'^(?P<year>\d{4})/(?P<week>\d{1,2})/add$', views.add, name="add"),
    url(r'^(?P<year>\d{4})/(?P<week>\d{1,2})/export$', views.export, name="export")
]
