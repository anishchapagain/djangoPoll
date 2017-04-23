from django import forms
from poll.models import Question, Choice, Contact
from datetime import datetime
from django.utils import timezone

# POLL FORMS #
class QuestionForm(forms.ModelForm):
    # question_text = forms.CharField(max_length=200, help_text="Please enter the question.")
    #pub_date = forms.DateTimeField(help_text="Please enter Date.",initial = timezone.now)
    class Meta:
        model = Question
        # fields = "__all__"
        fields = ('question_text',)

class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ('choice_text','votes','question',)


# BIRTH_YEAR_CHOICES = ('1980', '1981', '1982','1983','1984', '1985', '1986','1987')
class ProfileForm(forms.Form):
    firstname = forms.CharField(help_text='Player FirstName',max_length=200,required=True)
    lastname = forms.CharField(help_text='Player LastName',max_length=200,required=True)
    middlename = forms.CharField(help_text='Player MiddleName',max_length=50,required=False)
    # dob = forms.DateField(help_text='Date Of Birth',widget=forms.SelectDateWidget(years=BIRTH_YEAR_CHOICES))
    dob = forms.DateField(help_text='Date Of Birth',required=False)
    photo = forms.ImageField(help_text='Player Photo',required=False)
    country = forms.CharField(help_text='Player Country',required=True)

    class Meta:
        fields = ('__all__',)

class ContactForm(forms.Form):
    subject = forms.CharField(help_text='Subject',required=True)
    emailAddress = forms.EmailField(help_text='Email Address')
    message = forms.CharField(required=False,widget=forms.Textarea,help_text='Message')
    class Meta:
        model = Contact
        fields = ('__all__',)

class ChoiceDeleteForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = "__all__"