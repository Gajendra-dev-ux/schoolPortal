from django.contrib import admin
from .models import UserProfile, Notice, SchoolEvent, EventPhoto, MockTest
# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Notice)
admin.site.register(SchoolEvent)
admin.site.register(EventPhoto)
admin.site.register(MockTest)