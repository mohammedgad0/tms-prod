from .models import *
from ram.views import get_period
from django.shortcuts import render, render_to_response ,get_object_or_404,redirect
import datetime

# def get_period(date):
#     try:
#         period = PeriodQuestion.objects.get(date_from__lte = date , date_to__gte = date)
#         return period.period_no
#     except:
#         period = 5
#     return period

def period(request):
    date = datetime.datetime.now()
    # date = date + timedelta(days=10)
    period = get_period(date)
    period = 3
    period_obj = PeriodQuestion.objects.get(period_no = period)
    return {'period_obj' : period_obj}
