MAX_DRIVING_HOURS = 11
MAX_DUTY_HOURS = 14
RESET_HOURS = 10


def split_into_days(total_hours):

    days = []
    remaining = total_hours
    day = 1

    while remaining > 0:

        segments = []
        duty_used = 0
        driving_used = 0

        while remaining > 0 and duty_used < MAX_DUTY_HOURS:

            # DRIVING
            drive = min(MAX_DRIVING_HOURS - driving_used, remaining)
            if drive <= 0:
                break

            segments.append({
                "type": "driving",
                "hours": drive
            })

            driving_used += drive
            duty_used += drive
            remaining -= drive

            if remaining <= 0:
                break

            # ON DUTY (not just off duty!)
            on_duty = min(2, remaining)
            segments.append({
                "type": "on_duty",
                "hours": on_duty
            })

            duty_used += on_duty
            remaining -= on_duty

            if remaining <= 0:
                break

            # REST (sleeper equivalent for simulation)
            rest = min(1, remaining)
            segments.append({
                "type": "off_duty",
                "hours": rest
            })

            duty_used += rest
            remaining -= rest

        # COMPLETE DAY WITH SLEEPER
        if duty_used < 24:
            segments.append({
                "type": "sleeper",
                "hours": 24 - duty_used
            })

        days.append({
            "day": day,
            "segments": segments,

            # FIXED: correct interpretation
            "driving_hours": driving_used,
            "on_duty_hours": duty_used,
            "off_duty_hours": 24 - duty_used
        })

        day += 1

    return days

def generate_fuel_stops(distance_miles):

    stops = []

    interval = 1000
    count = int(distance_miles // interval)

    for i in range(count):

        stops.append({
            "type": "fuel",
            "mile_marker": (i + 1) * interval,
            "duration_hours": 0.5
        })

    return stops