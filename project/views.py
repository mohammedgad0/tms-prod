from django.shortcuts import render, render_to_response ,get_object_or_404,redirect
from django.template import loader
from django.http import HttpResponse ,HttpResponseRedirect,Http404 ,HttpResponseForbidden
from .models import *
from .forms import *
from django.contrib.auth.views import *
from django.utils.translation import ugettext as _
from django.forms import formset_factory
from django.forms import BaseModelFormSet
from datetime import datetime , timedelta
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.models import Group , User
from django.contrib.auth.decorators import permission_required
from django.views.generic import UpdateView, ListView
from .filters import SheetFilter
from django.template.loader import  render_to_string
from django.http import JsonResponse
from django.views.generic.list import ListView
from django.core.urlresolvers import resolve
from django.core.cache import cache
from rest_framework import viewsets , generics
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.sites import requests

from .serializers import UserSerializer, GroupSerializer



class SheetsStatusViewSet(APIView):
    """
    API endpoint that allows users to be viewed or edited.
    """
    def get(self, request, status,empid):
        """
        Get current week range start week is sunday end day is saturday
        """
        date = datetime.now()
        year, week, dow = date.isocalendar()
        if dow == 7:
            start_date = date
        else:
            start_date = date - timedelta(dow)
        end_date = start_date + timedelta(6)
        """ End current week """
        sheet = Sheet.objects.filter(empid=empid)
        if status == 'inprogress':
            sheet = sheet.filter(Q(status=1))
        elif status == 'notfinish':
            sheet = sheet.filter(Q(status=3))
        queryset = sheet.filter(
            Q(taskdate__gte=end_date, createddate__lte=start_date) |
            Q(taskdate__lte=end_date, taskdate__gte=start_date) |
            Q(createddate__lte=end_date, createddate__gte=start_date)
        )

        serializer_class = UserSerializer(queryset,many=True)
        return Response(serializer_class.data)


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


def RestApi(request):
    import urllib.request, json
    empid = '1028645107'
    with urllib.request.urlopen("http://127.0.0.1:8000/project/api-sheets/inprogress/" + empid + '/') as url:
        data = json.loads(url.read())
    context = {'user':data}
    return render(request, 'project/rest-api.html', context)


class BaseSheetFormSet(BaseModelFormSet):
    def clean(self):
        if any(self.errors):
            return
        taskdesc = []
        for form in self.forms:
            taskdescs = form.cleaned_data['taskdescs']
            if taskdescs in titles:
                raise forms.ValidationError("Articles in a set must have distinct titles.")
            titles.append(title)


def loginfromdrupal(request, email,signature,time):
    from django.urls import resolve
    current_url = resolve(request.path_info).namespaces
    request.session['current_url'] = None
    if current_url:
        request.session['current_url'] = current_url
    print ("current url" ,current_url)
    from django.contrib.auth import login
    import getpass
    import datetime
    """ Email function """
    def decrypted(text):
        from Crypto.Cipher import AES
        from Crypto.Cipher import DES
        import base64
        #AES.key_size=128
        key = b"5E712B225B5148E9"
        iv = b"55FE52A86C3ABWED"
        crypt_object = AES.new(key=key,mode=AES.MODE_CBC,IV=iv)
        original = text
        plain = original.replace('-', "/")
        decoded=base64.b64decode(plain) # your ecrypted and encoded text goes here
        decrypted=crypt_object.decrypt(decoded)
        decrypted = decrypted.decode("utf-8")
        return decrypted
    """" return mail"""
    mail = decrypted(email)
    """ return ip """
    ip = 1
    ip = decrypted(signature)
    """ return time """
    time = decrypted(time)

    now = datetime.datetime.now()
    now_plus_10 = now + datetime.timedelta(minutes = 1)
    time_now = now.strftime('%H:%M')
    date_after_minute = now_plus_10.strftime('%H:%M')

    """ Current ip """
    current_ip = request.META.get('REMOTE_ADDR')
    """" Get url from"""
    URL = request.META.get('HTTP_REFERER')
    print (URL)
    referer = None
    if URL:
        referer= URL.split("/")[2]
    if referer == 'portal.stats.gov.sa':
        if current_ip in ip:
        #     if time == time_now or time == date_after_minute:
            username = mail
            try:
                user = User.objects.get(username=username)
                #manually set the backend attribute
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user)
            except User.DoesNotExist:
                from django_auth_ldap.backend import LDAPBackend
                ldap_backend = LDAPBackend()
                ldap_backend.populate_user(username)
                # return HttpResponseRedirect(reverse('login'))
            try:
                user = User.objects.get(username=username)
                #manually set the backend attribute
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user)
            except User.DoesNotExist:
                if 'ramadan' in current_url:
                    return HttpResponseRedirect(reverse('ramadan:login'))
                return HttpResponseRedirect(reverse('login'))
            if request.user.is_authenticated():
                email = request.user.email
                emp = Employee.objects.filter(email= email)
            # Get all data filtered by user email and set in session
                for data in emp:
                    request.session['EmpID'] = data.empid
                    request.session['EmpName'] = data.empname
                    request.session['DeptName'] = data.deptname
                    request.session['Mobile'] = data.mobile
                    request.session['DeptCode'] = data.deptcode
                    request.session['JobTitle'] = data.jobtitle
                    request.session['IsManager'] = data.ismanager
                if emp:
                    if data.ismanager == 1:
                        g = Group.objects.get(name='ismanager')
                        g.user_set.add(request.user.id)
                    else:
                        g = Group.objects.get(name='employee')
                        g.user_set.add(request.user.id)
                # if not emp:
                #     g = Group.objects.get(name='employee')
                #     g.user_set.add(request.user.id)
            else:
                return HttpResponseRedirect(reverse('login'))
    else:
        if 'ramadan' in current_url:
            return HttpResponseRedirect(reverse('ramadan:login'))

        return HttpResponseRedirect(reverse('login'))

    logged = request.COOKIES.get('logged_in_status')
    context = {'logged':logged, "mail":mail,"ip":ip,"time1":time,"URL":referer}
    template = loader.get_template('project/index.html')
    return HttpResponseRedirect(reverse('ns-project:index'))

def myuser(request, *args, **kwargs):
    if request.method == "POST":
        form = BootstrapAuthenticationForm(request, data=request.POST)
        emp = None
        if form.is_valid():
          auth_login(request, form.get_user())
            # email = None
        if request.user.is_authenticated():
            email = request.user.email
            emp = Employee.objects.filter(email= email)
        # Get all data filtered by user email and set in session
            for data in emp:
                request.session['EmpID'] = data.empid
                request.session['EmpName'] = data.empname
                request.session['DeptName'] = data.deptname
                request.session['Mobile'] = data.mobile
                request.session['DeptCode'] = data.deptcode
                request.session['JobTitle'] = data.jobtitle
                request.session['IsManager'] = data.ismanager
            if emp:
                if data.ismanager == 1:
                    g = Group.objects.get(name='ismanager')
                    g.user_set.add(request.user.id)
                else:
                    g = Group.objects.get(name='employee')
                    g.user_set.add(request.user.id)
            # if not emp:
            #     g = Group.objects.get(name='employee')
            #     g.user_set.add(request.user.id)

        else:
            return login(request, *args, **kwargs)
    return login(request, *args, **kwargs)

