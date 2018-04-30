from django.conf.urls import url ,include
from ram import views
# from project.views import ProjectMembersListView
#application namespace
app_name = 'ramadan'

urlpatterns = [
    # Matches any html file - to be used for gentella
    # Avoid using your .html in your resources.
    # Or create a separate django app.
    # The home page
    url(r'^$', views.index, name='index'),
    url(r'^i18n/', include('django.conf.urls.i18n')),

]
