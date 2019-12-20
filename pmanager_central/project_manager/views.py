# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, redirect, get_object_or_404
from .forms import UserForm, ProjectsForm, TasksForm, ProfileForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.views.generic import DetailView, View, CreateView, UpdateView, DeleteView, ListView
from django.views.generic.edit import FormView
from .models import Project, Organization, Profile, Task
from django.contrib.auth.decorators import login_required
from django.urls import reverse, reverse_lazy, resolve
from django.utils.decorators import method_decorator
from django.db import transaction
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect
from django.forms import formset_factory, inlineformset_factory

# Create your views here.
def index(request):
	return render(request, 'index.html')
def dashboard(request):
    return render(request, 'dashboard.html')
def home(request):
    return render(request, 'home.html')
def login_user(request):
	if request.method == "POST":
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username=username, password=password)
		if user is not None:
			if user.is_active:
				login(request, user)
				return render(request, 'dashboard.html')
			else:
				return render(request, 'login.html', {'error_message': 'Account is disabled.'})
		else:
			return render(request, 'login.html', {'error_message': 'Invalid login'})
	return render(request, 'dashboard.html')	

#User submits the form filled with data in a POST request
def register(request):
	if request.method == 'POST':
		form = UserForm(request.POST)
		if form.is_valid():
			user= form.save(commit=False)
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')
			first_name = form.cleaned_data.get('first_name')
			last_name = form.cleaned_data.get('last_name')
			user.set_password(password)
			user.save()
			user = authenticate(username=username, password=password)
			login(request, user)
			return render(request,'register_success.html')
	else:
		form = UserForm()
	return render(request, 'register.html', {'form': form})

#Function for updating prfoile, currently not used
@login_required
@transaction.atomic
def update_profile(request):
    form = ProfileForm(instance=request.user)
    context = {}
    context['form'] = form
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, ("Your profile was successfully updated!"))
            return redirect('profile')
        else:
            messages.error(request, ("Please correct the errors"))
    return render(request, 'profile.html', context)

#Views for Projects 
@login_required
@transaction.atomic
def project_create(request):
	TaskInlineFormSet = inlineformset_factory(Project, Task, fields=('task_name', 
            'task_description','task_priority', 'task_performer'), extra=0)
	if request.method == 'POST':
		form = ProjectsForm(request.POST)
		task_form = TasksForm(request.POST)
		if form.is_valid() and task_form.is_valid():
			project = form.save(commit=False)
			projectname = form.cleaned_data.get('projectname')
			projdesc = form.cleaned_data.get('projdesc')
			project_deadline = form.cleaned_data.get('project_deadline')
			latest_proj = Project.objects.create(projectname=projectname, projdesc=projdesc, project_deadline=project_deadline)
			#Task object
			task = task_form.save(commit=False)
			task_name = task_form.cleaned_data.get('task_name')
			task_description = task_form.cleaned_data.get('task_description')
			task_priority = task_form.cleaned_data.get('task_priority')
			task_performer = task_form.cleaned_data.get('task_performer')
			task.project = latest_proj
			task.save()
			return render(request,'project_success.html')
	else:
		form = ProjectsForm()
		task_form = TasksForm()
	return render(request, 'project_create.html', {'form': form, 'task_form': task_form})

def task_create(request):
	TaskInlineFormSet = inlineformset_factory(Project, Task, fields=('task_name', 
            'task_description','task_priority', 'task_performer'), extra=0)
	if request.method == 'POST':
		task_form = TasksForm(request.POST)
		if task_form.is_valid():
			task = task_form.save(commit=False)
			task_name = task_form.cleaned_data.get('task_name')
			task_description = task_form.cleaned_data.get('task_description')
			task_priority = task_form.cleaned_data.get('task_priority')
			task_performer = task_form.cleaned_data.get('task_performer')
			task.save()
			return render(request,'task_success.html')
	else:
		task_form = TasksForm()
	return render(request, 'task_create.html', {'task_form': task_form})

@login_required
def task_detail(request, pk):
	template_name ="task_detail.html"
	obj = get_object_or_404(Project, projectid=pk)
	context = {}
	tasks = Task.objects.filter(project__projectid=pk)
	if obj is not None:
		context['project'] = obj
		context['tasks'] = tasks
	return render(request, template_name, context)
	
