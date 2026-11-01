from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, MockTest, Question, StudentAnswer, Evaluation

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    user_type = forms.ChoiceField(choices=UserProfile.USER_TYPES, label="Aapka Role (Teacher/Student)")
    
    # Naya field student class ke liye
    student_class = forms.ChoiceField(
        choices=[
            ('', '-- Apni Class Chunein (Agar Student hain) --'),
            ('6th', 'Class 6th'), ('7th', 'Class 7th'), ('8th', 'Class 8th'),
            ('9th', 'Class 9th'), ('10th', 'Class 10th'), ('11th', 'Class 11th'), ('12th', 'Class 12th')
        ],
        required=False,
        label="Class (Sirf Students ke liye)"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']


class MockTestForm(forms.ModelForm):
    class Meta:
        model = MockTest
        fields = ['title', 'subject']

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text', 'question_type', 'max_marks']