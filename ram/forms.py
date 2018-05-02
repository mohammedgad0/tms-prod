from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _
import datetime
from django.forms import modelformset_factory
from .models import *
from django.forms import ModelForm, Textarea,TextInput,DateField
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.forms import ModelChoiceField

class AnswerList(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.answer_desc



class QuizForm(ModelForm):
    # answers = AnswerList(queryset=Answers.objects.all(),to_field_name="answer_no",empty_label=_("Select Answer"),required=False,widget=forms.Select(attrs={'class': 'chosen form-control'} ))
    class Meta:
        model = EmployeeAnswer
        fields = ['question_no','emp_answer_number',]
    widgets = {
    'question_no':TextInput(attrs={'class': 'form-control','placeholder':_('Project Name'),'required': True}),
    'emp_answer_number':forms.Select(attrs={'class': 'form-control','placeholder':_('Select answer')}),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['emp_answer_number'].queryset = Answers.objects.none()




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
