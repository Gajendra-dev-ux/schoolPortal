from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home_view, name='home'),
    # path('register/', views.register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('password/change/', views.change_password_view, name='change_password'),
    path('password/forgot/', views.forgot_password_view, name='forgot_password'),
    path('dashboard/', views.dashboard_view, name='dashboard'),

    path('notice/add/', views.add_notice, name='add_notice'),
    path('gallery/', views.gallery_view, name='gallery'),
    path('gallery/add/', views.add_event, name='add_event'),

    path('test/create/', views.create_mock_test, name='create_mock_test'),
    path('test/take/<int:test_id>/', views.take_test, name='take_test'),
    # path('test/evaluate/<int:test_id>/', views.evaluate_answers, name='evaluate_answers'),
    path('test/responses/<int:test_id>/', views.test_responses, name='test_responses'), # Yeh line add karni hai
    path('student/subject/<str:subject_name>/', views.subject_tests, name='subject_tests'),
    path('test/solution/<int:test_id>/', views.view_solution, name='view_solution'),
    path('teacher/class/<str:school_class>/', views.teacher_class_tests, name='teacher_class_tests'),
    path('teacher/test/<int:test_id>/students/', views.teacher_test_students, name='teacher_test_students'),
    path('teacher/test/<int:test_id>/student/<int:student_id>/response/', views.teacher_student_response, name='teacher_student_response'),
    path('gallery/', views.gallery_view, name='gallery'),
    path('gallery/event/<int:event_id>/', views.event_detail_view, name='event_detail'),
    path('gallery/add/', views.add_event, name='add_event'),
    path('teacher/test/<int:test_id>/preview/', views.preview_mock_test, name='preview_mock_test'),
    path('teacher/test/<int:test_id>/edit/', views.edit_mock_test, name='edit_mock_test'),
    path('teacher/students/classes/', views.teacher_classes_view, name='teacher_classes'),
    path('teacher/students/class/<str:school_class>/', views.teacher_class_students_view, name='teacher_class_students'),
    path('teacher/student/<int:student_id>/edit/', views.teacher_edit_student_view, name='teacher_edit_student'),
    path('teacher/student/<int:student_id>/delete/', views.teacher_delete_student_view, name='teacher_delete_student'),
]