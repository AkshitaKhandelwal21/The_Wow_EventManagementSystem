from datetime import timedelta
from django.utils import timezone
from django.db.models import Q


class EventFilterMixin:

    def filter_queryset(self, queryset):
        category = self.request.GET.get('category')
        date_filter = self.request.GET.get('date')
        price = self.request.GET.get('price')
        search = self.request.GET.get('search')
        sort = self.request.GET.get('sort')

        if category:
            queryset = queryset.filter(category=category)

        today = timezone.localdate()
        if date_filter == 'today':
            queryset = queryset.filter(date=today)
        if date_filter == 'tomorrow':
            tomorrow = today + timedelta(days=1)
            queryset = queryset.filter(date=tomorrow)
        if date_filter == 'this-week':
            end_week = today + timedelta(days=7)
            queryset = queryset.filter(date__range = [today, end_week])
        if date_filter == 'this-month':
            queryset = queryset.filter(date__month=today.month, date__year=today.year)

        if search:
            queryset = queryset.filter(Q(title__icontains=search) | Q(location__icontains=search))
            # queryset = queryset.filter(location__icontains=search)

        sort_mapping = {
            "date": "date",
            "name": "title",
            "latest": "-date",
        }

        if sort in sort_mapping:
            queryset = queryset.order_by(sort_mapping[sort])
        else:
            queryset = queryset.order_by("-date")

        return queryset