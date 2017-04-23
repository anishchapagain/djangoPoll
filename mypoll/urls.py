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
from django.conf.urls import include, url
from django.contrib import admin
from poll import views

app_name="poll"

urlpatterns = [
    url(r'^poll/', include('poll.urls')),
    # url(r'^contact/', include('contact_form.urls')),
    # url(r'^$',views.IndexView.as_view(), name='index'),
    url(r'^$',views.IndexView, name='index'),
    # url(r'^blogs/', include('poll.urls')),
    # url(r'[a-eA-E]{1}', include('poll.urls')),
    url(r'^admin/', admin.site.urls),
]
