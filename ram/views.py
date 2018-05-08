from django.shortcuts import render, render_to_response ,get_object_or_404,redirect
from .models import *
from .forms import *
from project.models import Employee
from django.db.models import Q
from datetime import timedelta
from django.http import HttpResponse ,HttpResponseRedirect,Http404 ,HttpResponseForbidden
from django.core.urlresolvers import reverse

# Create your views here.


def get_period(date):
    try:
        period = PeriodQuestion.objects.get(date_from__lte = date , date_to__gte = date)
        return period.period_no
    except:
        period = 5
    return period

def index(request):
    print (request.session.get('EmpID'))
    # employee = Employee.objects.get(empid = request.session.get('empid'))
    employee =  get_object_or_404(Employee, empid = request.session.get('EmpID'))
    question = get_object_or_404(Questions, question_no = 1)
    all_emp_question_list = set()
    all_emp_question = EmployeeAnswer.objects.filter(emp_id = request.session.get('EmpID'))
    date = datetime.datetime.now()
    # date = date + timedelta(days=10)
    period = get_period(date)
    for item in all_emp_question:
        all_emp_question_list.add(item.question_no.question_no)
    questions = Questions.objects.filter(
    Q(period_no = period)&
    ~Q(question_no__in= all_emp_question_list))
    for item in questions:
        q_no = Questions.objects.get(question_no= item.question_no)
        EmployeeAnswer.objects.create(emp_id=employee, question_no= q_no)

    print ("period is ", period)
    print(all_emp_question_list)
    # question = Questions.objects.filter(question_no = 1)
    # EmployeeAnswer.objects.create(emp_id=employee, question_no= question)
    form = QuizForm
    context = {'form':form}
    return render(request, 'ram/home.html', context)

# def quiz(request):
#     # quiz = EmployeeAnswer.objects.filter(emp_id = request.session.get('EmpID'))
#     # ans = {}
#     # for data in quiz:
#     #     answer = Answers.objects.filter(question_no = data.question_no.question_no)
#     #     ans[data.question_no.question_no]  = answer
#     # print (ans)
#
#     question = Questions.objects.all()
#     for q in question:
#         answer = q.choices.all()
#         print("this is question" , q.question_no)
#         for data in answer:
#             print(data.answer_no)
#     # print(question.choices.all())
#
#     context = {'answer':answer,'question':question}
#     return render(request, 'ram/quiz.html', context)

def quiz(request):
    date = datetime.datetime.now()
    # date = date + timedelta(days=10)
    period = get_period(date)
    query = EmployeeAnswer.objects.filter(
    Q(emp_id = request.session.get('EmpID'))&
    Q(question_no__period_no = period)
    )

    quiz_emp = modelformset_factory(EmployeeAnswer, form=QuizForm, extra=0)
    formset = quiz_emp(queryset=query)
    if request.method == 'POST':
        print('this is post')
        formset = quiz_emp(request.POST)
        if formset.is_valid():
            print("form valid")
            if 'save' in request.POST:
                instances = formset.save(commit=False)
                for obj in instances:
                    obj.is_save = True
                    print(obj.emp_answer_number)
                    obj.save()
            elif '_submit':
                instances = formset.save(commit=False)
                for obj in instances:
                    print(obj.emp_answer_number)

                    obj.is_submitted = 1
                for form in formset:
                    instances = form.instance
                    print(instances.emp_answer_number)
                    instances.is_submitted = 1
                    instances.save()
        return HttpResponseRedirect(reverse('ramadan:quiz'))
    else:
        formset = formset
    context = {'form':formset}
    return render(request, 'ram/quiz.html', context)

def levels(request):
    # period_1

    # period_2

    # period_3
    emp = request.session.get('EmpID')
    is_agree = Conditions.objects.filter(emp_id=emp)
    if len(is_agree) == 0:
        print(len(is_agree))
        return HttpResponseRedirect(reverse('ramadan:conditions'))

    context = {}
    return render(request, 'ram/levels.html', context)

def EmployeeData(request):
    form = EmpDataForm(request.POST)

    if form.is_valid():
        return redirect('/ram/levels')
    context = {"form":form}
    return render(request, 'ram/EmployeeData.html', context)


def conditions(request):
    emp = request.session.get('EmpID')
    is_agree = Conditions.objects.filter(emp_id=emp)
    if len(is_agree) != 0:
        print(len(is_agree))
        return HttpResponseRedirect(reverse('ramadan:employee-data'))

    if request.method == "POST":
        emp_id = request.session.get('EmpID')
        employee = Employee.objects.get(empid=emp_id)
        Conditions.objects.create(emp_id=employee, is_agree= 1)
        return HttpResponseRedirect(reverse('ramadan:levels'))
    context = {}
    return render(request,'ram/conditions.html',context)
