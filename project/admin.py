from django.contrib import admin
from django.http import HttpResponse
from django.core import serializers

from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect

from .models import *
from django.http import HttpResponse
from django.core import serializers

from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect



class ProjectAdmin(admin.ModelAdmin):
    model = Project
    fk_name = "id"

@admin.register(Sheet)
class SheetAdmin(admin.ModelAdmin):
    pass

admin.site.register(Project,ProjectAdmin)



@admin.register(Employee)
class ContractorAdmin(admin.ModelAdmin):
    model = Employee
    fk_name = "id"
    fields = ( 'empname', 'sexcode', 'empid', 'jobtitle', 'deptcode', 'deptname', 'mobile', 'email','ismanager','managercode','ext','iscontract')
    list_display =( 'empname', 'empid', 'jobtitle', 'deptcode', 'deptname',  'email','ismanager','managercode','ext','iscontract')
  #  filter_vertical=('deptcode','sexcode')
    list_filter=('ismanager','iscontract')
    #list_max_show_all=200
    list_per_page=100
    ordering = ['-ismanager','empname']
    search_fields = ['empname', 'sexcode', 'empid', 'jobtitle', 'deptcode', 'deptname', 'mobile', 'email']
   # autocomplete_fields=['empname']  #autocomplete_fields is a list of ForeignKey and/or ManyToManyField fields
    show_full_result_count=True

	
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    model = Department
    fk_name = "id"
    fields = ( 'deptname', 'managerid', 'deptcode')
    list_display = ( 'deptname', 'managerid', 'deptcode')
    list_per_page=100
    ordering = ['-deptcode',]
    search_fields = ['deptname', 'managerid', 'deptcode']
    show_full_result_count=True