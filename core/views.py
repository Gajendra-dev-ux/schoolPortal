from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import UserRegistrationForm
from .models import UserProfile, Notice, MockTest, SchoolEvent, EventPhoto, Evaluation, Question, StudentAnswer

# Home / Landing Page
def home_view(request):
    notices = Notice.objects.all().order_by('-date_posted')[:5]
    events = SchoolEvent.objects.all().order_by('-date')[:3]
    return render(request, 'core/home.html', {'notices': notices, 'events': events})

# Registration View
def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            # UserProfile banate waqt student_class bhi save karna
            u_type = form.cleaned_data['user_type']
            s_class = form.cleaned_data.get('student_class') if u_type == 'student' else ''
            
            UserProfile.objects.create(
                user=user, 
                user_type=u_type,
                student_class=s_class
            )
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'core/register.html', {'form': form})

# Role-based Dashboard Redirection View
@login_required
def dashboard_view(request):
    profile = UserProfile.objects.get(user=request.user)
    if profile.user_type == 'teacher':
        # Teacher ke dashboard par ab classes ki list dikhayenge (e.g., 6th to 12th)
        classes = ['6th', '7th', '8th', '9th', '10th', '11th', '12th']
        return render(request, 'core/teacher_dashboard.html', {'classes': classes})
    else:
        student_class = profile.student_class or '9th'
        subjects = MockTest.objects.filter(school_class=student_class).values_list('subject', flat=True).distinct()
        return render(request, 'core/student_dashboard.html', {'subjects': subjects, 'student_class': student_class})

@login_required
def subject_tests(request, subject_name):
    profile = UserProfile.objects.get(user=request.user)
    if profile.user_type == 'teacher':
        return redirect('dashboard')
        
    student_class = profile.student_class or '9th'
    
    # 1. Is subject aur class ke test ids jo student ne attempt kar liye hain
    attempted_test_ids = StudentAnswer.objects.filter(student=request.user, question__test__subject=subject_name).values_list('question__test', flat=True).distinct()
    
    # 2. Attempted tests list
    attempted_tests = MockTest.objects.filter(school_class=student_class, subject=subject_name, id__in=attempted_test_ids).order_by('-created_at')
    
    # 3. Available (Uplabdha) tests list (exclude attempted)
    available_tests = MockTest.objects.filter(school_class=student_class, subject=subject_name).exclude(id__in=attempted_test_ids).order_by('-created_at')
    
    return render(request, 'core/subject_tests.html', {
        'subject_name': subject_name,
        'available_tests': available_tests,
        'attempted_tests': attempted_tests
    })

@login_required
def view_solution(request, test_id):
    test = get_object_or_404(MockTest, id=test_id)
    questions = test.questions.all()
    
    saved_answers_data = []
    obtained_score = 0
    total_score = 0
    correct_count = 0
    incorrect_count = 0
    
    for q in questions:
        total_score += q.max_marks
        latest_ans = StudentAnswer.objects.filter(student=request.user, question=q).order_by('-submitted_at').first()
        
        evaluation = None
        if latest_ans:
            if q.question_type == 'mcq':
                if latest_ans.is_correct:
                    obtained_score += q.max_marks
                    correct_count += 1
                else:
                    incorrect_count += 1
            else:
                evaluation = Evaluation.objects.filter(student_answer=latest_ans).first()
                if evaluation:
                    obtained_score += evaluation.obtained_marks
                    
            saved_answers_data.append({
                'answer': latest_ans,
                'evaluation': evaluation
            })

    return render(request, 'core/view_solution.html', {
        'test': test,
        'saved_answers_data': saved_answers_data,
        'obtained_score': obtained_score,
        'total_score': total_score,
        'correct_count': correct_count,
        'incorrect_count': incorrect_count
    })


# 1. Notice Create karne ka View (Sirf Teacher ke liye)
@login_required
def add_notice(request):
    profile = UserProfile.objects.get(user=request.user)
    # Sirf Admin (superuser) ya jise teacher ko permission di gayi ho
    if profile.user_type != 'teacher' or (not request.user.is_superuser and not profile.can_publish):
        return redirect('dashboard')
        
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        image = request.FILES.get('image') # Optional notice image
        
        Notice.objects.create(title=title, content=content, image=image)
        return redirect('home')
        
    return render(request, 'core/add_notice.html')

# 2. School Gallery View (Sabhi ke liye)
def gallery_view(request):
    events = SchoolEvent.objects.all().order_by('-date')
    return render(request, 'core/gallery.html', {'events': events})

# 3. Gallery Event aur Photos Add karne ka View (Sirf Teacher ke liye)
@login_required
def add_event(request):
    profile = UserProfile.objects.get(user=request.user)
    if profile.user_type != 'teacher' or (not request.user.is_superuser and not profile.can_publish):
        return redirect('dashboard')
        
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        date = request.POST.get('date')
        
        event = SchoolEvent.objects.create(title=title, description=description, date=date)
        
        # Multiple Photos loop handling
        images = request.FILES.getlist('photos')
        for img in images:
            EventPhoto.objects.create(event=event, image=img)
            
        return redirect('gallery')
        
    return render(request, 'core/add_event.html')


