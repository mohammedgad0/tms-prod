from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _
import datetime
from django.forms import modelformset_factory
from .models import *
from django.forms import ModelForm, Textarea,TextInput,DateField
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.forms import ModelChoiceField
from django.db.models import Count, Case, When, IntegerField ,F
from ram.views import *


def get_period(date):
    try:
        period = PeriodQuestion.objects.get(date_from__lte = date , date_to__gte = date)
        return period.period_no
    except:
        period = 5
    return period

class AnswerList(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.answer_desc


class QuizForm(ModelForm):
    emp_answer_number = ModelChoiceField(
        widget=forms.RadioSelect(attrs={'class': 'option-input radio'}),
        queryset=None,
        empty_label=None,
        to_field_name='answer_no',
        label = 'Please select',
        required = False

        )
    # emp_answer_number = (queryset=None,)forms.RadioSelect(attrs={'class': 'option-input radio'} )
    class Meta:
        model = EmployeeAnswer
        fields = ['question_no','emp_answer_number']

    def __init__(self, *args, **kwargs):
        super(QuizForm, self).__init__(*args, **kwargs)
        answers_list = Answers.objects.filter(question_no = self.instance.question_no.question_no)
        self.fields['emp_answer_number'].queryset = answers_list
        date = datetime.datetime.now()
        period = get_period(date)
        self.fields['question_no'].queryset =  Questions.objects.filter(period_no = period)
        self.fields['emp_answer_number'].choices = [(q.answer_no, q.answer_desc) for q in answers_list]
        # self.fields['question_no']=forms.CharField(max_length=100)
        self.fields['question_no'].widget.attrs['hidden'] = True
        if self.instance.is_submitted:
            self.fields['emp_answer_number'].widget.attrs['disabled'] = True

class EmpDataForm(forms.Form):
    fullname = forms.CharField(max_length=254,widget=forms.TextInput(attrs={'class': "form-control form-group",'placeholder':"الإسم الكامل"}),)
    dept = forms.CharField(max_length=254,widget=forms.TextInput(attrs={'class': "form-control",'placeholder':"الإدارة"}),)
    email = forms.CharField(max_length=254,widget=forms.TextInput(attrs={'class': "form-control",'placeholder':"البريد الإلكتروني"}),)
    mobile = forms.CharField(max_length=254,widget=forms.TextInput(attrs={'class': "form-control",'placeholder':"الجوال"}),)

class conditions(forms.Form):
    agree = forms.BooleanField()
