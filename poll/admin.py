from django.contrib import admin
from poll.models import *
from django import forms

#https://docs.djangoproject.com/en/2.0/intro/tutorial07/
# class QuestionInLine(admin.StackedInline):
#     model = Question

class ChoiceInline(admin.TabularInline):#StachedInline , TabularInline
    model = Choice
    extra = 4

class QuestionAdmin(admin.ModelAdmin):
    # fields = ['pub_date', 'question_text']
    fieldsets = [
        ('Question',{'fields':['question_text']}),
        ('Date Information',{'fields':['pub_date']}),
        ]
    inlines = [ChoiceInline]
    list_display = ('id','question_text','pub_date',)
    list_filter = ['pub_date']

class ChoiceAdmin(admin.ModelAdmin):
    fields = ['choice_text', 'votes', 'question',]
    # fieldsets = [
    #     ('Question',{'fields':['question_text']}),
    #     ('Date Information',{'fields':['pub_date']}),
    #     ]
    list_display = ('id','choice_text','votes','question',)
    list_filter = ['question']

# Register your models here.
admin.site.register(Post)
admin.site.register(Question,QuestionAdmin)
admin.site.register(Contact)
admin.site.register(Choice,ChoiceAdmin)
