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
class AnswerList(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.answer_desc


class QuizForm(ModelForm):
<<<<<<< HEAD
    emp_answer_number = AnswerList(queryset=Answers.objects.filter(question_no = 1),to_field_name="answer_no",empty_label=None,required=False,widget=forms.RadioSelect(attrs={'class': ''} ))
=======
    answers = AnswerList(queryset=Answers.objects.filter(question_no = 1),to_field_name="answer_no",empty_label=None,required=False,widget=forms.RadioSelect(attrs={'class': 'option-input radio'} ))
>>>>>>> 2866a15893ba6c62137d698cb16d5fe998d7473d
    class Meta:
        model = EmployeeAnswer
        fields = ['question_no','emp_answer_number']
    widgets = {
    'question_no':TextInput(attrs={'class': 'form-control','placeholder':_('Project Name'),'required': True}),
    'emp_answer_number':forms.ModelChoiceField(queryset=Answers.objects.none(),widget=forms.RadioSelect)
    }

    def __init__(self, *args, **kwargs):
        super(QuizForm, self).__init__(*args, **kwargs)
        self.fields['emp_answer_number'].queryset = Answers.objects.filter(question_no = self.instance.question_no.question_no)
        if self.instance.is_submitted:
            self.fields['emp_answer_number'].widget.attrs['disabled'] = True
        # self.fields['answers'].widget = forms.RadioSelect()

# class QuizForm(ModelForm):
#     employee = AnswerList(queryset=Answers.objects.all(),to_field_name="answer_no",empty_label=_("Select Answer"),required=False,widget=forms.Select(attrs={'class': 'chosen form-control'} ))
#     class Meta:
#         model = Questions
#         fields = ['question_desc','question_no']
#         widgets = {
#             'question_desc':TextInput(attrs={'class': 'form-control','required': True}),
#             'question_no': Textarea(attrs={'id':'summernote','class':'form-control','required': True}),
#         }

    # def clean(self):
    #     cleaned_data = super().clean()
    #     enddate = cleaned_data.get("enddate")
    #     startdate = cleaned_data.get("startdate")
    #     #Check end date less than start date
    #     if enddate < startdate:
    #         msg = _("End date is less than start date")
    #         self.add_error('enddate', msg)

class EmpDataForm(forms.Form):

    fullname = forms.CharField(max_length=254,widget=forms.TextInput(attrs={'class': "form-control form-group",'placeholder':"الإسم الكامل"}),)
    dept = forms.CharField(max_length=254,widget=forms.TextInput(attrs={'class': "form-control",'placeholder':"الإدارة"}),)
    email = forms.CharField(max_length=254,widget=forms.TextInput(attrs={'class': "form-control",'placeholder':"البريد الإلكتروني"}),)
    mobile = forms.CharField(max_length=254,widget=forms.TextInput(attrs={'class': "form-control",'placeholder':"الجوال"}),)
