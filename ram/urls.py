from django.conf.urls import url ,include
from ram import views
from project.views import loginfromdrupal
from project.forms import BootstrapAuthenticationForm
from datetime import datetime
# from project.views import ProjectMembersListView
#application namespace
app_name = 'ramadan'

urlpatterns = [
    # Matches any html file - to be used for gentella
    # Avoid using your .html in your resources.
    # Or create a separate django app.
    # The home page
    url(r'^$', views.index, name='index'),
    url(r'^quiz/$', views.quiz, name='quiz'),
    url(r'^levels/$', views.levels, name='levels'),
    url(r'^employee-data/$', views.EmployeeDataView, name='employee-data'),
    url(r'^conditions/$', views.conditions, name='conditions'),
    url(r'^auth/(?P<email>.*)/(?P<signature>.*)/(?P<time>.*)/$', loginfromdrupal, name='loginfromdrupal'),
    url(r'^accounts/login/$',
        views.myuser,
        {
            'template_name': 'ram/login.html',
            'authentication_form': BootstrapAuthenticationForm,
            'extra_context':
            {
                'title': 'Log in',
                'year': datetime.now().year,
            }
        },
        name='login'),
    url(r'^i18n/', include('django.conf.urls.i18n')),

]
