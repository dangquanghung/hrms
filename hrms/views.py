import email
import imp
import json
from django.shortcuts import render, redirect, resolve_url, reverse, get_object_or_404
from django.urls import reverse_lazy
from datetime import datetime
from django.contrib.auth import get_user_model
from .models import Employee, Department, Kin, Attendance, Leave, Recruitment, Payroll, Salary
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView, CreateView, View, DetailView, TemplateView, ListView, UpdateView, DeleteView
from .forms import RegistrationForm, LoginForm, EmployeeForm, KinForm, DepartmentForm, AttendanceForm, LeaveForm, RecruitmentForm, PayrollForm
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from flask import flash, Flask, render_template
from werkzeug.utils import secure_filename
import os
from .models import Recruitment

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__, template_folder='',
            static_folder='.hrms/applicationForm/lib', )


# Create your views here.
class Index(TemplateView):
    template_name = 'hrms/home/home.html'

#   Authentication


class Register (CreateView):
    model = get_user_model()
    form_class = RegistrationForm
    template_name = 'hrms/registrations/register.html'
    success_url = reverse_lazy('hrms:login')


class Login_View(LoginView):
    model = get_user_model()
    form_class = LoginForm
    template_name = 'hrms/registrations/login.html'

    def get_success_url(self):
        url = resolve_url('hrms:dashboard')
        return url


class Logout_View(View):

    def get(self, request):
        logout(self.request)
        return redirect('hrms:login', permanent=True)

 # Main Board


class Dashboard(LoginRequiredMixin, ListView):
    template_name = 'hrms/dashboard/index.html'
    login_url = 'hrms:login'
    model = get_user_model()
    context_object_name = 'qset'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['emp_total'] = Employee.objects.all().count()
        context['dept_total'] = Department.objects.all().count()
        context['admin_count'] = get_user_model().objects.all().count()
        context['workers'] = Employee.objects.order_by('-id')
        return context

# Employee's Controller


