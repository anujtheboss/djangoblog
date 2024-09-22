import os
import logging
from .models import Post, Website
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.views.generic import  ListView, DetailView, CreateView, UpdateView,DeleteView,View 
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class ImageUploadView(View):
    def post(self, request, *args, **kwargs):
        try:
            image_file = request.FILES.get('file')
            if image_file:
                image_name = image_file.name
                media_directory = os.path.join('media', 'images')
                image_path = os.path.join(media_directory, image_name)

                # Create directory if it doesn't exist
                os.makedirs(media_directory, exist_ok=True)

                with open(image_path, 'wb+') as destination:
                    for chunk in image_file.chunks():
                        destination.write(chunk)
                
                return JsonResponse({'location': f'/media/images/{image_name}'})
            return JsonResponse({'error': 'No file uploaded'}, status=400)
        except Exception as e:
            logger.error("Image upload error: %s", str(e))
            return JsonResponse({'error': 'Image upload failed'}, status=500)

class PostListView(ListView):
    model = Post
    template_name = 'blog/home.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 5

    def get_queryset(self):
        # Get the search query from the request
        q = self.request.GET.get('q', '')

        if q:
            # Filter posts by title, content, or author's username
            return Post.objects.filter(
                Q(title__icontains=q) |
                Q(content__icontains=q) |
                Q(author__username__icontains=q)
            ).order_by('-date_posted')
        else:
            # If no search query, return all posts ordered by date
            return Post.objects.all().order_by('-date_posted')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '')  # Pass 'q' to the template

        # Add the total post count to the context
        context['post_count'] = self.get_queryset().count()
        return context


class UserPostListView(ListView):
    model = Post
    template_name = 'blog/user_posts.html'     #<app>/<model>_<viewtype>.html
    context_object_name = 'posts'     
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')


class PostDetailView(DetailView):
    model = Post


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title','content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title','content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

def about(request):
    return render(request, 'blog/about.html', {'title': 'About'}) 


def website(request):
    return render(request, 'blog/pageweb.html')
