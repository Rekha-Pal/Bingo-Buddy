from django.shortcuts import render,redirect,reverse
from . import forms,models
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from datetime import date, timedelta
from quiz import models as QMODEL
from teacher import models as TMODEL
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
import random


#for showing signup/login button for student
def studentclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'student/studentclick.html')

def student_signup_view(request):
    userForm=forms.StudentUserForm()
    studentForm=forms.StudentForm()
    mydict={'userForm':userForm,'studentForm':studentForm}
    if request.method=='POST':
        userForm=forms.StudentUserForm(request.POST)
        studentForm=forms.StudentForm(request.POST,request.FILES)
        if userForm.is_valid() and studentForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            student=studentForm.save(commit=False)
            student.user=user
            student.save()
            my_student_group = Group.objects.get_or_create(name='STUDENT')
            my_student_group[0].user_set.add(user)
        return HttpResponseRedirect('studentlogin')
    return render(request,'student/studentsignup.html',context=mydict)

def is_student(user):
    return user.groups.filter(name='STUDENT').exists()

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_dashboard_view(request):
    dict={
    
    'total_course':QMODEL.Course.objects.all().count(),
    'total_question':QMODEL.Question.objects.all().count(),
    }
    return render(request,'student/student_dashboard.html',context=dict)

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_exam_view(request):
    courses=QMODEL.Course.objects.all()
    return render(request,'student/student_exam.html',{'courses':courses})

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def take_exam_view(request,pk):
    course=QMODEL.Course.objects.get(id=pk)
    total_questions=QMODEL.Question.objects.all().filter(course=course).count()
    questions=QMODEL.Question.objects.all().filter(course=course)
    total_marks=0
    for q in questions:
        total_marks=total_marks + q.marks
    
    return render(request,'student/take_exam.html',{'course':course,'total_questions':total_questions,'total_marks':total_marks})
"""
@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def start_exam_view(request,pk):
    course=QMODEL.Course.objects.get(id=pk)
    questions=QMODEL.Question.objects.all().filter(course=course)
    if request.method=='POST':
        pass
    response= render(request,'student/start_exam.html',{'course':course,'questions':questions})
    response.set_cookie('course_id',course.id)
    return response
    """