# 1. Teacher dwara Mock Test banane ka view
@login_required
def create_mock_test(request):
    profile = UserProfile.objects.get(user=request.user)
    if profile.user_type != 'teacher':
        return redirect('dashboard')
        
    if request.method == 'POST':
        title = request.POST.get('title')
        school_class = request.POST.get('school_class')
        subject = request.POST.get('subject')
        
        test = MockTest.objects.create(title=title, school_class=school_class, subject=subject)
        
        # Multiple Questions loop (Dynamic handling)
        q_texts = request.POST.getlist('question_text')
        q_types = request.POST.getlist('question_type')
        max_marks = request.POST.getlist('max_marks')
        
        opt_as = request.POST.getlist('option_a')
        opt_bs = request.POST.getlist('option_b')
        opt_cs = request.POST.getlist('option_c')
        opt_ds = request.POST.getlist('option_d')
        correct_opts = request.POST.getlist('correct_option')
        
        for i in range(len(q_texts)):
            q_type = q_types[i]
            Question.objects.create(
                test=test,
                question_text=q_texts[i],
                question_type=q_type,
                max_marks=max_marks[i],
                option_a=opt_as[i] if q_type == 'mcq' else '',
                option_b=opt_bs[i] if q_type == 'mcq' else '',
                option_c=opt_cs[i] if q_type == 'mcq' else '',
                option_d=opt_ds[i] if q_type == 'mcq' else '',
                correct_option=correct_opts[i] if q_type == 'mcq' else ''
            )
        return redirect('dashboard')
        
    return render(request, 'core/create_mock_test.html')

# 2. Student dwara Test attend karke Answer (Text + Photo) submit karne ka view
@login_required
def take_test(request, test_id):
    test = get_object_or_404(MockTest, id=test_id)
    questions = test.questions.all()
    
    if request.method == 'POST':
        total_score = 0
        obtained_score = 0
        correct_count = 0
        incorrect_count = 0
        
        # Student ke is test ke purane answers delete kar sakte hain agar reattempt kar raha hai
        StudentAnswer.objects.filter(student=request.user, question__test=test).delete()
        
        saved_answers = []
        for question in questions:
            total_score += question.max_marks
            if question.question_type == 'mcq':
                selected_opt = request.POST.get(f'question_{question.id}')
                is_right = (selected_opt and selected_opt.strip().upper() == question.correct_option.strip().upper())
                
                if is_right:
                    obtained_score += question.max_marks
                    correct_count += 1
                else:
                    incorrect_count += 1
                    
                ans_obj = StudentAnswer.objects.create(
                    student=request.user,
                    question=question,
                    selected_option=selected_opt,
                    is_correct=is_right
                )
                saved_answers.append(ans_obj)
            else:
                ans_text = request.POST.get(f'answer_text_{question.id}')
                ans_image = request.FILES.get(f'answer_image_{question.id}')
                ans_obj = StudentAnswer.objects.create(
                    student=request.user,
                    question=question,
                    answer_text=ans_text,
                    answer_image=ans_image,
                    is_correct=False
                )
                saved_answers.append(ans_obj)
        
        # Result page par correct solutions ke sath redirect karna
        return render(request, 'core/test_result.html', {
            'test': test,
            'obtained_score': obtained_score,
            'total_score': total_score,
            'correct_count': correct_count,
            'incorrect_count': incorrect_count,
            'saved_answers': saved_answers
        })
        
    return render(request, 'core/take_test.html', {'test': test, 'questions': questions})

# 3. Teacher dwara Manual Checking (Evaluation) karne ka view
@login_required
def evaluate_answers(request, test_id):
    profile = UserProfile.objects.get(user=request.user)
    if profile.user_type != 'teacher':
        return redirect('dashboard')
        
    test = get_object_or_404(MockTest, id=test_id)
    # Is test ke sabhi students ke answers jo check hone baaki hain
    answers = StudentAnswer.objects.filter(question__test=test)
    
    if request.method == 'POST':
        for ans in answers:
            marks = request.POST.get(f'marks_{ans.id}')
            remarks = request.POST.get(f'remarks_{ans.id}')
            if marks:
                Evaluation.objects.update_or_create(
                    student_answer=ans,
                    defaults={
                        'teacher': request.user,
                        'obtained_marks': float(marks),
                        'teacher_remarks': remarks
                    }
                )
        return redirect('dashboard')
        
    return render(request, 'core/evaluate_answers.html', {'test': test, 'answers': answers})

