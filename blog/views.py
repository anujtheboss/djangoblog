from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.views.generic import (ListView,
                                 DetailView,
                                 CreateView,
                                 UpdateView,
                                 DeleteView,
                                 )
from .models import Post
from django.db.models import Q

# def home(request):
#     q = request.GET.get('q') if request.GET.get('q') else ''
    
#     if q:
#         # Filter posts by title, content, or author_username
#         posts = Post.objects.filter(
#             Q(title__icontains=q) | 
#             Q(content__icontains=q) | 
#             Q(author__username__icontains=q)
#         )
#     else:
#         # No query, so return all posts
#         posts = Post.objects.all()
    
#     context = {
#         'posts': posts,
#         'q': q
#     }
    
#     return render(request, 'blog/home.html', context)


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