@login_required
def index(request):
    current_url = request.session.get('current_url')
    print ('session', current_url)
    if current_url:
        if 'ramadan' in current_url:
            print('ramadan login')
            return HttpResponseRedirect(reverse('ramadan:index'))
    if request.user.is_authenticated():
        deptcode= request.session.get('DeptCode')
    if request.session.get('IsManager'):
        return HttpResponseRedirect(reverse('ns-project:dept-sheet' ,kwargs={'deptcode': deptcode}))
    else:
        return HttpResponseRedirect(reverse('ns-project:my-sheet'))
    if request.user.is_authenticated():
        emp = get_object_or_404(Employee, empid = request.session.get('empid'))
    if emp.ismanager == 1:
        template = loader.get_template('project/index.html')
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect(reverse('ns-project:my-sheet'))
    logged = request.COOKIES.get('logged_in_status')
    context = {'logged':logged}
    template = loader.get_template('project/index.html')
    return HttpResponse(template.render(context, request))
# request.session['idempresa'] = profile.idempresa

def gentella_html(request):
    context = {'LANG': request.LANGUAGE_CODE}
    # The template to be loaded as per gentelella.
    # All resource paths for gentelella end in .html.
    # Pick out the html file name from the url. And load that template.
    load_template = request.path.split('/')[-1]
    template = loader.get_template('project/' + load_template)
    return HttpResponse(template.render(context, request))

@login_required
@permission_required('project.add_sheet',raise_exception=True)
def MySheet(request):
    EmpID = 0
    if request.user.is_authenticated():
        EmpID = request.session.get('EmpID',1)
    sheets = Sheet.objects.filter(empid = EmpID).order_by('ifsubmitted','status')
    count = len(list(sheets))
    if count == 0:
        messages.info(request, _("No tasks"))
    context = {'AllSheets': sheets,'count':count}
    return render(request, 'project/my_tasks.html', context)

@login_required
def EmpSheet(request,empid):
    '''
    Page For Manager to See Employees Sheets
    '''
    """
    Get current week range start week is sunday end day is saturday
    """
    EmpID = request.session.get('EmpID')
    date = datetime.now()
    year, week, dow = date.isocalendar()
    if dow == 7:
        start_date = date
    else:
        start_date = date - timedelta(dow)
    end_date = start_date + timedelta(6)
    """ End current week """
    EmpData = get_object_or_404(Employee, empid = empid)
    deptcode = EmpData.deptcode
    deptcode = request.session.get('DeptCode')
    alldept = _get_tree_dept(deptcode)
    # alldept = request.session.get('TreeDept', '0')
    delegation = Delegation.objects.filter(authorized = EmpID, expired = '0')
    auth_dept = []
    for data in delegation:
        auth_dept.append(data.deptcode.deptcode)
    have_permission = False
    if int(deptcode) in auth_dept:
        have_permission = True
    """ Check if this manager and have permission to see EMP sheets """
    his_manager = False
    if str(EmpData.managercode) == str(request.session['EmpID']):
        his_manager = True
    if str(EmpData.managercode) == str(request.session['EmpID']) or deptcode in alldept or have_permission or request.user.groups.filter(name='supermanager').exists():
        """ Get all sheets """
        sheet_list = Sheet.objects.filter(empid = empid).order_by('ifsubmitted','status')
        """ Get only sheet for current week """
        sheet_list = sheet_list.filter(
            Q(taskdate__gte=end_date , createddate__lte=start_date)|
            Q(taskdate__lte=end_date , taskdate__gte=start_date)|
            Q(createddate__lte=end_date , createddate__gte=start_date)
            # Q(createddate__gte=start_date)
            )
        """ Get value from get to filter """
        start = request.GET.get("q_start")
        end = request.GET.get("q_end")
        # if start is None:
        #     end = datetime.strptime('2014-12-04', '%Y-%m-%d').date()
        #     start = start_date

        start_date = start_date.strftime('%Y-%m-%d')
        end_date = end_date.strftime('%Y-%m-%d')
        if start and end:
            """ Get only sheet for date filter """
            sheet_list = Sheet.objects.filter(
                Q(empid__exact = empid ,taskdate__gte=end, createddate__lte=start)|
                Q(empid__exact = empid ,taskdate__lte=end , taskdate__gte=start)|
                Q(empid__exact = empid ,createddate__lte=end , createddate__gte=start)
                )
        """ Render filter fields """
        sheet_filter = SheetFilter(request.GET, queryset=sheet_list)

    else:
        raise Http404

    context = {"date":date,"week":week,"start_date":start_date,"end_date":end_date,'filter': sheet_filter,
    'have_permission':have_permission,'EmpData':EmpData,"his_manager":his_manager}
    return render(request, 'project/emp_sheet.html', context)

@login_required
def AllSheets(request):
    AllEmp = VSheetsdata.objects.filter()
    query = request.GET.get("q")
    if query:
        AllEmp = VSheetsdata.objects.filter(
        Q(employeeid__icontains = query)|
        Q(employeename__icontains = query)|
        Q(deptname__icontains = query)
        )
    # for data in AllEmp:
    count = len(list(AllEmp))
    if count == 0:
        messages.info(request, _("No data there"))
        return render(request, 'project/all_emp_sheets.html')
    context = {'allemp':AllEmp,"count":count}
    return render(request, 'project/all_emp_sheets.html',context)

@login_required
def DeptsnoSheets(request):
    dept_code = request.session.get('DeptCode', 2322)
    """
    Get current week range start week is sunday end day is saturday
    """
    date = datetime.now()
    year, week, dow = date.isocalendar()
    if dow == 7:
        start_date = date
    else:
        start_date = date - timedelta(dow)
    end_date = start_date + timedelta(6)
    """ End current week """
    #Fix date format
    start_date = start_date.strftime('%Y-%m-%d')
    end_date = end_date.strftime('%Y-%m-%d')

    all_sheets = Sheet.objects.filter(
        Q(deptcode__deptcode__gte = 0)&
        Q(deptcode__deptcode__isnull= False )
        )

    sheets = all_sheets.filter(
        Q(taskdate__gte=end_date , createddate__lte=start_date)|
        Q(taskdate__lte=end_date , taskdate__gte=start_date)|
        Q(createddate__lte=end_date , createddate__gte=start_date)
        )

    start = request.GET.get("q_start", start_date)
    end = request.GET.get("q_end", end_date)
    if start and end:
        """ Get only sheet for date filter """
        sheets = all_sheets.filter(
            Q(taskdate__gte=end, createddate__lte=start)|
            Q(taskdate__lte=end , taskdate__gte=start)|
            Q(createddate__lte=end , createddate__gte=start)
            )
    # Get all tree dept
    tree_dept = _get_tree_dept(dept_code)
    if request.user.groups.filter(name='supermanager').exists():
        sheets = sheets
    else:
        sheets = sheets.filter(deptcode__in = tree_dept)

    # sheets = cache.get('sheets')

    DeptHaveTask = []
    for data in sheets:
        try:
            DeptHaveTask.append(data.deptcode.deptcode)
        except:
            pass
    all_dept = Department.objects.exclude(deptcode__in = DeptHaveTask)
    if request.user.groups.filter(name='supermanager').exists():
        all_dept = all_dept
    else:
        all_dept = all_dept.filter(deptcode__in=tree_dept)

    cache.set('all_dept',all_dept)
    paginator = Paginator(all_dept, 20) # Show 5 contacts per page
    page = request.GET.get('page')
    try:
        _plist = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        _plist = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        _plist = paginator.page(paginator.num_pages)


    count =  (len(all_dept))
    context = {"total_count":_plist,"count":count,"start_date":start_date,"end_date":end_date}
    return render(request, 'project/sheet_no_departments.html',context )

