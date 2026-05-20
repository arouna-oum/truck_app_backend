from .simulator import split_into_days, generate_fuel_stops

# def generate_eld_logs(distance_miles, total_hours):

#     daily_logs = split_into_days(total_hours)
#     fuel_stops = generate_fuel_stops(distance_miles)

#     return {
#         "daily_logs": daily_logs,
#         "fuel_stops": fuel_stops
#     }

def generate_eld_logs(distance_miles, total_hours):

    daily_logs = split_into_days(total_hours)

    fuel_stops = generate_fuel_stops(distance_miles)

    summary = {
        "driving": 0,
        "on_duty": 0,
        "off_duty": 0,
        "sleeper": 0
    }

    for day in daily_logs:

        summary["driving"] += day["driving_hours"]

        summary["on_duty"] += day["on_duty_hours"]

        summary["off_duty"] += day["off_duty_hours"]

        for seg in day["segments"]:

            if seg["type"] == "sleeper":
                summary["sleeper"] += seg["hours"]

    return {
        "daily_logs": daily_logs,
        "fuel_stops": fuel_stops,
        "summary": summary
    }