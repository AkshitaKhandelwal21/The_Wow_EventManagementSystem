
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.utils.timezone import now
import calendar
from dashboards.models import Event, EventRegistration
from django.db.models import Count, F, ExpressionWrapper, DecimalField, Value
from django.db.models.functions import Coalesce, Cast



def get_monthly_registration_data(user):
    current_year = now().year

    monthly_regs = (
        EventRegistration.objects
        .filter(event__user=user, created_at__year=current_year)
        .annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(count=Count("id"))
        .order_by("month")
    )

    month_dict = {
        entry["month"].month: entry["count"]
        for entry in monthly_regs
    }

    max_count = max(month_dict.values()) if month_dict else 1

    monthly_data = []

    for month in range(1, 13):
        count = month_dict.get(month, 0)

        monthly_data.append({
            "label": calendar.month_abbr[month],
            "registrations_pct": int((count / max_count) * 100),
            "checkins_pct": int((count / max_count) * 100),
        })

    return monthly_data


def get_top_events(user, limit=3):

    events = (
        Event.objects
        .filter(user=user)
        .annotate(
            guests_count=Count('registrations'),

            revenue=ExpressionWrapper(
                Cast(Count('registrations'), DecimalField()) *
                Coalesce(
                    F('price'),
                    Value(0),
                    output_field=DecimalField()
                ),
                output_field=DecimalField(max_digits=12, decimal_places=2)
            )
        )
        .order_by('-guests_count')[:limit]
    )

    for event in events:
        if event.seats and event.seats > 0:
            event.occupancy = int((event.guests_count / event.seats) * 100)
        else:
            event.occupancy = 0

    return events