@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def startTest(request,pk):
    course = QMODEL.Course.objects.get(id=pk)
    count = QMODEL.Question.objects.all().filter(course=course).count()
    l = []
    for i in range(1,count):
        quesid = QMODEL.Question.objects.all().filter(course=course)[i].id
        l.append(quesid)
    random.shuffle(l)
    global d
    d = {}
    d['qnos'] = l.copy()
    d['count'] = len(l)
    row1 = []
    for i in range(1,6):
        row1.append(l.pop(0))
    row2 = []
    for i in range(1, 6):
        row2.append(l.pop(0))
    row3 = []
    for i in range(1, 6):
        row3.append(l.pop(0))
    row4 = []
    for i in range(1, 6):
        row4.append(l.pop(0))
    row5 = []
    for i in range(1, 6):
        row5.append(l.pop(0))
    random.shuffle(row1)
    random.shuffle(row2)
    random.shuffle(row3)
    random.shuffle(row4)
    random.shuffle(row5)
    d['tabledata'] = [row1,row2,row3,row4,row5]

    rows = d['tabledata']
    cols = []
    for i in range(5):
        col = []
        for row in rows:
            col.append(row[i] - 1)
        cols.append(col)
    d['columns'] = cols

    diag1 = []
    diag2 = []
    i = 0
    for row in rows:
        diag1.append(row[i])
        diag2.append(row[4 - i])
        i = i + 1
    diags = []
    diags.append(diag1)
    diags.append(diag2)
    d['diagonals'] = diags

    global ques
    ques = []
    return redirect('testPaper',pk)

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def testPaper(request,pk):
    if(d['count']>0):
        course = QMODEL.Course.objects.get(id=pk)
        random.shuffle(d['qnos'])
        qid = d['qnos'].pop()
        d['count'] = d['count']-1
        question = QMODEL.Question.objects.all().filter(course=course).get(id=qid)
        d['ques'] = question
        return render(request,'student/test-paper.html',d)
    else:
        messages.info(request,'Test Ended')
        return render(request,'student/ended.html')

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
@csrf_exempt
def result(request):
    if request.method=="POST":
        v=request.POST['option']
        pk = request.POST['qid']
        q = QMODEL.Question.objects.all().get(id=pk)
        pk = q.course.id
        if v==q.answer:
            ques.append(q.id)
            d['marked'] = ques
            return redirect('letsBingo',pk)
        else:
            messages.info(request,"Sorry, Your answer is not correct")
        d['marked'] = ques
        pk = q.course.id
    return redirect('testPaper',pk)

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def LetsBingo(request,pk):
    rows = d['tabledata']
    for row in rows :
        for r in row :
            if r not in d['marked'] :
                break
        else:
            result = QMODEL.Result()
            student = models.Student.objects.get(user_id=request.user.id)
            course = QMODEL.Course.objects.get(id=pk)
            attempted = 25-int(d['count'])
            correct = len(d['marked'])
            total_marks = float(correct)*(100.0/float(attempted))
            result.marks = total_marks
            result.exam = course
            result.student =student
            result.save()
            return render(request, 'student/win.html',d)

    cols = d['columns']
    for col in cols :
        for c in col :
            if c not in d['marked'] :
                break
        else:
            result = QMODEL.Result()
            student = models.Student.objects.get(user_id=request.user.id)
            course = QMODEL.Course.objects.get(id=pk)
            attempted = 25 - int(d['count'])
            correct = len(d['marked'])
            total_marks = float(correct) * (100.0 / float(attempted))
            result.marks = total_marks
            result.exam = course
            result.student = student
            result.save()
            return render(request, 'student/win.html', d)

    diags = d['diagonals']
    for diag in diags :
        for x in diag :
            if x not in d['marked'] :
                break
        else:
            result = QMODEL.Result()
            student = models.Student.objects.get(user_id=request.user.id)
            course = QMODEL.Course.objects.get(id=pk)
            attempted = 25 - int(d['count'])
            correct = len(d['marked'])
            total_marks = float(correct) * (100.0 / float(attempted))
            result.marks = total_marks
            result.exam = course
            result.student = student
            result.save()
            return render(request, 'student/win.html',d)

    return redirect('testPaper',pk)

"""
@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def calculate_marks_view(request):
    if request.COOKIES.get('course_id') is not None:
        course_id = request.COOKIES.get('course_id')
        course=QMODEL.Course.objects.get(id=course_id)
        
        total_marks=0
        questions=QMODEL.Question.objects.all().filter(course=course)
        for i in range(len(questions)):
            
            selected_ans = request.COOKIES.get(str(i+1))
            actual_answer = questions[i].answer
            if selected_ans == actual_answer:
                total_marks = total_marks + questions[i].marks
        student = models.Student.objects.get(user_id=request.user.id)
        result = QMODEL.Result()
        result.marks=total_marks
        result.exam=course
        result.student=student
        result.save()

        return HttpResponseRedirect('view-result')

"""

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def view_result_view(request):
    courses=QMODEL.Course.objects.all()
    return render(request,'student/view_result.html',{'courses':courses})
    

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def check_marks_view(request,pk):
    course=QMODEL.Course.objects.get(id=pk)
    student = models.Student.objects.get(user_id=request.user.id)
    results= QMODEL.Result.objects.all().filter(exam=course).filter(student=student)
    return render(request,'student/check_marks.html',{'results':results})

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_marks_view(request):
    courses=QMODEL.Course.objects.all()
    return render(request,'student/student_marks.html',{'courses':courses})
