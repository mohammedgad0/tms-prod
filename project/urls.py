from django.conf.urls import url ,include
from project import views
# from project.views import ProjectMembersListView
#application namespace
app_name = 'ns-project'

urlpatterns = [
    # Matches any html file - to be used for gentella
    # Avoid using your .html in your resources.
    # Or create a separate django app.

    # The home page
    url(r'^$', views.index, name='index'),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^add-sheet/$', views.AddSheet, name='add-sheet'),
    url(r'^sheet/(?P<pk>\d+)/edit/$', views.EditSheet, name='edit-sheet'),
    url(r'^sheet/(?P<pk>\d+)/submit/$', views.SubmitSheet, name='submit-sheet'),
    url(r'^sheet/(?P<pk>\d+)/change/$', views.ChangeStatus, name='change-status'),
    url(r'^my_sheet/$', views.MySheet, name='my-sheet'),
    # url(r'^all_sheets/$', views.ManagerPage, name='all-sheets'),
    url(r'^all_employees_sheets/$', views.AllSheets, name='emps-sheets'),
    url(r'^all_dept_sheet/$', views.AllDept, name='dept-sheets'),
    url(r'^all_dept_sheets/$', views.AllDepts, name='department-sheets'),
    url(r'^dept_no_sheets/$', views.DeptsnoSheets, name='department-nosheets'),
    #url(r'^all_emp/$', views.IsManager, name='all-emp'),
    url(r'^sheet/(?P<deptcode>\d+)/dept/$', views.DeptSheet, name='dept-sheet'),
    # Employees does'nt have task
    url(r'^emp_notsheet/$', views.EmployeeNoSheet, name='emp-no-sheets'),
    url(r'^emp_notfinished/$', views.EmpnotFinished, name='emp-not-finished'),
    # url(r'^sheet/(?P<empid>\d+)/update/$', views.EditSheet, name='edit-sheet'),
    url(r'^sheet/(?P<empid>\d+)/update/$', views.UpdateSheet, name='update-sheet'),
    url(r'^sheet/(?P<empid>\d+)/details/$', views.DetailseSheet, name='detials-sheet'),
    url(r'^sheet/(?P<empid>\d+)/show/$', views.EmpSheet, name='emp-sheet'),
    url(r'^add_project/$', views.AddProject, name='add-project'),
    url(r'^project_list/$', views.ProjectList, name='project-list'),
    url(r'^project_detail/(?P<pk>\d+)$', views.ProjectDetail, name='project-detail'),
    url(r'^project_edit/(?P<pk>\d+)$', views.ProjectEdit, name='project-edit'),
    url(r'^project_delete/(?P<pk>\d+)$', views.ProjectDelete, name='project-delete'),
    url(r'^project_task/(?P<pk>\d+)$', views.ProjectTask, name='project-task'),
    url(r'^project_task_detail/(?P<pk>\d+)$', views.ProjectTaskDetail, name='project-task-detail'),
    url(r'^project_team/(?P<pk>\d+)$', views.ProjectTeam, name='project-team'),
    url(r'^task_update_start/(?P<pk>\d+)$', views.updateStartDate, name='task-update-start'),
    url(r'^update_finish_task/(?P<pk>\d+)$',views.updateTaskFinish, name='update-finish-task'),
    url(r'^update_close_task/(?P<pk>\d+)$',views.updateTaskClose, name='update-close-task'),
    # url(r'^ProjectMember/$', ProjectMembersListView.as_view(), name='ProjectMember-list'),
    url(r'^.*\.html', views.gentella_html, name='gentella'),
    url(r'^auth/(?P<email>.*)/(?P<signature>.*)/(?P<time>.*)/$', views.loginfromdrupal, name='loginfromdrupal'),
    # Delegations
    url(r'^add_delegation/$',views.adddelegation, name='add-delegation'),
    url(r'^delegation/(?P<pk>\d+)/edit/$', views.editdelegation, name='edit-delegation'),
    url(r'^delegation/$',views.delegation, name='delegation'),
    url(r'^my_delegation/$',views.mydelegation, name='my-delegation'),
    # End Delegations

    url(r'^export/xls/$', views.export_users_xls, name='export_users_xls'),
    url(r'^export/xls/empnosheet$', views.export_empnosheet_xls, name='export_empnosheet_xls'),
    url(r'^export/xls/depts$', views.export_department_xls, name='export_departmen_xls'),
    url(r'^export/xls/deptsnosheet$', views.export_departmentnosheet_xls, name='export_departmennosheet_xls'),

]
