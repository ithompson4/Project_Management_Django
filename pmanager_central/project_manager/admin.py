from django.contrib import admin
from project_manager.models import Profile, Organization, Project, Task
# Register your models here.
admin.site.register(Profile)
admin.site.register(Organization)
admin.site.register(Project)
admin.site.register(Task)