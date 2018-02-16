from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.core.mail import BadHeaderError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Sum, Q
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.core import serializers
from poll.fusioncharts import FusionCharts
from poll.forms import QuestionForm, ChoiceForm, ContactForm, ProfileForm
from poll.forms import SignUpForm, FilterResults, AJAXFilterResults
from poll.models import Question, Choice, Contact
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage


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


def get_queryset(query):
    if query:
        print("Searching :", query)
        query_list = query.split()
        results={}
        count=0
        for q in query_list:
            try:
                # val = list(Choice.objects.filter(choice_text__icontains=q))
                val1 = list(Question.objects.filter(question_text__contains=q))#.filter(question_text__icontains=q).filter(question_text__exact=q))
                # val2 = list(Choice.objects.filter(question__choice__votes__exact=int(q)))
                if len(val1)>0:
                    results[count]= val1
                    count+= 1
                # if len(val1)>0:
                #     results[count]= val1
                #     count+= 1
                # if len(val2)>0:
                #     results[count]= val2
                #     count+= 1
            except ValueError:
                print('')
        finalresults = list(results.values())
        return finalresults


def IndexView(request):
    template_name = 'poll/index.html'
    questions = Question.objects.order_by('-pub_date')
    choice = Choice.objects.all()

    test=[12,23,45,67,89]


    query = request.GET.get('q')
    result=[]
    if query:
        result = get_queryset(query)
        if len(result) == 0:
            result.append('')
    else:
        result.append('')

    total_votes = {}
    for q in questions:
        total = 0
        id = q.id
        for c in choice:
            if c.question_id == id:
                total += c.votes
            total_votes[id] = total
    print(total_votes)

    # form = FilterResults()
    if request.method == 'POST':
        form = FilterResults(request.POST)
        if form.is_valid():
            # status = form.cleaned_data['status']
            # status = request.POST['status']
            status = request.POST.get('status')
            if status == '10':
                choices_filtering = Choice.objects.all().filter(votes__gte=10).filter(votes__lt=20).order_by(
                    'choice_text')  # multiple condition
            elif status == '20':
                choices_filtering = Choice.objects.all().filter(votes__gte=20).order_by(
                    'choice_text')  # single condition
            elif status == '5':
                choices_filtering = Choice.objects.all().filter(votes__lte=5).order_by('choice_text')
            else:
                status = '0'  # As Default : show all
                choices_filtering = Choice.objects.all().filter(votes__gte=0).order_by('choice_text')

            dataPlot = choices_filtering  # results Queryset after Filtering
            # Queryset: Choice.objects.all().filter(votes__gte=10).order_by('choice_text')
            columnChart = chart(dataPlot, plotType="column2d", subCaption=status)  # pie3d column2d
            return render(request, template_name,
                          {'title': 'T20 Index Page', 'head': 'T20 Index Head',
                           'questions': questions,
                           'form': form,
                           'total': total_votes,
                           'output': columnChart.render(),
                           'count': calculate(),
                           'searchResult':result[0]})
            # count()/sum/max/min/avg

    else:
        form = FilterResults()
        return render(request, template_name,
                      {'title': 'T20 Index Page',
                       'head': 'T20 Index Head',
                       'questions': questions,
                       'form': form,
                       'total': total_votes,
                       'count': calculate(),
                       'searchResult':result[0],'test':test})


@login_required
# @login_required(login_url='/poll/login/')
def detail(request, question_id):
    template_name = 'poll/detail.html'
    question = get_object_or_404(Question, id=question_id)
    choice = Choice.objects.all()
    sum_up = [c.votes for c in choice if c.question_id == int(question_id)]
    return render(request, template_name,
                  {'question': question,
                   'question_total_votes': sum(sum_up),
                   'count': calculate()})


def results(request, question_id):
    template_name = 'poll/results.html'
    question = get_object_or_404(Question, id=question_id)
    return render(request, template_name, {'question': question, 'count': calculate()})


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
                  {'question': question,
                   'choice': choice,
                   'total_votes': total_votes,
                   'score_total': score_total, 'count': calculate()})


