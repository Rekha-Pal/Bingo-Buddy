from django.shortcuts import render,redirect
from . import forms,models
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required,user_passes_test
from quiz import models as QMODEL
from student.models import Game
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
import random
import json

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
def enter_game(request,pk):
    global cid
    cid = {}
    cid['pk'] = pk
    return render(request,'student/start_game.html')

def game(request):
    if request.method == "POST":
        render(request, 'student/start_game.html')
        username = request.user.username
        option = request.POST.get('option')
        room_code = request.POST.get('room_code')

        if option == '1':
            game = Game.objects.filter(room_code=room_code).first()
            if game is None:
                messages.success(request, "Room code not found")
                return redirect('enter_game',cid['pk'])

            if game.is_over:
                messages.success(request, "Game is over")
                return redirect('enter_game',cid['pk'])

            game.game_opponent = username
            game.save()
            return redirect('start-game/' + room_code + '?username=' + username)
        else:
            game = Game(game_creator=username, room_code=room_code)
            game.save()
            return redirect('start-game/' + room_code + '?username=' + username)

    return redirect('student-exam')

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def startGame(request,room_code):
    course = QMODEL.Course.objects.get(id=cid['pk'])
    context = {}
    context['data'] = json.dumps(
        [
            {
                'question': obj.question,
                'answer': obj.answer,
                'option1': obj.option1,
                'option2': obj.option2,
                'option3': obj.option3,
                'option4': obj.option4
            }
            for obj in QMODEL.Question.objects.all().filter(course=course)
        ]
    )
    context['room_code'] = room_code
    context['username'] = request.GET.get('username')
    print(room_code)
    return render(request, 'student/game.html', context)



