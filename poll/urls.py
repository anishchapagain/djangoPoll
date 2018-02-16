"""mypoll URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from poll import views
from poll.fusioncharts import FusionCharts


app_name='poll'
urlpatterns = [
    # url(r'(?P<title>Dan?.*)$',views.post_detail,name='post_detail'),
    # url(r'^(?P<pk>[0-9]+)/results/$', views.ResultsView.as_view(), name='results'),
    # url(r'^(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),
    url(r'poll/$', views.IndexView, name='index'),
    # ex: /poll/
    url(r'^index/$', views.IndexView, name='index'),
    url(r'^filter/$', views.pollFilter, name='filter'),

    url(r'^testing/(?P<param1>[0-9]+)/$', views.testing, name='testing'),

    url(r'^(?P<question_id>[0-9]+)/$', views.detail, name='detail'),
    url(r'^(?P<question_id>[0-9]+)/results/$', views.results, name='results'),
    url(r'^(?P<question_id>[0-9]+)/vote/$', views.vote, name='vote'),
    url(r'^(?P<question_id>[0-9]+)/choice/$', views.add_choice, name='add_choice'),
    url(r'^(?P<question_id>[0-9]+)/delete/$', views.delete_question, name='delete_question'),
    url(r'^add$', views.add_poll, name='add_poll'),

    url(r'^profile/(?P<username>[a-zA-Z0-9]+)$', views.profile, name='profile'),
    url(r'^email/$', views.email, name='email'),
    url(r'^viewall/$', views.viewAllResults, name='viewAllResults'),

    url(r'^signup/$', views.signup, name='signup'),
    url(r'^$', auth_views.login, name='login'),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout,{'next_page': 'out/'}, name='logout'),
    url(r'^logout/out/$', auth_views.login, name='login'),
]

