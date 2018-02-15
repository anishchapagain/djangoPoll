from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.core.mail import BadHeaderError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Sum
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from poll.fusioncharts import FusionCharts  # HighCharts D3
#from fusioncharts import FusionCharts  # HighCharts D3
#from highcharts import Highchart
from poll.forms import QuestionForm, ChoiceForm, ContactForm
from poll.forms import SignUpForm, FilterResults
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

class ChartData(object):
    @classmethod
    def check_valve_data(cls):
        data = {'choice text': [], 'votes': []}
        valves = Choice.objects.all().filter(votes__gte=10).order_by('choice_text')
        for unit in valves:
            data['choice text'].append(unit.choice_text)
            data['votes'].append(unit.votes)
        return data


def IndexView(request):
    template_name = 'poll/index.html'
    questions = Question.objects.order_by('pub_date')
    form = FilterResults()
    answer = ''
    if request.method == 'POST':
        # form = FilterResults(request.POST)
        # if form.is_valid():
        # status = form.cleaned_data['status']
        # status = request.POST['status']
        print(request.POST)
        status = request.POST.get('status')
        if status == '10':
            choices_filtering = Choice.objects.all().filter(votes__gte=10).filter(votes__lt=20).order_by('choice_text')
        elif status == '20':
            choices_filtering = Choice.objects.all().filter(votes__gte=20).order_by('choice_text')
        elif status == '5':
            choices_filtering = Choice.objects.all().filter(votes__lte=5).order_by('choice_text')
        else:
            status = '0'
            choices_filtering = Choice.objects.all().filter(votes__lte=0).order_by('choice_text')

        dataPlot = choices_filtering  # Choice.objects.all().filter(votes__gte=10).order_by('choice_text')
        columnChart = chart(dataPlot, plotType="column3d", subCaption=status)  # pie3d column2d
        return render(request, template_name,
                            {'title': 'T20 Index Page', 'head': 'T20 Index Head', 'questions': questions, 'form': form,
                             'output': columnChart.render()})

    else:
        form = FilterResults()
        return render(request, template_name,
                      {'title': 'T20 Index Page', 'head': 'T20 Index Head', 'questions': questions, 'form': form})


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
    paginator = Paginator(question, 5)
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
        # question referencing choices set foreign key values
        selected_choice = question.choice_set.get(id=request.POST['choice'])
        print("Choice ", selected_choice.question_id)
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'poll/detail.html', {
            'question': question, 'error_message': "Please Select or Create Choice first, Please Contact Administrator",
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
                print(subject, emailAddress, message)
                obj = Contact(subject=subject, emailAddress=emailAddress, message=message)
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
        if form.is_valid():  # form.cleaned_data
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


def profile(request, username):
    user = User.objects.get(username=username)
    return render(request, "poll/profile.html", {'user': user})


#     if request.method == 'POST':
#         form = ProfileForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return render(request, 'poll/profile.html', {'form': form})
#         else:
#             print(form.errors)
#     else:
#         form = ProfileForm()
#     return render(request, 'poll/profile.html', {'form': form})

def delete_question(request, question_id):
    if request.method == 'GET':
        Question.objects.get(id=question_id).delete()
        print("Question Deleted")
    return viewAllResults(request)


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'poll/signup.html', {'form': form})


    # Create an object for the Area 2D chart using the FusionCharts class constructor
    # http://www.fusioncharts.com/dev/chart-attributes.html?chart=column2d&attributeName=chart_theme


def chart(dataPlot, plotType, subCaption):
    """Data source """
    chartType = plotType  # "column2d"#pie3d
    chartID = "chart-1"  # chart ID unique for Page
    chartHeight = "100%"  # chart Height
    chartWidth = "100%"  # chart Width
    chartDataFormat = "json"  # json xml
    dataSource = {}
    dataSource['chart'] = {}
    dataSource['chart']['caption'] = "World T20 Cricket POLL"
    dataSource['chart']['subCaption'] = "Votes (" + subCaption + ")"
    dataSource['chart']['xAxisName'] = "Questions"
    dataSource['chart']['yAxisName'] = "Votes Count"
    dataSource['chart']['numberPrefix'] = ""
    dataSource['chart']['startingangle'] = "120"  # pie3d
    dataSource['chart']['slicingdistance'] = "10"  # pie3d
    dataSource['chart']['rotatevalues'] = "1"
    dataSource['chart']['plotToolText'] = "<div><b>$label</b><br/>Votes : <b>$value</b></div>"
    dataSource['chart']['theme'] = "zune"  # ‘carbon’, ‘fint’, ‘ocean’, ‘zune’
    dataSource['chart']['animation'] = "1"  
    dataSource['chart']['animationDuration'] = "1" 
    dataSource['chart']['exportEnabled'] = "1"
    dataSource['chart']['use3DLighting'] = "1"
    dataSource['chart']['maxZoomLimit'] = 100
    dataSource['chart']['labelDisplay'] = "Wrap"
    dataSource['chart']['placeValuesInside'] = "1"
    dataSource['chart']['legendPosition']='RIGHT'
    dataSource['chart']['plotGradientColor']='black'
    dataSource['chart']['slantLabels']='1'


    dataSource['data'] = []
    for item in dataPlot:
        q = get_object_or_404(Question, id=item.question_id)
        data = {}
        data['label'] = item.choice_text + "\n (" + q.question_text + ")"
        data['value'] = item.votes
        dataSource['data'].append(data)
    columnChart = FusionCharts(chartType, "ex2", chartHeight, chartWidth, chartID, chartDataFormat, dataSource)
    return columnChart


def plot(request, chartID='chart_ID', chart_type='line', chart_height=500):
    data = ChartData.check_valve_data()
    # print(data)

    chart = {"renderTo": chartID, "type": chart_type, "height": chart_height, "width": chart_height}
    title = {"text": 'Votes Results'}
    xAxis = {"title": {"text": 'Votes'}}
    yAxis = {"title": {"text": 'Data'}}
    series = [
        {"name": 'Votes', "data": data['votes']},
        {"name": 'Choice Options', "data": data['choice text']}
    ]

    return render(request, 'poll/index.html', {'chartID': chartID, 'chart': chart,
                                               'series': series, 'title': title,
                                               'xAxis': xAxis, 'yAxis': yAxis})


def home(request):
    template_name = 'poll/index.html'
    form = FilterResults()
    questions = Question.objects.order_by('pub_date')
    if request.method == 'POST':
        # form = FilterResults(request.POST)
        status = request.POST['filter_option']
        form = FilterResults(request.POST)
        # print("in home ", status)
        if status == "10":
            choices_filtering = Choice.objects.all().filter(votes__gte=10).order_by('choice_text')
        elif status == "20":
            choices_filtering = Choice.objects.all().filter(votes__gte=20).order_by('choice_text')
        elif status == "5":
            choices_filtering = Choice.objects.all().filter(votes__lte=5).order_by('choice_text')
        else:
            status = "0"
            choices_filtering = Choice.objects.all().filter(votes__lte=0).order_by('choice_text')

        dataPlot = choices_filtering  # Choice.objects.all().filter(votes__gte=10).order_by('choice_text')
        columnChart = chart(dataPlot, plotType="column2d", subCaption=status)  # pie3d column2d

        return render(request, template_name,
                      {'title': 'T20 Index Page', 'head': 'T20 Index Head', 'questions': questions,
                       'form': form, 'output': columnChart.render()})
