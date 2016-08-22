from geopy.distance import vincenty


def closest_stations(coord, engine, count=5):
    conn = engine.connect()

    # Compute distance to each station.
    stations = conn.execute("SELECT * FROM station_info;")

    distances = []

    for station in stations:
        distances.append({
            "id": station["station_id"],
            "name": station["name"],
            "distance": vincenty(
                coord, (station["lat"], station["long"])).meters
        })

    return sorted(distances, key=lambda info: info["distance"])[:count]
