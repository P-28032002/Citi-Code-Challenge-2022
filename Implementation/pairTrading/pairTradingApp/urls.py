from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('test', views.test, name='test'),
]

urlpatterns += staticfiles_urlpatterns()
