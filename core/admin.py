from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import UserProfile, Notice, SchoolEvent, EventPhoto, MockTest, Question

# Inline UserProfile ko User admin ke sath jodna taaki ek hi page par username aur profile (class/type) dikhe
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'User Profile (Role & Class)'

class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'get_user_type', 'get_student_class', 'is_staff')
    list_filter = ('userprofile__user_type', 'userprofile__student_class', 'is_staff')

    def get_user_type(self, obj):
        return obj.userprofile.user_type if hasattr(obj, 'userprofile') else '-'
    get_user_type.short_description = 'User Type'

    def get_student_class(self, obj):
        return obj.userprofile.student_class if hasattr(obj, 'userprofile') else '-'
    get_student_class.short_description = 'Student Class'

# Default User admin ko unregister karke apna Custom User Admin register karna
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Baaki models ko bhi admin mein register karna
admin.site.register(Notice)
admin.site.register(SchoolEvent)
admin.site.register(MockTest)