def vote(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    try:
        # question referencing choices set foreign key values
        selected_choice = question.choice_set.get(id=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'poll/detail.html', {
            'question': question,
            'error_message': "Please Select or Create Choice first, Please Contact Administrator",
            'count': calculate()
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
    return render(request, "poll/contact.html", {'form': form, 'count': calculate()})


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
    return render(request, 'poll/add_poll.html', {'form': form, 'count': calculate()})


def add_choice(request, question_id):
    question = Question.objects.get(id=question_id)
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
    return render(request, 'poll/add_choice.html', {'form': form, 'question': question, 'count': calculate()})


# @login_required
def profile(request, username):
    user = User.objects.values().get(username=username)
    # user = User.objects.values()
    # return render(request, "poll/profile.html", {'user': user, 'form': form, 'count': calculate()})
    form = ProfileForm(request.POST)
    if request.method == 'POST':
        if request.FILES['photo']:
            myfile = request.FILES['photo']
            fs = FileSystemStorage()
            filename = fs.save(myfile.name,myfile)
            uploaded_file = fs.url(filename)
            print(uploaded_file)
            return render(request,'poll/simple_upload.html',{'uploaded_file':uploaded_file,'user': user, 'form': form, 'count': calculate()})
    else:
        return render(request, 'poll/profile.html', {'user': user,'form':form,'count': calculate()})

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
            return redirect('index')
    else:
        form = SignUpForm()
    return render(request, 'poll/signup.html', {'form': form, 'count': calculate()})


def chart(dataPlot, plotType, subCaption):
    """Data source """
    chartType = plotType  # "column2d"#pie3d
    chartID = "chart-1"  # chart ID unique for Page
    chartHeight = "800"  # chart Height
    chartWidth = "800"  # chart Width
    renderer = "JavaScript"  # optional
    # chartDataFormat = "json"  # json xml
    chartDataFormat = "json"  # json xml
    dataSource = {}
    dataSource['chart'] = {}
    dataSource['chart']['caption'] = "World T20 Cricket POLL"
    dataSource['chart']['subCaption'] = "Votes (" + subCaption + ")"
    dataSource['chart']['xAsixName'] = ""
    dataSource['chart']['yAsixName'] = ""
    dataSource['chart']['numberPrefix'] = ""
    dataSource['chart']['startingangle'] = "120"  # pie3d
    dataSource['chart']['slicingdistance'] = "10"  # pie3d
    dataSource['chart']['rotatevalues'] = "1"
    dataSource['chart']['plotToolText'] = "<div><b>$label</b><br/>Votes : <b>$value</b></div>"
    dataSource['chart']['theme'] = "fint"  # ‘carbon’, ‘fint’, ‘ocean’, ‘zune’
    dataSource['chart']['animation'] = "1"  # ‘carbon’, ‘fint’, ‘ocean’, ‘zune’
    dataSource['chart']['animationDuration'] = "1"  # ‘carbon’, ‘fint’, ‘ocean’, ‘zune’
    dataSource['chart']['exportEnabled'] = "1"
    # dataSource['chart']['maxZoomLimit'] = 1000
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


#Task: Plan with HighCharts
def pollFilter(request):
    """
    Try URL :
    http://127.0.0.1:8000/poll/filter/?status=10 ,
    http://127.0.0.1:8000/poll/filter/?status=20&type=pie2d
    for each status value below
    """
    template_name = 'poll/filterAjax.html'
    questions = Question.objects.order_by('pub_date')

    status = request.GET.get('status')
    charttype = request.GET.get('type')
    if charttype is None:
        charttype = 'column2d'
    if status == "10":
        choices_filtering = Choice.objects.all().filter(votes__gte=10).order_by('choice_text')
    elif status == "20":
        # choices_filtering = Choice.objects.all().filter(votes__gte=20).order_by('choice_text')
        choices_filtering = Choice.objects.filter(Q(votes__gte=20)).order_by('choice_text')
    elif status == "5":
        choices_filtering = Choice.objects.all().filter(votes__lte=5).order_by('choice_text')
    else:
        status = "0"
        choices_filtering = Choice.objects.all().filter(votes__gte=0).order_by('choice_text')

    dataPlot = choices_filtering
    columnChart = chart(dataPlot, plotType=charttype, subCaption=status)  # pie3d column2d
    return render(request, template_name,
                  {'title': 'T20 Filter Page',
                   'head': 'T20 Filter Head',
                   'questions': questions,
                   'output': columnChart.render(), 'count': calculate()})


def testing(request, param1):
    total = int(param1) + 20
    val1 = "Method : ", request.method, "<br> Content Params ", request.content_params, "<br> Content Type ", request.content_type, "<br> Encoding ", request.encoding,
    val2 = "<br>  Path Info ", request.path_info, "<br> Path ", request.path, " <br> Session ", request.session, " <br> cookies ", request.COOKIES
    val3 = "<br><br> META ", request.META
    val4 = "<br><br> Read ", request.read, " <br> Read Line ", request.readlines()
    val = val1, " <br>", val2, "<br>", val3, "<br>", val4, "<br> sum is %d " % total
    return HttpResponse(val)


def calculate():
    question = Question.objects.count()
    choice = Choice.objects.count()
    totalVotes = [c.votes for c in Choice.objects.all()]
    return {'questionCount': question, 'choiceCount': choice, 'totalVotes': sum(totalVotes)}