from django.shortcuts import render
from .models import *
from .forms import *

# Create your views here.

def index(request):
    context = {}
    return render(request, 'ram/home.html', context)

def quiz(request):
    Quiz = QuizForm()
    quiz = {}
    array = []
    array1 = []
    answer = Answers.objects.all()
    for data in answer:
        quiz[data.question_no] = {data.answer_no:data.answer_desc}
    for p_id, p_info in quiz.items():
        print("\nQuestion ID:", p_id)

    for key in p_info:
        print(str(key) + ':', p_info[key])

    context = {'answer':answer, 'quiz':quiz}
    return render(request, 'ram/quiz.html', context)