class ProjectList(LoginRequiredMixin,ListView):
	model = Project
	context_object_name = 'projects_list'
	template_name = 'dashboard.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['project_list'] = Project.objects.all()
		return context

@login_required
def project_details(request, pk):
	template_name ="project_detail.html"
	obj = get_object_or_404(Project, projectid=pk)
	context = {}
	tasks = Task.objects.filter(project__projectid=pk)
	if obj is not None:
		context['project'] = obj
		context['tasks'] = tasks
	return render(request, template_name, context)
 
class ProjectUpdateView(FormView):
	template_name = "project_update.html"
	#Retrieve Project object from the <pk> value passed through the URL parameters
	def get_object(self):
		id = self.kwargs.get('pk')
		obj = None
		if id is not None:
			obj = get_object_or_404(Project, projectid=id)
		return obj
	#Retrieve the ProjectsForm and TasksForm
	def get(self, request, id=None, *args, **kwargs):
		context = {}
		obj = self.get_object()
		if obj is not None:
			form = ProjectsForm(instance=obj)
			task_form = TasksForm()
			context['project'] = obj
			context['form'] = form
			context['projectid'] = obj.projectid
			context['tasks'] = Task.objects.filter(project__projectid=obj.projectid)
		return render(request, self.template_name, context)

	def post(self, request, id=None, *args, **kwargs):
		context = {}
		obj = self.get_object()
		if obj is not None:
			form = ProjectsForm(request.POST, instance=obj)
			if form.is_valid():
				project = form.save(commit=False)
				projectname = form.cleaned_data.get('projectname')
				projdesc = form.cleaned_data.get('projdesc')
				project_deadline = form.cleaned_data.get('project_deadline')
				project.save()
				messages.success(request, 'Project was edited successfully')
			context['project'] = obj
			context['form'] = form
			context['projectid'] = obj.projectid
		return render(request, self.template_name, context)

@login_required
@transaction.atomic
def ProjectUpdateView2(request,pk):
	template_name = "project_update_second.html"
	TaskInlineFormSet = inlineformset_factory(Project, Task, fields=('task_name', 
            'task_description','task_priority', 'task_performer'), extra=0, can_delete=True)
	project = Project.objects.get(projectid=pk)
	tasks = Task.objects.filter(project__projectid=pk)
	if request.method == "POST":
		formset = TaskInlineFormSet(request.POST, request.FILES, instance=project)
		if formset.is_valid():
			formset.save()
			return redirect('project-update-second',project.projectid)
	else:
		formset = TaskInlineFormSet(instance=project)
	return render(request, 'project_update_second.html', {'formset':formset, 'project':project, 'tasks': tasks})

class ProjectDelete(LoginRequiredMixin,View):
	template_name = "project_delete.html"
	success_message = "Project was deleted successfully!"

	def get_object(self):
		id = self.kwargs.get('pk')
		obj = None
		if id is not None:
			obj = get_object_or_404(Project, projectid=id)
		return obj

	#Retrieve the object
	def get(self, request, id=None, *args, **kwargs):
		context = {}
		obj = self.get_object()
		if obj is not None:
			form = ProjectsForm(instance=obj)
			task_form = TasksForm()
			context['project'] = obj
		return render(request, self.template_name, context)

	def post(self, request, id=None, *args, **kwargs):
		context ={}
		obj = self.get_object()
		if obj is not None:
			obj.delete()
			context['project'] = None
			return redirect('dashboard')	
		return render(request, self.template_name, context)

 #Generic CRUD for Tasks
class TasksList(LoginRequiredMixin,ListView):
	model = Task
	context_object_name = "tasks"
     #template_name = "tasks_list.html"
	def get_context_data(self, **kwargs):
		 # Call the base implementation first to get a context
		context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
		context['tasks'] = Task.objects.filter(project__projectid=pk)
		return context
class TaskDetail(LoginRequiredMixin,DetailView):
	model = Task
	template_name = "task_detail.html"
class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = Task
    context_object_name = 'task'
	 #template_name = "task_update.html"

class TaskDelete(LoginRequiredMixin, DeleteView):
    model = Task
	 #template_name = "task_delete.html"