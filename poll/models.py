import datetime
from django.db import models
from django.utils import timezone
from django.views.generic.list import ListView


# Create your models here.

class Question(models.Model):
    question_text = models.CharField('Question ', max_length=500, help_text="Enter your Question")
    # pub_date = models.DateTimeField(help_text='Date Published',auto_now_add=True,blank=True)
    pub_date = models.CharField(help_text='Date Published', max_length=200)

    def __str__(self):
        return self.question_text
    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

    was_published_recently.admin_order_field = 'pub_date'
    was_published_recently.boolean = True
    was_published_recently.short_description = 'Published recently?'


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, blank=True)
    choice_text = models.CharField('Poll Option', max_length=200, help_text="Enter Poll option for Choosen Question")
    votes = models.IntegerField(default=0, help_text="Enter Vote Count")

    def __str__(self):
        return self.choice_text


class Post(models.Model):
    author = models.ForeignKey('auth.User')
    title = models.CharField(max_length=200)
    text = models.TextField()
    created_date = models.DateTimeField(
        default=timezone.now)
    published_date = models.DateTimeField(
        blank=True, null=True)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.title


class Contact(models.Model):
    subject = models.CharField(max_length=200)
    message = models.TextField()
    emailAddress = models.EmailField()
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.subject
