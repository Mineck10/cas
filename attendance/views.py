from unicodedata import category
from aiohttp import request
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
import json
from datetime import datetime
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse

from ams.settings import MEDIA_ROOT, MEDIA_URL
from rest_framework.response import Response
from rest_framework import status
from attendance.serializers import RaspberryPiDataSerializer
from attendance.models import Attendance, UserProfile, Program, Department, Course, Student, ClassStudent, PI_Data, Semester

from attendance.forms import UserRegistration, UpdateProfile, UpdateProfileMeta, UpdateProfileAvatar, AddAvatar, SaveDepartment, SaveProgram, SaveClass, SaveStudent, SaveClassStudent, UpdatePasswords, UpdateFaculty

deparment_list = Department.objects.exclude(status = 2).all()
context = {
    'page_title' : 'Simple Blog Site',
    'deparment_list' : deparment_list,
    'deparment_list_limited' : deparment_list[:3]
}
#login
def login_user(request):
    logout(request)
    resp = {"status":'failed','msg':''}
    username = ''
    password = ''
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                resp['status']='success'
            else:
                resp['msg'] = "Incorrect username or password"
        else:
            resp['msg'] = "Incorrect username or password"
    return HttpResponse(json.dumps(resp),content_type='application/json')

#Logout
def logoutuser(request):
    logout(request)
    return redirect('/')

@login_required
def home(request):
    context['page_title'] = 'Home'
    departments = Department.objects.count()
    programs = Program.objects.count()
    lecturer = UserProfile.objects.filter(user_type = 2).count()
    if request.user.profile.user_type == 1:
        students = Student.objects.count()
        classes = Course.objects.count()
    else:
        classes = Course.objects.filter(assigned_lecturer = request.user.profile).count()
        students = ClassStudent.objects.filter(classIns__in = Course.objects.filter(assigned_lecturer = request.user.profile).values_list('id')).count()
    context['departments'] = departments
    context['programs'] = programs
    context['lecturers'] = lecturer
    context['students'] = students
    context['courses'] = classes

    # context['posts'] = posts
    return render(request, 'home.html',context)

def registerUser(request):
    user = request.user
    if user.is_authenticated:
        return redirect('home-page')
    context['page_title'] = "Register User"
    if request.method == 'POST':
        data = request.POST
        form = UserRegistration(data)
        if form.is_valid():
            form.save()
            newUser = User.objects.all().last()
            try:
                profile = UserProfile.objects.get(user = newUser)
            except:
                profile = None
            if profile is None:
                UserProfile(user = newUser, dob = data['dob'], contact = data['contact'], avatar = request.FILES['avatar']).save()
            else:
                UserProfile.objects.filter(id = profile.id).update(user = newUser, dob= data['dob'], contact= data['contact'])
                avatar = AddAvatar(request.POST,request.FILES, instance = profile)
                if avatar.is_valid():
                    avatar.save()
            username = form.cleaned_data.get('username')
            pwd = form.cleaned_data.get('password1')
            loginUser = authenticate(username= username, password = pwd)
            login(request, loginUser)
            return redirect('home-page')
        else:
            context['reg_form'] = form

    return render(request,'register.html',context)

@login_required
def profile(request):
    context = {
        'page_title':"My Profile"
    }

    return render(request,'profile.html',context)
    
@login_required
def update_profile(request):
    context['page_title'] = "Update Profile"
    user = User.objects.get(id= request.user.id)
    profile = UserProfile.objects.get(user= user)
    context['userData'] = user
    context['userProfile'] = profile
    if request.method == 'POST':
        data = request.POST
        # if data['password1'] == '':
        # data['password1'] = '123'
        form = UpdateProfile(data, instance=user)
        if form.is_valid():
            form.save()
            form2 = UpdateProfileMeta(data, instance=profile)
            if form2.is_valid():
                form2.save()
                messages.success(request,"Your Profile has been updated successfully")
                return redirect("profile")
            else:
                # form = UpdateProfile(instance=user)
                context['form2'] = form2
        else:
            context['form1'] = form
            form = UpdateProfile(instance=request.user)
    return render(request,'update_profile.html',context)


