from django.forms import DateTimeInput
from django_filters import FilterSet, DateTimeFilter
from .models import Post


class PostsFIlter(FilterSet):
	post_after = DateTimeFilter(field_name='date', lookup_expr='gt',
								widget=DateTimeInput(format='%d-%m-%Y', attrs={'type': 'datetime-local'}))
	class Meta:
		model = Post
		fields = [
			'title',
			'categories',
		]