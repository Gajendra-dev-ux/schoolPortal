from django.contrib.auth.models import User
from django.db import models


# 1. User Profile Model (Yeh tay karne ke liye ki user Teacher hai ya Student)
class UserProfile(models.Model):
    USER_TYPES = (
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=10, choices=USER_TYPES)
    student_class = models.CharField(max_length=10, blank=True, null=True, verbose_name="Student Class")
    
    # Naya field: Kya yeh teacher notice/event add kar sakta hai? (Sirf Admin decide karega)
    can_publish = models.BooleanField(default=False, verbose_name="Can Publish Notice/Events (Admin Controlled)")

    def __str__(self):
        return f"{self.user.username} ({self.user_type})"


# 2. Notice Board Model (School ke notices ke liye)
class Notice(models.Model):
    title = models.CharField(max_length=200, verbose_name="Notice Title")
    content = models.TextField(verbose_name="Notice Vivran")
    image = models.ImageField(upload_to='notice_images/', blank=True, null=True, verbose_name="Optional Notice Image")
    date_posted = models.DateTimeField(auto_now_add=True, verbose_name="Posting Tithi")

    def __str__(self):
        return self.title


# 3. School Gallery Models (Events aur photos ke liye)
class SchoolEvent(models.Model):
    title = models.CharField(max_length=200, verbose_name="Event Naam")
    description = models.TextField(blank=True, null=True, verbose_name="Event Vivran")
    date = models.DateField(verbose_name="Event ki Tithi")

    def __str__(self):
        return self.title


class EventPhoto(models.Model):
    event = models.ForeignKey(SchoolEvent, related_name='photos', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='gallery_photos/', verbose_name="Event Photo")
    caption = models.CharField(max_length=255, blank=True, null=True, verbose_name="Photo Caption")

    def __str__(self):
        return f"Photo for {self.event.title}"


# 4. Mock Test & Questions Model (AI ya Manual tests ke liye)
class MockTest(models.Model):
    CLASS_CHOICES = [
        ('6th', 'Class 6th'), ('7th', 'Class 7th'), ('8th', 'Class 8th'),
        ('9th', 'Class 9th'), ('10th', 'Class 10th'), ('11th', 'Class 11th'), ('12th', 'Class 12th')
    ]
    title = models.CharField(max_length=200, verbose_name="Test Naam")
    school_class = models.CharField(max_length=10, choices=CLASS_CHOICES, verbose_name="Kiske liye Class")
    subject = models.CharField(max_length=100, verbose_name="Subject")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Question(models.Model):
    QUESTION_TYPES = (
        ('mcq', 'MCQ (Multiple Choice)'),
        ('subjective', 'Subjective / Written'),
    )
    test = models.ForeignKey(MockTest, related_name='questions', on_delete=models.CASCADE)
    question_text = models.TextField(verbose_name="Sawaal")
    question_type = models.CharField(max_length=15, choices=QUESTION_TYPES, default='mcq')
    
    # MCQ Options
    option_a = models.CharField(max_length=255, blank=True, null=True, verbose_name="Option A")
    option_b = models.CharField(max_length=255, blank=True, null=True, verbose_name="Option B")
    option_c = models.CharField(max_length=255, blank=True, null=True, verbose_name="Option C")
    option_d = models.CharField(max_length=255, blank=True, null=True, verbose_name="Option D")
    correct_option = models.CharField(max_length=5, blank=True, null=True, verbose_name="Sahi Option (A/B/C/D)")
    
    max_marks = models.IntegerField(default=1, verbose_name="Marks")

    def __str__(self):
        return self.question_text[:50]

# 5. Student Answers Model (Text type ya Photo upload karne ke liye)
# 6. Student Answer Model
class StudentAnswer(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=5, blank=True, null=True, verbose_name="Student ka MCQ Jawab")
    answer_text = models.TextField(blank=True, null=True, verbose_name="Typed Jawab")
    answer_image = models.ImageField(upload_to='student_answers/', blank=True, null=True, verbose_name="Copy Photo Upload")
    is_correct = models.BooleanField(default=False, verbose_name="Kya Sahi hai?") # Naya field
    submitted_at = models.DateTimeField(auto_now_add=True)


# 6. Evaluation Model (Teacher dwara manual checking aur marks dene ke liye)
class Evaluation(models.Model):
  student_answer = models.OneToOneField(
      StudentAnswer, on_delete=models.CASCADE, related_name='evaluation'
  )
  teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
  obtained_marks = models.FloatField(verbose_name='Prapt Ank')
  teacher_remarks = models.TextField(
      blank=True, null=True, verbose_name='Teacher Remarks'
  )
  evaluated_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return (
        f"Evaluation for {self.student_answer.id} - Marks:"
        f" {self.obtained_marks}"
    )