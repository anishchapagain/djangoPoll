from django.contrib import admin
from .models import *


# class QuestionInLine(admin.StackedInline):
#     model = Question


# class QuestionAdmin(admin.ModelAdmin):
#     inlines = [QuestionInLine]

# Register your models here.
admin.site.register(Post)
admin.site.register(Question)
admin.site.register(Contact)
admin.site.register(Choice)
