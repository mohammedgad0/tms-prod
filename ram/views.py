from django.shortcuts import render, render_to_response ,get_object_or_404,redirect
from .models import *
from .forms import *
from project.models import Employee

# Create your views here.


def index(request):
    print (request.session.get('EmpID'))
    # employee = Employee.objects.get(empid = request.session.get('empid'))
    employee =  get_object_or_404(Employee, empid = request.session.get('EmpID'))
    question = get_object_or_404(Questions, question_no = 1)
    # question = Questions.objects.filter(question_no = 1)
    EmployeeAnswer.objects.create(emp_id=employee, question_no= question)
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
    query = EmployeeAnswer.objects.filter(emp_id = '1056821208')
    quiz_emp = modelformset_factory(EmployeeAnswer, form=QuizForm, extra=0)
    formset = quiz_emp(request.POST or None,queryset=query)
    # form = QuizForm()
    context = {'form':formset}
    return render(request, 'ram/quiz.html', context)