@login_required
def AllDepts(request):
    from django.db.models import Count, Case, When, IntegerField ,F
    dept_code = request.session.get('DeptCode', 2322)
    """
    Get current week range start week is sunday end day is saturday
    """
    date = datetime.now()
    year, week, dow = date.isocalendar()
    if dow == 7:
        start_date = date
    else:
        start_date = date - timedelta(dow)
    end_date = start_date + timedelta(6)
    """ End current week """
    all_sheets = Sheet.objects.filter(
        Q(deptcode__deptcode__gte = 0)&
        Q(deptcode__deptcode__isnull= False )
        )
    # Get all tree dept
    tree_dept = _get_tree_dept(dept_code)
    if request.user.groups.filter(name='supermanager').exists():
        all_sheets = all_sheets
    else:
        all_sheets = all_sheets.filter(deptcode__in = tree_dept)
    cache.set('sheets',all_sheets)
    sheets = all_sheets.filter(
        Q(taskdate__gte=end_date , createddate__lte=start_date)|
        Q(taskdate__lte=end_date , taskdate__gte=start_date)|
        Q(createddate__lte=end_date , createddate__gte=start_date)
        )


       # sheets = sheets.exclude(deptcode__in =DeptHaveTask)
    #Fix date format
    start_date = start_date.strftime('%Y-%m-%d')
    end_date = end_date.strftime('%Y-%m-%d')

    # cache.set('sheets',sheets)
    # sheets = cache.get('sheets')
    start = request.GET.get("q_start", start_date)
    end = request.GET.get("q_end", end_date)
    if start and end:
        """ Get only sheet for date filter """
        sheets = all_sheets.filter(
            Q(taskdate__gte=end, createddate__lte=start)|
            Q(taskdate__lte=end , taskdate__gte=start)|
            Q(createddate__lte=end , createddate__gte=start)
            )

    select_menu = sheets.values('deptcode__deptname','deptcode__managername','deptcode__deptcode').annotate(total=Count('deptcode'))
    query = request.GET.get("q")
    if query and query != '0':
        sheets = sheets.filter(
        Q(deptcode__deptcode = query)
        )
    total_count = sheets.values('deptcode__deptname','deptcode__managername','deptcode__deptcode').annotate(total=Count('deptcode'),
     new_task = Count(Case(When(ifsubmitted =0 ,then=F("deptcode__deptcode")),output_field=IntegerField())),
     submitted_task = Count(Case(When(ifsubmitted =1 ,then=F("deptcode__deptcode")),output_field=IntegerField())),
     finished_task = Count(Case(When(status=2 , ifsubmitted =1 ,then=F("deptcode__deptcode")),output_field=IntegerField())),
     inprogress_task = Count(Case(When(status=1 , ifsubmitted =1 ,then=F("deptcode__deptcode")),output_field=IntegerField())),
     notfinished_task = Count(Case(When(status=3 , ifsubmitted =1 ,then=F("deptcode__deptcode")),output_field=IntegerField())),
     ignore_task = Count(Case(When(ifsubmitted =2 ,then=F("deptcode__deptcode")),output_field=IntegerField())),
     ).all().order_by('-submitted_task')
    cache.set('all_dept',total_count)
    paginator = Paginator(total_count, 20) # Show 5 contacts per page
    page = request.GET.get('page')
    try:
        _plist = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        _plist = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        _plist = paginator.page(paginator.num_pages)


    count =  (len(total_count))
    context = {"total_count":_plist,"select_menu":select_menu,"count":count,"start_date":start_date,"end_date":end_date}
    return render(request, 'project/sheet_all_departments.html',context)

def _get_tree_dept(deptcode):
    dept_level_1 = ApfDeptView.objects.filter(resp_dept_code = deptcode)
    dept_level_2 = []
    dept_level_3 = []
    dept_level_4 = []
    for dept in dept_level_1:
        dept2 = dept.dept_code
        # name = dept.dept_name
        dept_level_2.append(dept2)
        # dept_level_2.append(name)
        dept = ApfDeptView.objects.filter(resp_dept_code = dept2)
        for data in dept:
            dept3= data.dept_code
            # name = data.dept_name
            dept_level_3.append(dept3)
            # dept_level_3.append(name)
            dept = ApfDeptView.objects.filter(resp_dept_code = dept3)
            for data in dept:
                dept4 = data.dept_code
                dept_level_4.append(dept4)
    all_dept =  dept_level_2 + dept_level_3 + dept_level_4
    all_dept.append(deptcode)
    return all_dept

@login_required
def AllDept(request):
    '''
    All departments as tree based on user logged in
    '''
    DeptCode = request.session['DeptCode']
    dept_level_1 = ApfDeptView.objects.filter(resp_dept_code = DeptCode)
    dept_level_2 = []
    dept_level_3 = []
    dept_level_4 = []
    for dept in dept_level_1:
        dept2 = dept.dept_code
        # name = dept.dept_name
        dept_level_2.append(dept2)
        # dept_level_2.append(name)
        dept = ApfDeptView.objects.filter(resp_dept_code = dept2)
        for data in dept:
            dept3= data.dept_code
            # name = data.dept_name
            dept_level_3.append(dept3)
            # dept_level_3.append(name)
            dept = ApfDeptView.objects.filter(resp_dept_code = dept3)
            for data in dept:
                dept4 = data.dept_code
                dept_level_4.append(dept4)
    all_dept =  dept_level_2 + dept_level_3 + dept_level_4
    all_dept.append(DeptCode)
    request.session['TreeDept'] = all_dept
    le = len(list(all_dept))
    SelectDept = VDeptsheetsdata.objects.filter(deptcode__in = all_dept)
    AllDept = VDeptsheetsdata.objects.filter(deptcode__in = all_dept)
    # AllDept = Department.objects.filter(deptcode__in = all_dept)
    DeptHaveTask = []
    for data in AllDept:
        DeptHaveTask.append(data.deptcode)
    query = request.GET.get("q")
    if query and query != '0':
        AllDept = VDeptsheetsdata.objects.filter(
        Q(deptcode = query)
        )
    no_data = request.GET.get("filter")
    if no_data:
       AllDept = Department.objects.filter(deptcode__in = all_dept).exclude(deptcode__in =DeptHaveTask)
    # for data in AllEmp:
        # super manager page
    if request.user.groups.filter(name='supermanager').exists():
        AllDept = VDeptsheetsdata.objects.all().order_by("-totaltask")
        SelectDept = VDeptsheetsdata.objects.all()
        DeptHaveTask = []
        for data in AllDept:
            DeptHaveTask.append(data.deptcode)
        if no_data:
            AllDept = Department.objects.exclude(deptcode__in =DeptHaveTask)
        if query and query != '0':
            AllDept = VDeptsheetsdata.objects.filter(
            Q(deptcode = query)
            )
    count = len(list(AllDept))
    paginator = Paginator(AllDept, 20) # Show 5 contacts per page

    page = request.GET.get('page')
    try:
        _plist = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        _plist = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        _plist = paginator.page(paginator.num_pages)

    if count == 0:
        messages.info(request, _("No data there"))
        context = {'alldept':AllDept,"count":count,"selectdept":SelectDept}
        return render(request, 'project/sheet_all_dept.html',context)
    context = {'alldept':_plist,"count":count,"selectdept":SelectDept,"deptcode":DeptCode,'dept2':dept_level_1
    ,'level3':dept_level_3,'level4':dept_level_4,'alldepartment':all_dept,'len':le
    }

    return render(request, 'project/sheet_all_dept.html',context)

