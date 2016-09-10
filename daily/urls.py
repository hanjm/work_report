from django.conf.urls import url
from daily import views

urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'^login/$', views.login, name="login"),
    url(r'^logout/$', views.logout, name="logout"),
    url(r'^(?P<date>\d{4}-\d{2}-\d{2})$', views.index, name="view"),
    url(r'^(?P<date>\d{4}-\d{2}-\d{2})/add$', views.add, name="add"),
    url(r'^(?P<date>\d{4}-\d{2}-\d{2})/export$', views.export, name="export")
]
