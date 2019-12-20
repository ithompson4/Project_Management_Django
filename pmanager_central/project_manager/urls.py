from django.urls import path
from . import views
from django.contrib import admin

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.ProjectList.as_view(), name='dashboard'),
    path('profile/', views.update_profile, name='profile'),
    path('home/', views.home, name='home'),
    path('project/create', views.project_create, name='project-create'),
    path('project/<int:pk>', views.project_details, name='project-detail'),
    path('project/<int:pk>/update/', views.ProjectUpdateView.as_view(), name='project-update'),
    path('project/<int:pk>/update/second', views.ProjectUpdateView2, name='project-update-second'),
    path('project/<int:pk>/delete/', views.ProjectDelete.as_view(), name='project-delete'),
    path('tasks/<project>/', views.TasksList.as_view(), name='tasks-list'),
    path('task/<int:pk>/detail/', views.TaskDetail.as_view(), name='task-detail'),
    path('task/<int:pk>/update/', views.TaskUpdate.as_view(), name='task-update'),
    path('task/<int:pk/delete', views.TaskDelete.as_view(), name='task-delete'),
    path('project/createtask', views.task_create, name='task-create')
]