@login_required
def UpdateSheet(request,empid):

    SbmitSheet = modelformset_factory(Sheet, fields=('taskdesc', 'tasktype', 'duration','durationhoure','taskcount','taskdate','submit'), extra=0,
        widgets = {
            'taskdesc': forms.Textarea(attrs={'class': 'form-control','readonly':True,'rows': 1}),
            'tasktype': forms.Select(attrs={'class': 'form-control pointer cust-select','readonly':True}),
            'duration': forms.NumberInput(attrs={'class': 'form-control','readonly':True}),
            'durationhoure': forms.NumberInput(attrs={'class': 'form-control','readonly':True}),
            'taskcount': forms.NumberInput(attrs={'class': 'form-control','readonly':True}),
            'taskdate': forms.TextInput(attrs={'class': 'form-control pointer','readonly':True}),
            'submit': forms.CheckboxInput(attrs={'class':'custom-control-input'})
        }
    )

    # formset = SbmitSheet()
    formset = SbmitSheet(queryset=Sheet.objects.filter(Q(ifsubmitted = '0'), empid= empid
    ))
    count = Sheet.objects.filter(Q(ifsubmitted = '0'), empid= empid).count()
    if count == 0:
        messages.info(request, _("No data for submitted"))
    start = request.GET.get("q_start")
    end = request.GET.get("q_end")
    if start:
        formset = SbmitSheet(queryset=Sheet.objects.filter(~Q(ifsubmitted = '1'), empid= empid ,
        taskdate__gte=start, taskdate__lte=end
        ))
    EmpSheet = get_object_or_404(Employee, empid = empid)
    EmpData = Employee.objects.filter(empid = empid)
    dept = Department.objects.filter(deptcode = EmpSheet.deptcode)[:1]
    managid = 0
    # Get manager id for employee
    for data in dept:
        managid = data.managerid
    EmpID = 0
    if request.user.is_authenticated():
        EmpID = request.session.get('EmpID', "1")
    # empid = 123456
    if managid == EmpID:
        if request.method == 'POST':
            submit = request.POST.get("query")
            formset = SbmitSheet(request.POST)
            if formset.is_valid():
                instances = formset.save(commit=False)
                # Get managers as hierarchicaly
                for obj in instances:
                    submit = request.POST.get("query")

                    obj.submittedby = request.session['EmpID']
                    obj.submitteddate = datetime.now()

                    if obj.submit is True and submit == '1':
                        obj.submit = False
                        obj.ifsubmitted = '1'
                        obj.status = '1'
                    if obj.submit is True and submit == '2':
                        obj.submit = False
                        obj.ifsubmitted ='2'
                        obj.status = '3'
                    obj.submit = False
                    obj.save()
                return HttpResponseRedirect(reverse('ns-project:update-sheet', kwargs={'empid':empid} ))
                # return HttpResponseRedirect(reverse('ns-project:all-sheets'))
        else:
            formset = formset
    else:
        raise Http404
    # form = form_class(request.POST or None)
    return render(request, 'project/update_sheet.html', {'form': formset,'EmpData':EmpData,'count':count})

@login_required
def DetailseSheet(request,empid):
    EmpData = Employee.objects.filter(empid = empid)
    allsheet = Sheet.objects.filter(empid =empid)
    return render(request, 'project/details_sheets.html', {'EmpData':EmpData, 'allsheet':allsheet})

@login_required
def DeptSheet(request,deptcode):
    if request.user.is_authenticated():
        DeptCode = request.session.get("DeptCode", 0)
        EmpID = request.session['EmpID']
    dept = Department.objects.filter(deptcode= deptcode)[:1]
    managid = '0'
    sheets = None
    alldept = _get_tree_dept(DeptCode)
    for data in dept:
        managid = data.managerid
    delegation = Delegation.objects.filter(authorized = EmpID, expired = '0')
    auth_dept = []
    for data in delegation:
        auth_dept.append(data.deptcode.deptcode)
    have_permission = False
    if int(deptcode) in auth_dept:
        have_permission = True
    if managid == EmpID or deptcode in alldept or have_permission or request.user.groups.filter(name='supermanager').exists():
        # if this user is manager
        AllEmp = "0"
        #count all data
        sheet = Sheet.objects.all()
        emp_count = Employee.objects.filter(deptcode = deptcode).count()
        total_task = sheet.filter(deptcode = deptcode,ifsubmitted='1').count()
        inprogress_task = sheet.filter(deptcode = deptcode,ifsubmitted='1',status = 1).count()
        submitted_task = sheet.filter(deptcode = deptcode,ifsubmitted='1', status = 2).count()
        not_submitted_task = sheet.filter(deptcode = deptcode,ifsubmitted='1', status = 3).count()
        AllEmp = VSheetsdata.objects.filter(deptcode = deptcode).order_by('new')
        query = request.GET.get("q")
        if query:
            AllEmp = VSheetsdata.objects.filter(
            Q(deptcode = deptcode)&
            Q(employeename__icontains = query)
            )
        #show employee not have sheet last 7 days
        last_week_data = Sheet.objects.filter(deptcode = deptcode
            ,taskdate__gte=datetime.now()-timedelta(days=7)
            ).values('empid').distinct()

        emp_last_week = []
        for data in last_week_data:
            emp_last_week.append(data['empid'])

        emp_last_week.append(managid)
        no_data = request.GET.get("filter")
        if no_data:
           AllEmp = Employee.objects.filter(deptcode = deptcode).exclude(empid__in=emp_last_week)
           # Filteremp = AllEmp.filter(empid__in=emp_last_week)
    else:
        raise Http404

    count = len(list(AllEmp))
    context = {'managid':managid,'allemp':AllEmp,"count":count,"total_task":total_task,'dpartment_code':deptcode,
    "data7week":emp_last_week,"filteremp":AllEmp,"inprogress_task":inprogress_task,
    "submitted_task":submitted_task,"n_task":not_submitted_task,"emp_count":emp_count}
    if count == 0:
        messages.info(request, _("No data"))
        return render(request, 'project/all_sheets.html',context)

    return render(request, 'project/all_sheets.html',context)