class Employee_New(LoginRequiredMixin, CreateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'hrms/employee/create.html'
    login_url = 'hrms:login'
    redirect_field_name = 'redirect:'


class Employee_All(LoginRequiredMixin, ListView):
    template_name = 'hrms/employee/index.html'
    model = Employee
    login_url = 'hrms:login'
    context_object_name = 'employees'
    paginate_by = 5


class Employee_View(LoginRequiredMixin, DetailView):
    queryset = Employee.objects.select_related('department')
    template_name = 'hrms/employee/single.html'
    context_object_name = 'employee'
    login_url = 'hrms:login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            query = Kin.objects.get(employee=self.object.pk)
            context["kin"] = query
            return context
        except ObjectDoesNotExist:
            return context


class Employee_Update(LoginRequiredMixin, UpdateView):
    model = Employee
    template_name = 'hrms/employee/edit.html'
    form_class = EmployeeForm
    login_url = 'hrms:login'


class Employee_Delete(LoginRequiredMixin, DeleteView):
    pass


class Employee_Kin_Add (LoginRequiredMixin, CreateView):
    model = Kin
    form_class = KinForm
    template_name = 'hrms/employee/kin_add.html'
    login_url = 'hrms:login'

    def get_context_data(self):
        context = super().get_context_data()
        if 'id' in self.kwargs:
            emp = Employee.objects.get(pk=self.kwargs['id'])
            context['emp'] = emp
            return context
        else:
            return context


class Employee_Kin_Update(LoginRequiredMixin, UpdateView):
    model = Kin
    form_class = KinForm
    template_name = 'hrms/employee/kin_update.html'
    login_url = 'hrms:login'

    def get_initial(self):
        initial = super(Employee_Kin_Update, self).get_initial()

        if 'id' in self.kwargs:
            emp = Employee.objects.get(pk=self.kwargs['id'])
            initial['employee'] = emp.pk

            return initial

# Department views


class Department_Detail(LoginRequiredMixin, ListView):
    context_object_name = 'employees'
    template_name = 'hrms/department/single.html'
    login_url = 'hrms:login'

    def get_queryset(self):
        queryset = Employee.objects.filter(department=self.kwargs['pk'])
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["dept"] = Department.objects.get(pk=self.kwargs['pk'])
        return context


class Department_New (LoginRequiredMixin, CreateView):
    model = Department
    template_name = 'hrms/department/create.html'
    form_class = DepartmentForm
    login_url = 'hrms:login'


class Department_Update(LoginRequiredMixin, UpdateView):
    model = Department
    template_name = 'hrms/department/edit.html'
    form_class = DepartmentForm
    login_url = 'hrms:login'
    success_url = reverse_lazy('hrms:dashboard')

# Attendance View


class Attendance_New (LoginRequiredMixin, CreateView):
    model = Attendance
    form_class = AttendanceForm
    login_url = 'hrms:login'
    template_name = 'hrms/attendance/create.html'
    success_url = reverse_lazy('hrms:attendance_new')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["today"] = timezone.localdate()
        pstaff = Attendance.objects.filter(
            Q(status='PRESENT') & Q(date=timezone.localdate()))
        context['present_staffers'] = pstaff
        return context


class Attendance_Out(LoginRequiredMixin, View):
    login_url = 'hrms:login'

    def get(self, request, *args, **kwargs):

        user = Attendance.objects.get(Q(staff__id=self.kwargs['pk']) & Q(
            status='PRESENT') & Q(date=timezone.localdate()))
        user.last_out = timezone.localtime()
        user.save()
        return redirect('hrms:attendance_new')


class LeaveNew (LoginRequiredMixin, CreateView, ListView):
    model = Leave
    template_name = 'hrms/leave/create.html'
    form_class = LeaveForm
    login_url = 'hrms:login'
    success_url = reverse_lazy('hrms:leave_new')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["leaves"] = Leave.objects.all()
        return context


# class PayrollView(LoginRequiredMixin, ListView):
#     model = Employee
#     template_name = 'hrms/payroll/index.html'
#     login_url = 'hrms:login'
#     context_object_name = 'stfpay'


# class RecruitmentNew (CreateView):
#     model = Recruitment
#     template_name = 'hrms/recruitment/index.html'
#     form_class = RecruitmentForm
#     success_url = reverse_lazy('hrms:recruitment')

class RecruitmentNew (CreateView):
    model = Recruitment
    template_name = 'hrms/applicationForm/applicationForm.html'
    form_class = RecruitmentForm


class RecruitmentAll(LoginRequiredMixin, ListView):
    model = Recruitment
    login_url = 'hrms:login'
    template_name = 'hrms/recruitment/all.html'
    context_object_name = 'recruit'

class RecruitmentDelete (LoginRequiredMixin, View):
    login_url = 'hrms:login'

    def get(self, request, pk):
        form_app = Recruitment.objects.get(pk=pk)
        form_app.delete()
        return redirect('hrms:recruitmentall', permanent=True)

# class PayrollEmployee(LoginRequiredMixin, ListView):
    # model = Payroll
    # login_url = 'hrms:login'
    # template_name = 'hrms/payroll/create.html'
    # form_class = PayrollForm
    # context_object_name = 'emps'
    # success_url = reverse_lazy('hrms:payroll')

def payroll_create(request, id):
    form_app = Employee.objects.get(pk=id)
    field_name_id = form_app._meta.fields[1].name
    field_name_first_name = form_app._meta.fields[3].name
    field_name_last_name = form_app._meta.fields[4].name

    emp_id = getattr(form_app, field_name_id)
    first_name = getattr(form_app, field_name_first_name)
    last_name = getattr(form_app, field_name_last_name)


    return render(request, 'hrms/payroll/create.html',
                  {
                      'pk': id,
                      'id': emp_id,
                      'first_name': first_name,
                      'last_name': last_name
                  })
@csrf_exempt
def payroll_employee(request, id):

        formOut = dict(request.POST.lists())
        emp_id = id
        month = datetime.now().month
        work_day = formOut['work_day'][0]
        bonus = formOut['bonus'][0]
        insurance = formOut['insurance'][0]
        pay_rate =formOut['pay_rate'][0]

        payroll = Payroll(emp_id=emp_id, month=month,
                                work_day=work_day, bonus=bonus, insurance=insurance, pay_rate=pay_rate)

        payroll.save()
        return render(request, 'hrms/payroll/show.html',
                  {
                  })
        # if 'id' in self.kwargs:
        #     pay = Employee.objects.get(pk=self.kwargs['id'])
            
        #     context['pay'] = pay
        #     return context
        # else:
        #     return context
    
class Pay(LoginRequiredMixin, ListView):
    model = Employee
    template_name = 'hrms/payroll/index.html'
    context_object_name = 'emps'
    login_url = 'hrms:login'

######################################################################
# Algorithm here


def job(request):
    return render(request, 'hrms/recruitment/index.html')


def index(request):
    return render(request, 'hrms/recruitment/java-1.html')


def index2(request):
    return render(request, 'hrms/recruitment/java-2.html')


key = ['Oracle', 'Microsoft SQL', 'Bash', 'Python', 'Go', 'Java', 'HTML/CSS', 'JavaScript', 'jQuery', 'Tableau',
       'Power BI', 'Google Data Studio', 'Tensorflow', 'Keras', 'PyTorch', 'Azuze', 'UI Design', 'Front-End']

thisdict = {
    "1": 0,
    "2": 5,
    "3": 7,
    "4": 10
}

jobdict = {
    "AI Engineer": ['Java', 'Python', 'Tensorflow', 'Keras', 'PyTorch', 'UI Design', 'Front-End'],
    "Data Engineer": ['Python', 'Azure', 'Oracle', 'Microsoft SQL', 'JavaScript', 'jQuery', 'Tableau'],
    "Data Analyst": ['Python', 'Oracle', 'Microsoft SQL', 'Tableau', 'Power BI', 'Google Data Studio', 'jQuery'],
    "Java Developer": ['Java', 'JavaScript', 'UI Design', 'Front-End', 'HTML/CSS', 'Microsoft SQL', 'Azuze'],
    "Software Engineer": ['Java', 'Python', 'Go', 'Azure', 'Tensorflow', 'Keras', 'PyTorch'],
    "Business Operations Manager": ['Microsoft SQL', 'Tableau', 'Power BI', 'Google Data Studio', 'Oracle', 'UI Design', 'Front-End']
}


def applicationForm(request):
    return render(request, 'hrms/applicationForm/applicationForm.html',
                  {
                      'key': key
                  })


def estScore(x, keyword, exp, gradute):
    listContrans = set(x) & set(keyword)
    print('go go: ', x)
    print("anwg  ang:", keyword)
    score = len(listContrans) / 7 * 100
    scoreExp = thisdict[exp[0]]
    print("scoreChoose :", score)
    print("scoreExp :", scoreExp)
    scoreGradute = 0

    if(gradute[0] == "1"):
        scoreGradute += 5
    print("scoreGradute :", scoreGradute)

    # for i in x:
    #     if i in keyword:
    #         score+=1
    score += scoreGradute + scoreExp
    if(score > 100):
        score = 100
    return score


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@csrf_exempt
def formProcess(request):
    if request.method == 'POST':
        # Information handle
        # print(request.form)
        formOut = dict(request.POST.lists())
        keyword = []
        data = formOut['Application for']
        keyword = jobdict[data[0]]
        print(keyword)
        score = estScore(formOut['select-tag'], keyword,
                         formOut['exp'], formOut['graduate'])
        print("score final :", score)

        first_name = formOut['First name'][0]
        family_name = formOut['Family name'][0]
        position = formOut['Application for'][0]
        phone = formOut['Phone'][0]
        email = formOut['Email'][0]
        cv = formOut['MAX_FILE_SIZE'][0]
        if score > 85:
            status = 'Pass!'
        elif score > 70:
            status = 'Waitlist'
        else:
            status = 'Failed'
        # Resume Upload handle
        #

        candidate = Recruitment(first_name=first_name, last_name=family_name,
                                position=position, email=email, phone=phone, score=score, status=status, resume=None)

        candidate.save()
    return render(request, 'hrms/applicationForm/formProcess.html',
                  {
                      'score': score
                  })