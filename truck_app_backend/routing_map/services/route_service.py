import requests

def get_route(origin, destination):

    url = (
        f"http://router.project-osrm.org/route/v1/driving/"
        f"{origin[1]},{origin[0]};"
        f"{destination[1]},{destination[0]}"
        f"?overview=full&geometries=geojson&steps=true"
    )

    response = requests.get(url)

    response.raise_for_status()

    data = response.json()

    if not data.get("routes"):
        raise Exception("No route found")

    route = data["routes"][0]

    return {
        "distance_miles": round(route["distance"] / 1609.34, 2),
        "duration_hours": round(route["duration"] / 3600, 2),
        "geometry": route["geometry"],
        "steps": route["legs"][0]["steps"]
    }