def _ecport_toexcel(all_emp):
    import xlwt
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Employees.xls"'
    emp_have_task = Sheet.objects.all()
    emp_list = []
    for data in emp_have_task:
        emp_list.append(data.empid)
    emp_list = set(emp_list)
    all_emp = Employee.objects.exclude(Q(empid__in = emp_list)|
        Q(ismanager = 1)
        )
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Users')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = [_('Name'), _('Job title'), _('Department'), _('Email address'), _('Ext')]

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    rows = all_emp.values_list('empname', 'jobtitle', 'deptname', 'email','ext')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response

def export_users_xls(request):
    import xlwt
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Employees-nosheets.xls"'
    all_emp =  cache.get('all_emp')
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Users')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = [_('Name'), _('Job title'), _('Department'), _('Email address'), _('Ext')]

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    rows = all_emp.values_list('empname', 'jobtitle', 'deptname', 'email','ext')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response

def export_empnosheet_xls(request):
    import xlwt
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Employees-notfinished.xls"'
    all_emp =  cache.get('all_emp_nosheet')
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Users')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = [_('Name'), _('Job title'), _('Department'), _('Manager Name'), _('Task not complete')]

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    rows = all_emp.values_list('empid__empname', 'empid__jobtitle', 'deptcode__deptname','deptcode__managername','total')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response

def export_department_xls(request):
    import xlwt
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="departments.xls"'
    all_emp =  cache.get('all_dept')
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Users')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = [_('Department'), _('Manager Name'), _('Task count submitted'), _('Task count not submitted'), _('Task not submitted')
    , _('Task Done'), _('Task inprogress'), _('Task not complete')]

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    rows = all_emp.values_list('deptcode__deptname', 'deptcode__managername', 'submitted_task','new_task','ignore_task',
        'finished_task','inprogress_task','notfinished_task')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response

def export_departmentnosheet_xls(request):
    import xlwt
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="departments.xls"'
    all_emp =  cache.get('all_dept')
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Users')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = [_('Department'), _('Manager Name'),]

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    rows = all_emp.values_list('deptname', 'managername')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response

@login_required
def EmployeeNoSheet(request):
    """
    Get current week range start week is sunday end day is saturday
    """
    date = datetime.now()
    year, week, dow = date.isocalendar()
    if dow == 7:
        start_date = date
    else:
        start_date = date - timedelta(dow)
    end_date = start_date + timedelta(6)
    """ End current week """
    emp_have_task = Sheet.objects.filter(
        Q(taskdate__gte=end_date , createddate__lte=start_date)|
        Q(taskdate__lte=end_date , taskdate__gte=start_date)|
        Q(createddate__lte=end_date , createddate__gte=start_date)
        )
    start = request.GET.get("q_start", start_date)
    end = request.GET.get("q_end", end_date)
    if start and end:
        """ Get only sheet for date filter """
        emp_have_task = Sheet.objects.filter(
            Q(taskdate__gte=end, createddate__lte=start)|
            Q(taskdate__lte=end , taskdate__gte=start)|
            Q(createddate__lte=end , createddate__gte=start)
            )
    emp_list = []
    for data in emp_have_task:
        emp_list.append(data.empid.empid)
    #Fix date format
    start_date = start_date.strftime('%Y-%m-%d')
    end_date = end_date.strftime('%Y-%m-%d')

    emp_list = set(emp_list)
    all_emp = Employee.objects.exclude(Q(empid__in = emp_list)|
        Q(ismanager = 1)
        )
    count = all_emp.count()
    # all_emp = all_emp.filter(sexcode=1)
    all_emp_1 = all_emp
    export = request.GET.get("export")

    cache.set('all_emp',all_emp)

    paginator = Paginator(all_emp, 20) # Show 5 contacts per page

    page = request.GET.get('page')
    try:
        _plist = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        _plist = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        _plist = paginator.page(paginator.num_pages)

    context = {'count':count, 'All_Emp':_plist , 'emp_list':emp_list,"start_date":start_date,"end_date":end_date,}
    return render(request, 'project/emp_no_sheet.html',context)
# Add sheet form

@login_required
def EmpnotFinished(request):
    from django.db.models import Count
    """
    Get current week range start week is sunday end day is saturday
    """
    date = datetime.now()
    year, week, dow = date.isocalendar()
    if dow == 7:
        start_date = date
    else:
        start_date = date - timedelta(dow)
    end_date = start_date + timedelta(6)
    """ End current week """
    sheets = Sheet.objects.filter(Q(status=3)&Q(ifsubmitted=1))
        # Q(taskdate__gte=end_date , createddate__lte=start_date)|
        # Q(taskdate__lte=end_date , taskdate__gte=start_date)|
        # Q(createddate__lte=end_date , createddate__gte=start_date)
        # )
    sheets = sheets.filter(
        Q(taskdate__gte=end_date , createddate__lte=start_date)|
        Q(taskdate__lte=end_date , taskdate__gte=start_date)|
        Q(createddate__lte=end_date , createddate__gte=start_date)
        )

    start = request.GET.get("q_start", start_date)
    end = request.GET.get("q_end", end_date)
    if start and end:
        sheets = Sheet.objects.filter(Q(status=3)&Q(ifsubmitted=1))
        """ Get only sheet for date filter """
        sheets = sheets.filter(
            Q(taskdate__gte=end, createddate__lte=start)|
            Q(taskdate__lte=end , taskdate__gte=start)|
            Q(createddate__lte=end , createddate__gte=start)
            )

    #Fix date format
    start_date = start_date.strftime('%Y-%m-%d')
    end_date = end_date.strftime('%Y-%m-%d')
    # sheets = sheets.values("empid").annotate(Count("id")).order_by()
    sheets = sheets.values('empid__empname','empid__jobtitle','empid__empid','deptcode__managername','deptcode__deptname').annotate(total=Count('empid'))
    paginator = Paginator(sheets, 20) # Show 5 contacts per page
    cache.set('all_emp_nosheet',sheets)
    page = request.GET.get('page')
    try:
        _plist = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        _plist = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        _plist = paginator.page(paginator.num_pages)
    count =  (len(sheets))
    context ={"sheets":_plist,'count':count,"start_date":start_date,"end_date":end_date,}
    return render(request, 'project/sheet_not_finished.html', context)

