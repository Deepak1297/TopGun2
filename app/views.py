from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from django.views.generic.edit import UpdateView, DeleteView, FormView
from django.urls import reverse_lazy

from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from .forms import UserUpdateForm, ProfileUpdateForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login

from .models import Task, Profile, Photo, Category


# Create your views here.
# def homeView(request):
# return render(request, 'app/profile.html')


@login_required
def profile(request, username):
    user = get_object_or_404(user, username=username)
    profile = get_object_or_404(Profile, user=user)

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST,
                                   request.FILES,
                                   instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('profile')

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'app/profile.html', {'profile': profile, 'user': user})


class CustomLoginView(LoginView):
    template_name = 'app/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('profile')


class ProfileView(Profile):
    model = Profile
    fields = '__all__'

    def profile(request):
        return render(request, 'app/profile.html')


class RegisterPage(FormView):
    template_name = 'app/register.html'
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(RegisterPage, self).form_valid(form)

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('tasks')
        return super(RegisterPage, self).get(*args, **kwargs)


class TaskList(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = 'tasks'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks'] = context['tasks'].filter(user=self.request.user)
        context['count'] = context['tasks'].filter(complete=False).count()

        search_input = self.request.GET.get('search-area') or ''
        if search_input:
            context['tasks'] = context['tasks'].filter(
                title__icontains=search_input)
            context['search_input'] = search_input
        return context


class TaskDetail(LoginRequiredMixin, DetailView):
    model = Task
    context_object_name = 'task'
    template_name = 'app/task.html'


class TaskCreate(LoginRequiredMixin, CreateView):
    model = Task
    fields = '__all__'
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(TaskCreate, self).form_valid(form)


class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = Task
    fields = '__all__'
    success_url = reverse_lazy('tasks')


class DeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    context_object_name = 'task'
    success_url = reverse_lazy('tasks')
    template_name = "app/task_confirm_delete.html"


@login_required(login_url='login')
def gallery(request):
    user = request.user
    category = request.GET.get('category')
    if category == None:
        photos = Photo.objects.filter(category__user=user)
    else:
        photos = Photo.objects.filter(
            category__name=category, category__user=user)

    categories = Category.objects.filter(user=user)
    context = {'categories': categories, 'photos': photos}
    return render(request, 'app/gallery.html', context)


@login_required(login_url='login')
def viewPhoto(request, pk):
    photo = Photo.objects.get(id=pk)
    return render(request, 'app/photo.html', {'photo': photo})





def editImage(request, pk):
    Photo = Category.objects.get(id=pk)

    if request.method == "POST":
        if len(request.FILES) != 0:
            if len(Photo.image) > 0:
                os.remove(Photo.image.path)
            Photo.image = request.FILES['image']
        Photo.name = request.POST.get('name')
        Photo.description = request.POST.get('description')
        Photo.category = request.POST.get('category')
        Photo.save()
        messages.success(request, "Photo Updated Successfully")
        return redirect('/')

    context = {'Photo': Photo}
    return render(request, 'app/edit_image.html', context)
