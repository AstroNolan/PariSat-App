from skyfield.api import Topos, load
from skyfield.sgp4lib import EarthSatellite
from datetime import timedelta
import requests


def GetTLE(norad_cat_id):
    url = f"https://db.satnogs.org/api/tle/?norad_cat_id={norad_cat_id}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data:
            tle = data[0]
            return tle['tle1'], tle['tle2']


def RoundTime(ti):
    dt = ti.utc_datetime().replace(microsecond=0)
    return load.timescale().utc(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)


def FindNextPass(satellite, observer, t, min_elevation):
    t0 = t
    t1 = t + timedelta(days=3)
    times, events = satellite.find_events(
        observer, t0, t1, altitude_degrees=min_elevation)

    rise_time = None
    culminate_time = None
    set_time = None
    culmination_azimuth = None
    culmination_elevation = None
    culmination_distance = None

    for ti, event in zip(times, events):
        if event == 0:
            rise_time = ti.utc_datetime()
        elif event == 1:
            culminate_time = ti.utc_datetime()
            difference = satellite - observer
            topocentric = difference.at(RoundTime(ti))
            alt, az, distance = topocentric.altaz()
            culmination_azimuth = round(az.degrees, 2)
            culmination_elevation = round(alt.degrees, 2)
            culmination_distance = int(distance.km)
        elif event == 2:
            set_time = ti.utc_datetime()
            break
    return rise_time, culminate_time, set_time, culmination_azimuth, culmination_elevation, culmination_distance


def NextPass(observer_lat, observer_lon, min_elevation):
    tle_line1, tle_line2 = GetTLE(60239)
    satellite = EarthSatellite(
        tle_line1, tle_line2, 'Satellite', load.timescale())
    observer = Topos(latitude_degrees=observer_lat,
                     longitude_degrees=observer_lon)
    ts = load.timescale()
    t = ts.now()
    rise_time, culminate_time, set_time, culmination_azimuth, culmination_elevation, culmination_distance = FindNextPass(
        satellite, observer, t, min_elevation)
    t_dt = t.utc_datetime()
    if not rise_time and set_time and t_dt <= set_time:
        rise_time, culminate_time, set_time, culmination_azimuth, culmination_elevation, culmination_distance = FindNextPass(
            satellite, observer, t - timedelta(minutes=30), min_elevation)
    return rise_time, culminate_time, set_time, culmination_azimuth, culmination_elevation, culmination_distance


if __name__ == "__main__":
    observer_lat = 48.8566
    observer_lon = 2.3522
    min_elevation = 45.0

    next_pass_info = NextPass(observer_lat, observer_lon, min_elevation)
    rise_time, culminate_time, set_time, culmination_azimuth, culmination_elevation, culmination_distance = next_pass_info
    if all(next_pass_info):
        rise_time, culminate_time, set_time, culmination_azimuth, culmination_elevation, culmination_distance = next_pass_info
        print("Rise time:", rise_time.strftime('%Y-%m-%d %H:%M:%S %Z'))
        print("Culminate time:", culminate_time.strftime('%Y-%m-%d %H:%M:%S %Z'))
        print("Set time:", set_time.strftime('%Y-%m-%d %H:%M:%S %Z'))
        print("Culmination azimuth:", culmination_azimuth)
        print("Culmination elevation:", culmination_elevation)
        print("Culmination distance:", culmination_distance)
    else:
        print("Pas de passage dans les 72 prochaines heures")
