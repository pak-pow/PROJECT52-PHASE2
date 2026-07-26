import datetime
from app.models.provider_model import get_provider_availability
from app.models.service_model import get_service_by_id
from app.models.booking_model import get_provider_bookings_for_date


def compute_available_slots(provider_id, service_id, date_str):
    """Compute available time slots for a provider on a specific date.

    Args:
        provider_id (int): Provider ID.
        service_id (int): Service ID.
        date_str (str): Date string formatted YYYY-MM-DD.

    Returns:
        list of dicts: [{"start_time": "09:00", "end_time": "09:30", "available": True}, ...]
    """
    service = get_service_by_id(service_id)
    if not service:
        return []

    duration = service["duration_minutes"]

    try:
        dt = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return []

    # Day of week: 0=Mon ... 6=Sun
    day_of_week = dt.weekday()

    # Get working hours
    schedules = get_provider_availability(provider_id, day_of_week)
    if not schedules:
        return []

    # Existing confirmed bookings on this date
    existing_bookings = get_provider_bookings_for_date(provider_id, date_str)
    booked_spans = []
    for b in existing_bookings:
        b_start = datetime.datetime.strptime(b["start_time"], "%H:%M").time()
        b_end = datetime.datetime.strptime(b["end_time"], "%H:%M").time()
        booked_spans.append((b_start, b_end))

    slots = []
    for sched in schedules:
        work_start = datetime.datetime.strptime(sched["start_time"], "%H:%M")
        work_end = datetime.datetime.strptime(sched["end_time"], "%H:%M")

        curr = work_start
        step = datetime.timedelta(minutes=duration)

        while curr + step <= work_end:
            s_time = curr.time()
            e_time = (curr + step).time()

            # Check overlap with any booked span
            is_booked = False
            for b_start, b_end in booked_spans:
                if (s_time < b_end and e_time > b_start):
                    is_booked = True
                    break

            slots.append({
                "start_time": s_time.strftime("%H:%M"),
                "end_time": e_time.strftime("%H:%M"),
                "available": not is_booked,
            })
            curr += datetime.timedelta(minutes=30)  # 30-min grid increment

    return slots