@login_required
def AddSheet(request):
    AddSheet = modelformset_factory(Sheet, fields=('taskdesc', 'tasktype', 'duration','durationhoure','taskdate','taskcount'),can_delete=True, extra=7,
        widgets = {
            'taskdesc': forms.Textarea(attrs={'class': 'form-control','rows': 1 ,   }),
            'tasktype': forms.Select(attrs={'class': 'form-control'}),
            'duration': forms.NumberInput(attrs={'class': 'form-control','min': 0}),
            'durationhoure': forms.NumberInput(attrs={'class': 'form-control','min': 0}),
            'taskcount': forms.NumberInput(attrs={'class': 'form-control','min': 0}),
            'taskdate': forms.TextInput(attrs={'class': 'datepicker form-control',}),
        }
    )
    EmpID = 0
    if request.user.is_authenticated():
        EmpID = request.session['EmpID']

    formset = AddSheet(queryset=Sheet.objects.filter(empid= EmpID , ifsubmitted = '0'
    # ,taskdate__gte=datetime.now()-timedelta(days=7), taskdate__lte=datetime.now()+ timedelta(days=7)
    ))

    # formset = AddSheet(initial=[{'tasktype': 'm'}])

    if request.method == 'POST':
        formset = AddSheet(request.POST)
        if formset.is_valid():
            instances = formset.save(commit=False)
            # Get managers as hierarchicaly
            email = request.user.email
            emp = Employee.objects.filter(email= email)
            # managr level 1
            managercode = manager_2 = manager_3 = manager_4 = 0
            for data in emp:
                managercode = data.managercode
                request.session['MNGID'] = managercode
            # managr level 2
            emp1 = Employee.objects.filter(empid=managercode)
            for manager in emp1:
                 manager_2 = manager.managercode
            # managr level 3
            emp2 = Employee.objects.filter(empid=manager_2)
            for manager in emp2:
                 manager_3 = manager.managercode
            # managr level 4
            emp3 = Employee.objects.filter(empid=manager_3)
            for manager in emp3:
                 manager_4 = manager.managercode
            for obj in instances:
                obj.empid = get_object_or_404(Employee,empid__exact=EmpID)
                obj.deptcode = get_object_or_404(Department,deptcode__exact=request.session['DeptCode'])
                obj.managercode = managercode
                obj.managerlevel2 = manager_2
                obj.managerlevel3 = manager_3
                obj.managerlevel4 = manager_4
                obj.ifsubmitted = '0'
                obj.status = '0'
                if obj.createddate:
                    obj.editedate = datetime.now()
                else:
                    obj.createddate = datetime.now()
                obj.save()
            for obj in formset.deleted_objects:
                obj.delete()
            messages.success(request, _("Post Submit"))
            return HttpResponseRedirect(reverse('ns-project:my-sheet'))
    else:
        formset = formset
    # form = form_class(request.POST or None)
    return render(request, 'project/add-sheet.html', {'form': formset})

@login_required
def SubmitSheet(request,pk):
    '''
    Submit or not submit individual sheet by manager.
    '''
    if request.user.is_authenticated():
        EmpID = request.session['EmpID']
    SbmitSheet = modelformset_factory(Sheet, fields=('taskdesc', 'tasktype', 'duration','taskdate','ifsubmitted'), can_delete=True, extra=0,
        widgets = {
            'taskdesc': forms.TextInput(attrs={'class': 'form-control','readonly':True}),
            'tasktype': forms.Select(attrs={'class': 'form-control pointer','readonly':True}),
            'duration': forms.NumberInput(attrs={'class': 'form-control','readonly':True}),
            'taskdate': forms.TextInput(attrs={'class': 'form-control pointer','readonly':True}),
            'ifsubmitted': forms.Select(attrs={'class': 'form-control'}),
        }
    )
    formset = SbmitSheet(queryset=Sheet.objects.filter(id = pk,ifsubmitted='0' ))
    # taskdate__gte=datetime.now()-timedelta(days=7), taskdate__lte=datetime.now()+ timedelta(days=7)
    SheetData = get_object_or_404(Sheet,pk=pk)
    sheetid = SheetData.empid
    employeeid = SheetData.empid.empid
    # if EmpID == str(sheetid):
    if request.method == 'POST':
        formset = SbmitSheet(request.POST)
        if formset.is_valid():
            instances = formset.save(commit=False)
            for obj in instances:
                obj.submittedby = request.session['EmpID']
                obj.submitteddate = datetime.now()
                if obj.ifsubmitted == '1':
                    obj.status = '1'
                if obj.ifsubmitted == '2':
                    obj.status = '3'
                obj.save()
            messages.success(request, _("Post Done"))
            return HttpResponseRedirect(reverse('ns-project:emp-sheet', kwargs={'empid':employeeid} ))
    else:
        formset = formset
    # else:
    #     raise Http404
    # form = form_class(request.POST or None)
    return render(request, 'project/submit_sheet.html', {'form': formset,'Sheetid':sheetid,'EmpID':EmpID})

@login_required
def EditSheet(request,pk):
    from django.utils import timezone
    import pytz
    if request.user.is_authenticated():
        EmpID = request.session['EmpID']
    SbmitSheet = modelformset_factory(Sheet, fields=('taskdesc', 'tasktype', 'duration','durationhoure','taskdate','ifsubmitted','taskcount'), can_delete=True, extra=0,
        widgets = {
            'taskdesc': forms.TextInput(attrs={'class': 'form-control'}),
            'tasktype': forms.Select(attrs={'class': 'form-control'}),
            'duration': forms.NumberInput(attrs={'class': 'form-control'}),
            'durationhoure': forms.NumberInput(attrs={'class': 'form-control'}),
            'taskcount': forms.NumberInput(attrs={'class': 'form-control'}),
            'taskdate': forms.TextInput(attrs={'class': 'form-control'}),
            'ifsubmitted': forms.Select(attrs={'class': 'form-control'}),
        }
    )
    formset = SbmitSheet(queryset=Sheet.objects.filter(id = pk,ifsubmitted='0' ))
    # taskdate__gte=datetime.now()-timedelta(days=7), taskdate__lte=datetime.now()+ timedelta(days=7)
    SheetData = get_object_or_404(Sheet,pk=pk)
    sheetid = SheetData.empid.empid
    if EmpID == str(sheetid):
        if request.method == 'POST':
            formset = SbmitSheet(request.POST)
            if formset.is_valid():
                instances = formset.save(commit=False)
                # Get managers as hierarchicaly
                for obj in instances:
                    obj.editedate = timezone.now()
                    obj.ifsubmitted = 0
                    obj.save()
                for obj in formset.deleted_objects:
                    obj.delete()
                messages.success(request, _("Edit complete"))
                return HttpResponseRedirect(reverse('ns-project:my-sheet'))
        else:
            formset = formset
    else:
        raise Http404
    # form = form_class(request.POST or None)
    return render(request, 'project/edit_s_sheet.html', {'form': formset,'Sheetid':sheetid,'EmpID':EmpID})

