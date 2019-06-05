from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import generics
from api.models import Songs
from api.serializers import SongsSerializer

class ListSongsView(generics.ListAPIView):
    queryset = Songs.objects.all()
    serializer_class = SongsSerializer
	
def index(request):
	songs = Songs.objects.all()
	output = "<ul>"
	output += '<li>'.join([s.title+' '+s.artist for s in songs])+"</li>"
	output += "</ul>"
	return HttpResponse(output)