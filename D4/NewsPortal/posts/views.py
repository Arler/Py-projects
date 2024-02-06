from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import (
	ListView, DetailView, CreateView, UpdateView, DeleteView
)
from .models import Post
from .filters import PostsFIlter
from .forms import NewsForm, ArticleForm


class PostsList(ListView):
	model = Post
	ordering = '-date'
	template_name = 'posts.html'
	context_object_name = 'posts'
	paginate_by = 10


class PostDetail(DetailView):
	model = Post
	template_name = 'post.html'
	context_object_name = 'post'


def posts_search(request):
	f = PostsFIlter(request.GET, queryset=Post.objects.all())
	return render(request, 'filter_posts.html', {'filter': f})


# ----- Представления для новостей -----

class NewsCreate(CreateView):
	form_class = NewsForm
	model = Post
	template_name = 'post_edit.html'

	def form_valid(self, form):
		news = form.save(commit=False)
		news.post_type = Post.news
		return super().form_valid(form)


class NewsUpdate(UpdateView):
	form_class = NewsForm
	model = Post
	template_name = 'post_edit.html'


class NewsDelete(DeleteView):
	model = Post
	template_name = 'post_delete.html'
	success_url = reverse_lazy('posts_list')


# ----- Представления для статей -----

class ArticleCreate(CreateView):
	form_class = ArticleForm
	model = Post
	template_name = 'post_edit.html'

	def form_valid(self, form):
		article = form.save(commit=False)
		article.post_type = Post.article
		return super().form_valid(form)


class ArticleUpdate(UpdateView):
	form_class = ArticleForm
	model = Post
	template_name = 'post_edit.html'


class ArticleDelete(DeleteView):
	model = Post
	template_name = 'post_delete.html'
	success_url = reverse_lazy('posts_list')