@login_required
def ChangeStatus(request,pk):
    if request.user.is_authenticated():
        EmpID = request.session['EmpID']
    ChangeStatus = modelformset_factory(Sheet, fields=('taskdesc', 'tasktype', 'duration','taskdate','reason','status'),extra=0,
        widgets = {
            'taskdesc': forms.TextInput(attrs={'class': 'form-control','readonly':True}),
            'tasktype': forms.Select(attrs={'class': 'form-control pointer','readonly':True}),
            'duration': forms.TextInput(attrs={'class': 'form-control','readonly':True}),
            'taskdate': forms.TextInput(attrs={'class': 'form-control pointer','readonly':True}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'reason': forms.Select(attrs={'class': 'form-control'}),
        }
    )
    formset = ChangeStatus(queryset=Sheet.objects.filter(ifsubmitted = '1',id = pk ))
    # taskdate__gte=datetime.now()-timedelta(days=7), taskdate__lte=datetime.now()+ timedelta(days=7)
    SheetData = get_object_or_404(Sheet,pk=pk)
    sheetid = SheetData.empid.empid
    if EmpID == str(sheetid):
        if request.method == 'POST':
            formset = ChangeStatus(request.POST)
            if formset.is_valid():
                instances = formset.save(commit=False)
                # Get managers as hierarchicaly
                for obj in instances:
                    obj.statusdate = datetime.now()
                    obj.save()

                messages.success(request, _("Change status done"))
                return HttpResponseRedirect(reverse('ns-project:my-sheet'))
        else:
            formset = formset
    else:
        raise Http404
    # form = form_class(request.POST or None)
    return render(request, 'project/change_s_sheet.html', {'form': formset})

def AddProject(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ProjectForm(request.POST)
        if form.is_valid():
            project_obj= form.save(commit=False)
            try:
               status_obj= ProjectStatus.objects.get(isdefault=1)
            except :
               status_obj= ProjectStatus.objects.order_by('priority')[0]

            project_obj.status=status_obj
            project_obj.createdby=request.session.get('EmpID', '1056821208')
            project_obj.createddate= datetime.now()
            #save to database
            project_obj.save()
            # redirect to a new URL:
            messages.success(request, _("Project has created successfully"))
            return HttpResponseRedirect(reverse('ns-project:project-list'))

    # if a GET (or any other method) we'll create a blank form
    else:
        form = ProjectForm()

    return render(request, 'project/add_project.html', {'form': form,'action_name': _('Ad Project')})

def ProjectList(request):
    createdBy=request.session.get('EmpID', '1056821208')
    project_list= Project.objects.all().filter(createdby__exact=createdBy).order_by('-id')
    paginator = Paginator(project_list, 5) # Show 5 contacts per page

    page = request.GET.get('page')
    try:
        _plist = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        _plist = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        _plist = paginator.page(paginator.num_pages)

    context = {'project_list':_plist}
    return render(request, 'project/projects.html', context)

def ProjectDetail(request,pk):
    project_detail= get_object_or_404(Project,pk=pk)
    createdBy=request.session.get('EmpID', '1056821208')
    project_list= Project.objects.all().filter(createdby__exact=createdBy).exclude(status=4).order_by('-id')
    current_url ="ns-project:" + resolve(request.path_info).url_name
    context={'project_detail':project_detail,'project_list':project_list,'current_url':current_url}
    return render(request, 'project/project_detail.html', context)

def ProjectEdit(request,pk):
    instance = get_object_or_404(Project,pk=pk)
    form = ProjectForm(request.POST or None, instance=instance)
    if form.is_valid():
       instance=form.save()
       instance.save()
       messages.success(request, _("Project has updated successfully"), fail_silently=True,)
       return HttpResponseRedirect(reverse('ns-project:project-list'))
    else:
        # Set the messages level back to default.
        #messages.add_message(request, messages.ERROR, 'Can not update project.', fail_silently=True, extra_tags='alert')
        #messages.error(request, _("Can not update project."))
        return render(request, 'project/add_project.html', {'form': form,'action_name': _('Edit Project')})

def ProjectDelete(request,pk):
    p= get_object_or_404(Project,pk=pk)
    emp_obj=Employee.objects.get(empid__exact=p.createdby)
    if request.method == 'POST':
          Project.objects.filter(id=p.id).delete()
          messages.success(request, _("Project has deleted successfully"), fail_silently=True,)
          return HttpResponseRedirect(reverse('ns-project:project-list'))
    else:
          context={'p':p,'emp_obj':emp_obj}
          return render(request, 'project/project_delete.html',context)

def ProjectTask(request,pk,task_status=None):
    current_url ="ns-project:" + resolve(request.path_info).url_name
    empid=request.session.get('EmpID', '1056821208')
    project_detail= get_object_or_404(Project,pk=pk)
    project_list= Project.objects.all().filter(createdby__exact=empid).exclude(status=4).order_by('-id')

    if task_status=="all":
         task_list= Task.objects.all().filter(createdby__exact=empid, projectid__exact=pk).order_by('-id')
    elif task_status=="unclosed":
         task_list= Task.objects.all().filter(createdby__exact=empid, projectid__exact=pk).exclude(status__exact='Closed').order_by('-id')
    elif task_status=="assignedtome":
         task_list= Task.objects.all().filter( projectid__exact=pk,assignedto__exact=empid).order_by('-id')
    elif task_status=="new":
         task_list= Task.objects.all().filter(createdby__exact=empid, projectid__exact=pk,status__exact='New').order_by('-id')
    elif task_status=="inprogress":
         task_list= Task.objects.all().filter(createdby__exact=empid, projectid__exact=pk,status__exact='InProgress').order_by('-id')
    elif task_status=="finishedbyme":
         task_list= Task.objects.all().filter(finishedby__exact=empid, projectid__exact=pk,status__exact='Done').order_by('-id')
    elif task_status=="done":
         task_list= Task.objects.all().filter( projectid__exact=pk,status__exact='Done').order_by('-id')
    elif task_status=="closed":
         task_list= Task.objects.all().filter( projectid__exact=pk,status__exact='Closed').order_by('-id')
    elif task_status=="cancelled":
         task_list= Task.objects.all().filter( projectid__exact=pk,status__exact='Cancelled').order_by('-id')
    elif task_status=="hold":
         task_list= Task.objects.all().filter( projectid__exact=pk,status__exact='Hold').order_by('-id')
    elif task_status=="delayed":
         task_list= Task.objects.all().filter( projectid__exact=pk,enddate__lt = datetime.today()).order_by('-id')
    else :
       task_list= Task.objects.all().filter(createdby__exact=empid, projectid__exact=pk).order_by('-id')


    paginator = Paginator(task_list, 5) # Show 5 contacts per page
    page = request.GET.get('page')
    try:
        _plist = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        _plist = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        _plist = paginator.page(paginator.num_pages)

    context = {'tasks':_plist,'project_detail':project_detail,'project_list':project_list,'current_url':current_url}
    return render(request, 'project/tasks.html', context)

def ProjectTeam(request,pk):
    createdBy=request.session.get('EmpID', '1056821208')
    project_list= Project.objects.all().filter(createdby__exact=createdBy).exclude(status=4).order_by('-id')
    current_url ="ns-project:" + resolve(request.path_info).url_name
    project_detail= get_object_or_404(Project,pk=pk)
    projectmembers= ProjectMembers.objects.all().order_by('-id')

    paginator = Paginator(projectmembers, 5) # Show 5 contacts per page
    page = request.GET.get('page')
    try:
        _mlist = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        _mlist = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        _mlist = paginator.page(paginator.num_pages)


    #project team
    form=TeamForm()

    context = {'form':form,'project_detail':project_detail,'project_list':project_list,'current_url':current_url,'projectmembers':_mlist}
    return render(request, 'project/project_team.html', context)

def ProjectTaskDetail(request,pk):
    createdBy=request.session.get('EmpID', '1056821208')
    task_list= Task.objects.all().filter(createdby__exact=createdBy, projectid__exact=pk).order_by('-id')
    paginator = Paginator(task_list, 5) # Show 5 contacts per page

    page = request.GET.get('page')
    try:
        _plist = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        _plist = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        _plist = paginator.page(paginator.num_pages)

    context = {'tasks':_plist}
    return render(request, 'project/tasks.html', context)

def updateStartDate(request,pk):
    data = dict()
    errors = []

    _obj =  get_object_or_404(Task,pk=pk)
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = TaskStartForm(request.POST)
        if form.is_valid():
            _obj.realstartdate=form.cleaned_data['rsd']
            _obj.realstartby=request.session.get('EmpID', '1056821208')
            _obj.status="InProgress"
            _obj.lasteditdate=datetime.now()
            _obj.lasteditby=request.session.get('EmpID', '1056821208')
            _obj.save()
            data['form_is_valid'] = True
            data['id'] = pk
            data['status'] = _('InProgress')
            data['icon'] = "p_%s" %pk
            data['message'] = _('Start Date Updated successfully for Task number %s ' %pk)
            data['html_form'] = render_to_string('project/update_start_task.html',request=request)
            return JsonResponse(data)

    # if a GET (or any other method) we'll create a blank form
    else:
        data['form_is_valid'] = False
    context = {'form': TaskStartForm(),'pk':pk,'errors':errors}
    data['html_form'] = render_to_string('project/update_start_task.html',context,request=request,)
    return JsonResponse(data)

def updateTaskFinish(request,pk):
    data = dict()
    errors = []

    _obj =  get_object_or_404(Task,pk=pk)
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = TaskFinishForm(request.POST)
        if form.is_valid():
            _obj.ftime=form.cleaned_data['ftime']
            _obj.status="Finished"
            _obj.finisheddate=datetime.now()
            _obj.finishedby=request.session.get('EmpID', '1056821208')
            _obj.lasteditdate=datetime.now()
            _obj.lasteditby=request.session.get('EmpID', '1056821208')
            _obj.save()
            data['form_is_valid'] = True
            data['icon'] = "f_%s" %pk
            data['id'] = pk
            data['status'] = _('Finished')
            data['message'] = _(' Finish Date Updated successfully for Task number %s ' %pk)
            data['html_form'] = render_to_string('project/task/update_finish_task.html',request=request)
            return JsonResponse(data)

    # if a GET (or any other method) we'll create a blank form
    else:
        data['form_is_valid'] = False
    context = {'form': TaskFinishForm(),'pk':pk,'errors':errors}
    data['html_form'] = render_to_string('project/task/update_finish_task.html',context,request=request)
    return JsonResponse({data})

def updateTaskClose(request,pk):
    data = dict()
    errors = []

    if 'notes' in request.POST:
        notes = request.POST['notes']
        if not notes:
            errors.append(_('Enter a notes .'))

    _obj =  get_object_or_404(Task,pk=pk)
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = TaskCloseForm(request.POST )
        if form.is_valid():
            _obj.closeddate=form.cleaned_data['ctime']
            _obj.status="Closed"
            _obj.closedby= request.session.get('EmpID', '1056821208')
            _obj.closeddate=datetime.now()
            _obj.lasteditdate=datetime.now()
            _obj.save()
            data['form_is_valid'] = True
            data['id'] = pk
            data['status'] = _('Closed')
            data['icon'] = "c_%s" %pk
            data['message'] = _(' Close Date Updated successfully for Task number %s ' %pk)
            data['html_form'] = render_to_string('project/task/update_close_task.html',request=request)
            return JsonResponse(data)
        else:
            data['form_is_valid'] = False

    # if a GET (or any other method) we'll create a blank form
    context = {'form': TaskCloseForm(),'pk':pk,'errors':errors}
    data['html_form'] = render_to_string('project/task/update_close_task.html',context,request=request)
    return JsonResponse(data)

def ganttChart(request,pk):

    context={}
    return render(request, 'project/project_ganttchart.html', context)


#Delegation for timesheet#
@login_required
def adddelegation(request):
    form = AddDelegation
    if request.method=='POST':
        auth_employee = request.POST.get('employee', False)
        print ('is Post')
        form = form(request.POST)
        if form.is_valid():
            print ('is valid')
            obj = form.save(commit = False)
            obj.authorized = get_object_or_404(Employee,empid__exact=auth_employee)
            obj.managerid =  get_object_or_404(Employee,empid__exact=request.session.get('EmpID'))
            obj.deptcode = get_object_or_404(Department,deptcode__exact=obj.managerid.deptcode)
            aut_data = get_object_or_404(Employee,empid__exact=auth_employee)
            obj.deptauthcode = aut_data.deptcode
            obj.expired = '0'
            obj.save()
            messages.success(request, _("Add complete"))
            return HttpResponseRedirect(reverse('ns-project:delegation'))
    else:
        form = form
    context = {"form":form}
    return render(request, 'project/add_delegation.html', context)

@login_required
def editdelegation(request,pk):
    EmpID = request.session.get('EmpID')
    record = get_object_or_404(Delegation, pk=pk)
    form = AddDelegation
    if EmpID == record.managerid.empid:
        form = form(request.POST or None, instance=record)
        form.fields["employee"].initial=record.authorized.empid
        if request.method=='POST':
            auth_employee = request.POST.get('employee', False)
            print ('is Post')
            if form.is_valid():
                print ('is valid')
                obj = form.save(commit = False)
                obj.authorized = get_object_or_404(Employee,empid__exact=auth_employee)
                obj.managerid =  get_object_or_404(Employee,empid__exact=request.session.get('EmpID'))
                obj.deptcode = get_object_or_404(Department,deptcode__exact=obj.managerid.deptcode)
                aut_data = get_object_or_404(Employee,empid__exact=auth_employee)
                obj.deptauthcode = aut_data.deptcode
                obj.save()
                messages.success(request, _("Edit complete"))
                return HttpResponseRedirect(reverse('ns-project:delegation'))
        else:
            form = form
    else:
        raise Http404

    context = {"form":form}
    return render(request, 'project/edit_delegation.html', context)

@login_required
def delegation(request):
    if request.user.is_authenticated():
        EmpID = request.session.get('EmpID',0)
    all_delegations = Delegation.objects.filter(managerid = EmpID).order_by('expired')
    count = len(list(all_delegations))
    if count == 0:
        messages.info(request, _("No Delegations"))
    context = {'AllDelegations': all_delegations,'count':count}
    return render(request, 'project/delegation.html', context)

@login_required
def mydelegation(request):
    if request.user.is_authenticated():
        EmpID = request.session.get('EmpID',0)
    all_delegations = Delegation.objects.filter(authorized = EmpID, expired = '0')

    count = len(list(all_delegations))
    if count == 0:
        messages.info(request, _("No Delegations"))
    context = {'AllDelegations': all_delegations,'count':count}
    return render(request, 'project/my_delegation.html', context)
