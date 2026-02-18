class EventFilterMixin:

    def filter_queryset(self, queryset):
        category = self.request.GET.get('category')
        search = self.request.GET.get('search')
        sort = self.request.GET.get('sort')

        if category:
            queryset = queryset.filter(category=category)

        if search:
            queryset = queryset.filter(title__icontains=search)

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