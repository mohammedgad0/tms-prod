from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from django.db import models
from project.models import Employee
# Create your models here.

class Questions(models.Model):
    question_no = models.AutoField(db_column='QUESTION_NO',primary_key=True)
    question_desc = models.CharField(db_column='QUESTION_DESC', max_length=400)
    correct_answer_no = models.IntegerField(db_column='CORRECT_ANSWER_NO')
    period_no = models.ForeignKey('PeriodQuestion', to_field= 'period_no' ,db_column='PERIOD_NO')

    def __str__(self):
        return self.question_desc

    class Meta:
        managed = True
        db_table = 'RAM_QUESTIONS'

class Answers(models.Model):
    question_no = models.ForeignKey('Questions',to_field='question_no', db_column='QUESTION_NO',related_name="choices")
    answer_no = models.CharField(db_column='ANSWER_NO',max_length=10)
    answer_desc = models.CharField(db_column='ANSWER_DESC', max_length= 255)
    def __str__(self):
        return self.answer_no

    class Meta:
        managed = True
        db_table = 'RAM_ANSWERS'

class EmployeeAnswer(models.Model):
    emp_id = models.ForeignKey('project.Employee' , to_field = 'empid' , db_column='EMP_ID',null=True,blank=True)
    question_no = models.ForeignKey('Questions',to_field='question_no', db_column='QUESTION_NO',null=True,blank=True)
    emp_answer_number = models.CharField(db_column='EMP_ANSWER_NUMBER',blank=True, null=True,max_length=50)
    is_save = models.NullBooleanField(db_column='IS_SAVE',blank=True,)
    is_submitted = models.NullBooleanField(db_column='IS_SUBMITTED',blank=True)

    class Meta:
        managed = True
        db_table = 'RAM_EMP_ANSWER'

class PeriodQuestion(models.Model):
    period_no = models.AutoField(db_column='PERIOD_NO',primary_key=True)
    date_from = models.DateField(db_column='DATE_FROM')
    date_to = models.DateField(db_column='DATE_TO')
    descreption = models.CharField(db_column='DESCREPTION', max_length=255)

    class Meta:
        managed = True
        db_table = 'RAM_PERIOD'
