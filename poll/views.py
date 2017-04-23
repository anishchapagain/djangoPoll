from django.shortcuts import render, get_list_or_404, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.views import generic
from django.db.models import Sum, Count, Avg
from django.core.mail import send_mail, BadHeaderError
from django.core.paginator import Paginator, EmptyPage, InvalidPage, PageNotAnInteger

from poll.forms import QuestionForm, ChoiceForm, ProfileForm,ContactForm, ChoiceDeleteForm
from poll.models import Question, Choice, Contact


# class IndexView(generic.ListView):
#     template_name = 'poll/index.html'
#     context_object_name = 'latest_question_list'
#
#     def get_queryset(self):
#         """Return the last five published questions."""
#         return Question.objects.order_by('pub_date')[:5]
#
# class DetailView(generic.DetailView):
#       model = Question
#        template_name = 'poll/detail.html'
#
# class ResultsView(generic.DetailView):
#         model = Question
#         template_name = 'poll/results.html'

def IndexView(request):
    template_name = 'poll/index.html'
    questions = Question.objects.order_by('pub_date')[:5]
    return render(request, template_name, {'questions': questions})


def detail(request, question_id):
    template_name = 'poll/detail.html'
    question = get_object_or_404(Question, id=question_id)
    choice = Choice.objects.all()
    sum_up = [c.votes for c in choice if c.question_id == int(question_id)]
    return render(request, template_name, {'question': question, 'question_total_votes': sum(sum_up)})


def results(request, question_id):
    template_name = 'poll/results.html'
    question = get_object_or_404(Question, id=question_id)
    return render(request, template_name, {'question': question})


def viewAllResults(request):
    question = Question.objects.all()
    choice = Choice.objects.all()
    score_total = {}
    for q in question:
        count = 0
        for c in choice:
            if c.question_id == q.id:
                count += c.votes
        score_total[q.id] = count
    print(score_total)
    total_votes = Choice.objects.all().aggregate(sumofvotes=Sum('votes'))
    page = request.GET.get('page', 1)
    paginator = Paginator(question, 2)
    try:
        question = paginator.page(page)
    except PageNotAnInteger:
        question = paginator.page(1)
    except EmptyPage:
        question = paginator.page(paginator.num_pages)
    return render(request, 'poll/viewall.html',
                  {'question': question, 'choice': choice, 'total_votes': total_votes, 'score_total': score_total})


def vote(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    try:
        selected_choice = question.choice_set.get(id=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'poll/detail.html', {
            'question': question, 'error_message': "No choices are provided. Please Contact Administrator",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        return HttpResponseRedirect(reverse('poll:results', args=(question.id,)))

def email(request):
    if request.method == 'GET':
        form = ContactForm()
    else:
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            emailAddress = form.cleaned_data['emailAddress']
            message = form.cleaned_data['message']
            try:
                print(subject, emailAddress,message)
                obj = Contact(subject=subject,emailAddress=emailAddress,message=message)
                obj.save()
                # send_mail(subject, message, contactemail, ['admin@example.com'])
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
    return render(request, "poll/contact.html", {'form': form})

def thanks(request):
    return HttpResponse('Thank you for your message.')

def add_poll(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            form.save()
            questions = Question.objects.order_by('pub_date')[:5]
            return render(request, 'poll/index.html', {'questions': questions})
        else:
            print(form.errors)
    else:
        form = QuestionForm()
    return render(request, 'poll/add_poll.html', {'form': form})

def add_choice(request, question_id):
    question = Question.objects.get(id=question_id)
    print(question)
    if request.method == 'POST':
        form = ChoiceForm(request.POST)
        if form.is_valid():#form.cleaned_data
            # print("FORM",form)
            # addOption = form.save()
            # print("\tOPTION",addOption)
            # addOption.question = question
            # addOption.votes = votes
            # addOption.save()
            form.save()
            return HttpResponseRedirect(reverse('poll:results', args=(question.id,)))
            # return render(request, 'poll/detail.html', {'questions': questions})
        else:
            print(form.errors)
    else:
        form = ChoiceForm()
    return render(request, 'poll/add_choice.html', {'form': form, 'question': question})

def profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'poll/profile.html', {'form': form})
        else:
            print(form.errors)
    else:
        form = ProfileForm()
    return render(request, 'poll/profile.html', {'form': form})

def delete_question(request, question_id):
    if request.method=='GET':
        Question.objects.get(id=question_id).delete()
        print("Question Deleted")
    return viewAllResults(request)