@login_required
def test_responses(request, test_id):
    profile = UserProfile.objects.get(user=request.user)
    if profile.user_type != 'teacher':
        return redirect('dashboard')
        
    test = get_object_or_404(MockTest, id=test_id)
    # Student-wise grouping ya saare answers fetch karna
    answers = StudentAnswer.objects.filter(question__test=test).order_by('student', 'question')
    
    # Student-wise summary calculate karna teacher ke liye
    students_summary = {}
    for ans in answers:
        s_name = ans.student.username
        if s_name not in students_summary:
            students_summary[s_name] = {'correct': 0, 'incorrect': 0, 'answers': []}
        
        if ans.question.question_type == 'mcq':
            if ans.is_correct:
                students_summary[s_name]['correct'] += 1
            else:
                students_summary[s_name]['incorrect'] += 1
        students_summary[s_name]['answers'].append(ans)
        
    return render(request, 'core/test_responses.html', {'test': test, 'students_summary': students_summary})

@login_required
def teacher_class_tests(request, school_class):
    profile = UserProfile.objects.get(user=request.user)
    if profile.user_type != 'teacher':
        return redirect('dashboard')
        
    # Us particular class ke saare mock tests
    tests = MockTest.objects.filter(school_class=school_class).order_by('-created_at')
    return render(request, 'core/teacher_class_tests.html', {'school_class': school_class, 'tests': tests})

@login_required
def teacher_test_students(request, test_id):
    profile = UserProfile.objects.get(user=request.user)
    if profile.user_type != 'teacher':
        return redirect('dashboard')
        
    test = get_object_or_404(MockTest, id=test_id)
    questions = test.questions.all()
    
    # Is test ke sabhi students jinhone answer diya hai
    students = User.objects.filter(studentanswer__question__test=test).distinct()
    
    students_data = {}
    for student in students:
        total_obtained = 0
        total_max = 0
        
        for q in questions:
            total_max += q.max_marks
            # Har question ke liye student ka latest attempt nikalna
            latest_ans = StudentAnswer.objects.filter(student=student, question=q).order_by('-submitted_at').first()
            
            if latest_ans:
                if q.question_type == 'mcq':
                    if latest_ans.is_correct:
                        total_obtained += q.max_marks
                else:
                    # Subjective ke liye Evaluation (teacher ke diye gaye marks) check karna
                    evaluation = Evaluation.objects.filter(student_answer=latest_ans).first()
                    if evaluation:
                        total_obtained += evaluation.obtained_marks
                        
        students_data[student] = {
            'obtained': total_obtained,
            'max': total_max
        }

    return render(request, 'core/teacher_test_students.html', {
        'test': test,
        'students_data': students_data
    })

@login_required
def teacher_student_response(request, test_id, student_id):
    profile = UserProfile.objects.get(user=request.user)
    if profile.user_type != 'teacher':
        return redirect('dashboard')
        
    test = get_object_or_404(MockTest, id=test_id)
    student = get_object_or_404(User, id=student_id)
    
    # Agar teacher ne form submit kiya hai (Marks aur Remarks save karne ke liye)
    if request.method == 'POST':
        answers = StudentAnswer.objects.filter(student=student, question__test=test)
        for ans in answers:
            marks_str = request.POST.get(f'marks_{ans.id}')
            remarks = request.POST.get(f'remarks_{ans.id}')
            
            if marks_str is not None and marks_str != '':
                try:
                    obtained = float(marks_str)
                    # Evaluation object create ya update karna
                    Evaluation.objects.update_or_create(
                        student_answer=ans,
                        defaults={
                            'teacher': request.user,
                            'obtained_marks': obtained,
                            'teacher_remarks': remarks
                        }
                    )
                except ValueError:
                    pass
        return redirect('teacher_test_students', test_id=test.id)

    # Aakhri attempt ke answers aur unki evaluations nikalna
    questions = test.questions.all()
    saved_answers_data = []
    total_obtained_score = 0
    total_max_score = 0
    
    for q in questions:
        total_max_score += q.max_marks
        latest_ans = StudentAnswer.objects.filter(student=student, question=q).order_by('-submitted_at').first()
        
        if latest_ans:
            # MCQ ka score automatic jude, subjective ka evaluation se aayega
            if q.question_type == 'mcq':
                q_score = q.max_marks if latest_ans.is_correct else 0
                total_obtained_score += q_score
                evaluation = None
            else:
                evaluation = Evaluation.objects.filter(student_answer=latest_ans).first()
                if evaluation:
                    total_obtained_score += evaluation.obtained_marks
            
            saved_answers_data.append({
                'answer': latest_ans,
                'evaluation': evaluation
            })

    return render(request, 'core/teacher_student_response.html', {
        'test': test,
        'student_user': student,
        'saved_answers_data': saved_answers_data,
        'total_obtained_score': total_obtained_score,
        'total_max_score': total_max_score
    })

# 1. Main Gallery View (Sabhi events ki sirf first 4 photos dikhane ke liye)
def gallery_view(request):
    events = SchoolEvent.objects.all().order_by('-date')
    return render(request, 'core/gallery.html', {'events': events})

# 2. Particular Event Detail View (Us event ki saari photos dikhane ke liye)
def event_detail_view(request, event_id):
    event = get_object_or_404(SchoolEvent, id=event_id)
    all_photos = event.photos.all() # Is event ki saari photos
    return render(request, 'core/event_detail.html', {'event': event, 'all_photos': all_photos})