@login_required
def update_avatar(request):
    context['page_title'] = "Update Avatar"
    user = User.objects.get(id= request.user.id)
    context['userData'] = user
    context['userProfile'] = user.profile
    if user.profile.avatar:
        img = user.profile.avatar.url
    else:
        img = MEDIA_URL+"/default/default-avatar.png"

    context['img'] = img
    if request.method == 'POST':
        form = UpdateProfileAvatar(request.POST, request.FILES,instance=user)
        if form.is_valid():
            form.save()
            messages.success(request,"Your Profile has been updated successfully")
            return redirect("profile")
        else:
            context['form'] = form
            form = UpdateProfileAvatar(instance=user)
    return render(request,'update_avatar.html',context)

@login_required
def update_password(request):
    context['page_title'] = "Update Password"
    if request.method == 'POST':
        form = UpdatePasswords(user = request.user, data= request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Your Account Password has been updated successfully")
            update_session_auth_hash(request, form.user)
            return redirect("profile")
        else:
            context['form'] = form
    else:
        form = UpdatePasswords(request.POST)
        context['form'] = form
    return render(request,'update_password.html',context)

#Department
@login_required
def department(request):
    departments = Department.objects.all()
    context['page_title'] = "Department Management"
    context['departments'] = departments
    return render(request, 'department_mgt.html',context)

@login_required
def manage_department(request,pk=None):
    # department = department.objects.all()
    if pk == None:
        department = {}
    elif pk > 0:
        department = Department.objects.filter(id=pk).first()
    else:
        department = {}
    context['page_title'] = "Manage Department"
    context['department'] = department

    return render(request, 'manage_department.html',context)

@login_required
def save_department(request):
    resp = { 'status':'failed' , 'msg' : '' }
    if request.method == 'POST':
        department = None
        print(not request.POST['id'] == '')
        if not request.POST['id'] == '':
            department = Department.objects.filter(id=request.POST['id']).first()
        if not department == None:
            form = SaveDepartment(request.POST,instance = department)
        else:
            form = SaveDepartment(request.POST)
    if form.is_valid():
        form.save()
        resp['status'] = 'success'
        messages.success(request, 'Department has been saved successfully')
    else:
        for field in form:
            for error in field.errors:
                resp['msg'] += str(error + '<br>')
        if not department == None:
            form = SaveDepartment(instance = department)
       
    return HttpResponse(json.dumps(resp),content_type="application/json")

@login_required
def delete_department(request):
    resp={'status' : 'failed', 'msg':''}
    if request.method == 'POST':
        id = request.POST['id']
        try:
            department = Department.objects.filter(id = id).first()
            department.delete()
            resp['status'] = 'success'
            messages.success(request,'Department has been deleted successfully.')
        except Exception as e:
            raise print(e)
    return HttpResponse(json.dumps(resp),content_type="application/json")


#Program
@login_required
def program(request):
    programs = Program.objects.all()
    context['page_title'] = "Program Management"
    context['programs'] = programs
    return render(request, 'program_mgt.html',context)

@login_required
def manage_program(request,pk=None):
    if pk == None:
        program = {}
        department = Department.objects.filter(status=1).all()
    elif pk > 0:
        program = Program.objects.filter(id=pk).first()
        department = Department.objects.filter(Q(status=1) or Q(id = program.id)).all()
    else:
        department = Department.objects.filter(status=1).all()
        program = {}
    context['page_title'] = "Manage Program"
    context['departments'] = department
    context['program'] = program

    return render(request, 'manage_program.html',context)

@login_required
def save_program(request):
    resp = { 'status':'failed' , 'msg' : '' }
    if request.method == 'POST':
        program = None
        print(not request.POST['id'] == '')
        if not request.POST['id'] == '':
            program = Program.objects.filter(id=request.POST['id']).first()
        if not program == None:
            form = SaveProgram(request.POST,instance = program)
        else:
            form = SaveProgram(request.POST)
    if form.is_valid():
        form.save()
        resp['status'] = 'success'
        messages.success(request, 'Program has been saved successfully')
    else:
        for field in form:
            for error in field.errors:
                resp['msg'] += str(error + '<br>')
        if not program == None:
            form = SaveProgram(instance = program)
       
    return HttpResponse(json.dumps(resp),content_type="application/json")

@login_required
def delete_program(request):
    resp={'status' : 'failed', 'msg':''}
    if request.method == 'POST':
        id = request.POST['id']
        try:
            program = Program.objects.filter(id = id).first()
            program.delete()
            resp['status'] = 'success'
            messages.success(request,'Program has been deleted successfully.')
        except Exception as e:
            raise print(e)
    return HttpResponse(json.dumps(resp),content_type="application/json")

#Faculty
@login_required
def faculty(request):
    user = UserProfile.objects.filter(user_type = 2).all()
    context['page_title'] = "Faculty Management"
    context['faculties'] = user
    return render(request, 'faculty_mgt.html',context)

@login_required
def manage_faculty(request,pk=None):
    if pk == None:
        faculty = {}
        department = Department.objects.filter(status=1).all()
    elif pk > 0:
        faculty = UserProfile.objects.filter(id=pk).first()
        department = Department.objects.filter(Q(status=1) or Q(id = faculty.id)).all()
    else:
        department = Department.objects.filter(status=1).all()
        faculty = {}
    #lec_username = User.objects.filter(status= 1).values_list('username', flat=True)
    #pi_username = PI_Data.objects.values_list('registration_number', 'fingerprint', flat=True)
    matching_data = PI_Data.objects.filter(registration_number__in = User.objects.filter(is_superuser=False).values('username')).values('registration_number', 'fingerprint')
    for data in matching_data:
        registration_number = data['registration_number']
        fingerprint = data['fingerprint']
        matching_found = False
        user = User.objects.filter(username=registration_number).first()   
        if user:
            # A match is found between registration_number and username
            # Update radiobutton appearance or perform other actions
            matching_found = True
            break
        else:
            # No match is found
            matching_found = False
        context['fingerprint'] = matching_found

    context['page_title'] = "Manage Faculty"
    context['departments'] = department
    context['faculty'] = faculty
    context['courses'] = Course.objects.all()
    return render(request, 'manage_faculty.html',context)

@login_required
def view_faculty(request,pk=None):
    if pk == None:
        faculty = {}
    elif pk > 0:
        faculty = UserProfile.objects.filter(id=pk).first()
    else:
        faculty = {}
    context['page_title'] = "Manage Faculty"
    context['faculty'] = faculty
    return render(request, 'faculty_details.html',context)

@login_required
def save_faculty(request):
    resp = { 'status' : 'failed', 'msg' : '' }
    if request.method == 'POST':
        data = request.POST
        if data['id'].isnumeric() and data['id'] != '':
            user = User.objects.get(id = data['id'])
        else:
            user = None
        if not user == None:
            form = UpdateFaculty(data = data, user = user, instance = user)
        else:
            form = UserRegistration(data)
        if form.is_valid():
            form.save()

            if user == None:
                user = User.objects.all().last()
            try:
                profile = UserProfile.objects.get(user = user)
            except:
                profile = None
            if profile is None:
                form2 = UpdateProfileMeta(request.POST,request.FILES)
            else:
                form2 = UpdateProfileMeta(request.POST,request.FILES, instance = profile)
                if form2.is_valid():
                    form2.save()
                    resp['status'] = 'success'
                    messages.success(request,'Lecturer data has been save successfully.')
                else:
                    User.objects.filter(id=user.id).delete()
                    for field in form2:
                        for error in field.errors:
                            resp['msg'] += str(error + '<br>')
            
        else:
            for field in form:
                for error in field.errors:
                    resp['msg'] += str(error + '<br>')

    return HttpResponse(json.dumps(resp),content_type='application/json')

@login_required
def delete_faculty(request):
    resp={'status' : 'failed', 'msg':''}
    if request.method == 'POST':
        id = request.POST['id']
        try:
            faculty = User.objects.filter(id = id).first()
            faculty.delete()
            resp['status'] = 'success'
            messages.success(request,'Lecturer data has been deleted successfully.')
        except Exception as e:
            raise print(e)
    return HttpResponse(json.dumps(resp),content_type="application/json")


    
#Class
@login_required
def classPage(request):
    if request.user.profile.user_type == 1:
        course = Course.objects.all()
    else:
        course = Course.objects.filter(assigned_lecturer=request.user.profile, department__name=Department.name, semester=Semester.semester).all()
    context['page_title'] = "Course Management"
    context['course'] = course
    return render(request, 'class_mgt.html',context)

@login_required
def manage_class(request,pk=None):
    lecturers = UserProfile.objects.filter(user_type= 2, department__name=Department.name).all()
    departments = Department.objects.filter(status=1).all()
    if pk == None:
        courses = {}
    elif pk > 0:
        courses = Course.objects.filter(id=pk).first()
    else:
        courses = {}
    context['page_title'] = "Manage Course"
    context['lecturers'] = lecturers
    context['courses'] = courses
    context['department'] = departments

    #if else loop can be deleted, we only need department names

    return render(request, 'manage_class.html',context)

@login_required
def view_class(request, pk= None):
    if pk is None:
        return redirect('home-page')
    else:
        _class = Course.objects.filter(id=pk).first()
        students = ClassStudent.objects.filter(classIns = _class).all()
        context['class'] = _class
        context['students'] = students
        context['page_title'] = "Class Information"
    return render(request, 'class_details.html',context)


@login_required
def save_class(request):
    resp = { 'status':'failed' , 'msg' : '' }
    if request.method == 'POST':
        _class = None
        print(not request.POST['id'] == '')
        if not request.POST['id'] == '':
            _class = Course.objects.filter(id=request.POST['id']).first()
        if not _class == None:
            form = SaveClass(request.POST,instance = _class)
        else:
            form = SaveClass(request.POST)
    if form.is_valid():
        form.save()
        resp['status'] = 'success'
        messages.success(request, 'Class has been saved successfully')
    else:
        for field in form:
            for error in field.errors:
                resp['msg'] += str(error + '<br>')
        if not _class == None:
            form = SaveClass(instance = _class)
       
    return HttpResponse(json.dumps(resp),content_type="application/json")

@login_required
def delete_class(request):
    resp={'status' : 'failed', 'msg':''}
    if request.method == 'POST':
        id = request.POST['id']
        try:
            _class = Course.objects.filter(id = id).first()
            _class.delete()
            resp['status'] = 'success'
            messages.success(request,'Class has been deleted successfully.')
        except Exception as e:
            raise print(e)
    return HttpResponse(json.dumps(resp),content_type="application/json")

@login_required
def manage_class_student(request,classPK = None):
    if classPK is None:
        return HttpResponse('Class ID is Unknown')
    else:
        context['classPK'] = classPK
        _class  = Course.objects.get(id = classPK)
        # print(ClassStudent.objects.filter(classIns = _class))
        students = Student.objects.exclude(id__in = ClassStudent.objects.filter(classIns = _class).values_list('student').distinct()).all()
        context['students'] = students
        return render(request, 'manage_class_student.html',context)
@login_required
def save_class_student(request):
    resp = {'status' : 'failed', 'msg':''}
    if request.method == 'POST':
        form = SaveClassStudent(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Student has been added successfully.")
            resp['status'] = 'success'
        else:
            for field in form:
                for error in field.errors:
                    resp['msg'] += str(error+"<br>")
    return HttpResponse(json.dumps(resp),content_type = 'json')

@login_required
def delete_class_student(request):
    resp={'status' : 'failed', 'msg':''}
    if request.method == 'POST':
        id = request.POST['id']
        try:
            cs = ClassStudent.objects.filter(id = id).first()
            cs.delete()
            resp['status'] = 'success'
            messages.success(request,'Student has been deleted from Class successfully.')
        except Exception as e:
            raise print(e)
    return HttpResponse(json.dumps(resp),content_type="application/json")


#Student
@login_required
def student(request):
    students = Student.objects.all()
    context['page_title'] = "Student Management"
    context['students'] = students
    return render(request, 'student_mgt.html',context)

@login_required
def manage_student(request,pk=None):
    if pk == None:
        student = {}
        program = Program.objects.filter(status=1).all()
    elif pk > 0:
        student = Student.objects.filter(id=pk).first()
        program = Program.objects.filter(Q(status=1) or Q(id = program.id)).all()
    else:
        program = Program.objects.filter(status=1).all()
        student = {}
    context['page_title'] = "Manage Program"
    context['courses'] = program
    context['student'] = student

    return render(request, 'manage_student.html',context)
@login_required
def view_student(request,pk=None):
    if pk == None:
        student = {}
    elif pk > 0:
        student = Student.objects.filter(id=pk).first()
    else:
        student = {}
    context['student'] = student
    return render(request, 'student_details.html',context)

@login_required
def save_student(request):
    resp = { 'status':'failed' , 'msg' : '' }
    if request.method == 'POST':
        student = None
        print(not request.POST['id'] == '')
        if not request.POST['id'] == '':
            student = Student.objects.filter(id=request.POST['id']).first()
        if not student == None:
            form = SaveStudent(request.POST,instance = student)
        else:
            form = SaveStudent(request.POST)
    if form.is_valid():
        form.save()
        resp['status'] = 'success'
        messages.success(request, 'Student Details has been saved successfully')
    else:
        for field in form:
            for error in field.errors:
                resp['msg'] += str(error + '<br>')
        if not program == None:
            form = SaveStudent(instance = program)
       
    return HttpResponse(json.dumps(resp),content_type="application/json")

@login_required
def delete_student(request):
    resp={'status' : 'failed', 'msg':''}
    if request.method == 'POST':
        id = request.POST['id']
        try:
            student = Student.objects.filter(id = id).first()
            student.delete()
            resp['status'] = 'success'
            messages.success(request,'Student Details has been deleted successfully.')
        except Exception as e:
            raise print(e)
    return HttpResponse(json.dumps(resp),content_type="application/json")

#Attendance
@login_required
def attendance_class(request):
    if request.user.profile.user_type == 1:
        courses = Course.objects.all()
    else:
        courses = Course.objects.filter(assigned_lecturer = request.user.profile).all()
    context['page_title'] = "Attendance Management"
    context['courses'] = courses
    return render(request, 'attendance_class.html',context)


@login_required
def attendance(request,classPK = None, date=None):
    _class = Course.objects.get(id = classPK)
    students = Student.objects.filter(id__in = ClassStudent.objects.filter(classIns = _class).values_list('student')).all()
    context['page_title'] = "Attendance Management"
    context['class'] = _class
    context['date'] = date
    att_data = {}
    for student in students:
        att_data[student.id] = {}
        att_data[student.id]['data'] = student
    if not date is None:
        date = datetime.strptime(date, '%Y-%m-%d')
        year = date.strftime('%Y')
        month = date.strftime('%m')
        day = date.strftime('%d')
        attendance = Attendance.objects.filter(attendance_date__year = year, attendance_date__month = month, attendance_date__day = day, classIns = _class).all()
        for att in attendance:
            att_data[att.student.pk]['type'] = att.type
    print(list(att_data.values()))
    context['att_data'] = list(att_data.values())
    context['students'] = students

    return render(request, 'attendance_mgt.html',context)

@login_required
def save_attendance(request):
    resp = {'status' : 'failed', 'msg':''}
    if request.method == 'POST':
        post = request.POST
        date = datetime.strptime(post['attendance_date'], '%Y-%m-%d')
        year = date.strftime('%Y')
        month = date.strftime('%m')
        day = date.strftime('%d')
        _class = Course.objects.get(id=post['classIns'])
        Attendance.objects.filter(attendance_date__year = year, attendance_date__month = month, attendance_date__day = day,classIns = _class).delete()
        for student in post.getlist('student[]'):
            type = post['type['+student+']']
            studInstance = Student.objects.get(id = student)
            att = Attendance(student=studInstance,type = type,classIns = _class,attendance_date=post['attendance_date']).save()
        resp['status'] = 'success'
        messages.success(request,"Attendance has been saved successfully.")
    return HttpResponse(json.dumps(resp),content_type="application/json")


def data_from_PI(request):
    if request.method == 'POST':
        # Get the data from the request
        student_data = request.POST
        
        # Process the data and save it to the database
        # ...
        
        # Return a JSON response indicating success
        return JsonResponse({'message': 'Student data saved successfully'})
    else:
        # Return a JSON response indicating an error
        return JsonResponse({'error': 'Invalid request method'})
