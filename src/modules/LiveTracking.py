from astropy import units as u
from poliastro.earth import EarthSatellite
from poliastro.earth.plotting import GroundtrackPlotter
from sgp4.api import Satrec, jday
from poliastro.bodies import Earth
from poliastro.twobody import Orbit
from astropy.time import Time
from poliastro.util import time_range
from astropy.coordinates import SphericalRepresentation
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta, timezone
import requests
from math import sqrt, degrees, radians, cos, sin


def GetTLE(norad_cat_id):
    url = f"https://db.satnogs.org/api/tle/?norad_cat_id={norad_cat_id}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data:
            tle = data[0]
            return tle


def OrbitFromTLE(tle, current_time):
    satellite = Satrec.twoline2rv(tle['tle1'], tle['tle2'])
    jd, fr = jday(current_time.year, current_time.month, current_time.day,
                  current_time.hour, current_time.minute, current_time.second)
    _, r, v = satellite.sgp4(jd, fr)
    r = np.array(r) * u.km
    v = np.array(v) * u.km / u.s
    orbit = Orbit.from_vectors(Earth, r, v, epoch=Time(current_time))
    return orbit


def CalculateVisibilityRadius(altitude_km):
    R_earth_km = 6371.0
    visibility_radius_km = sqrt((R_earth_km + altitude_km)**2 - R_earth_km**2)
    return visibility_radius_km


def GenerateCirclePoints(lat, lon, radius_km, num_points=100):
    circle_lats = []
    circle_lons = []
    for i in range(num_points):
        angle = radians(float(i) / num_points * 360)
        dlat = radius_km / 6371.0 * cos(angle)
        dlon = radius_km / 6371.0 * sin(angle) / cos(radians(lat))
        circle_lats.append(lat + degrees(dlat))
        circle_lons.append(lon + degrees(dlon))
    return circle_lats, circle_lons


def LatLon(orb: Orbit, gp):
    raw_pos, raw_epoch = orb.rv()[0], orb.epoch
    itrs_pos = gp._from_raw_to_ITRS(raw_pos, raw_epoch)
    itrs_latlon_pos = itrs_pos.represent_as(SphericalRepresentation)
    lat = itrs_latlon_pos.lat.to_value(u.deg)
    lon = itrs_latlon_pos.lon.to_value(u.deg)
    return lat, lon


def ShowOrbit(observer_lat=48.8566, observer_lon=2.3522):
    tle = GetTLE(60239)

    current_time = datetime.now(timezone.utc)
    parisat = OrbitFromTLE(tle, current_time)
    prs_spacecraft = EarthSatellite(parisat, None)
    period_seconds = parisat.period.to(u.second).value
    t_span = time_range(
        current_time, end=current_time + timedelta(seconds=period_seconds)
    )

    gp = GroundtrackPlotter()
    gp.update_layout(
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        dragmode=False,
        hoverlabel=dict(
            bgcolor="#CFD8DC",
            bordercolor="rgba(0,0,0,0)",
            font=dict(
                family="Roboto",
                color="#2C3E50"
            )
        ),
    )

    gp.update_geos(
        bgcolor='rgba(0,0,0,0)',
        projection_type="natural earth",
        showcountries=True,
        landcolor="#3F83BF",
        oceancolor="#1D4B73",
        countrycolor="rgba(68, 68 68, 0.5)",
        coastlinewidth=0.5,
        countrywidth=0.5,
        lataxis_gridcolor="rgba(128, 128, 128, 0.5)",
        lonaxis_gridcolor="rgba(128, 128, 128, 0.5)",
        lataxis_gridwidth=0.5,
        lonaxis_gridwidth=0.5
    )

    altitude_km = np.linalg.norm(parisat.r.to(u.km).value) - 6371.0
    visibility_radius_km = CalculateVisibilityRadius(altitude_km)
    lat, lon = LatLon(parisat, gp)
    circle_lats, circle_lons = GenerateCirclePoints(
        lat, lon, visibility_radius_km)

    gp.add_trace(
        go.Scattergeo(
            lon=circle_lons,
            lat=circle_lats,
            mode='lines',
            line=dict(width=0, color='#FF8668'),
            fill='toself',
            fillcolor='rgba(255, 134, 104, 0.5)',
            opacity=0.5,
            hoverinfo='skip',
        )
    )

    gp.add_trace(
        go.Scattergeo(
            lat=[observer_lat],
            lon=[observer_lon],
            name="Observer",
            marker={
                "color": "#ECEFF1",
                "size": 15,
                "symbol": "x-thin",
                "line": {"width": 4, "color": "#ECEFF1"}
            },
            hovertemplate="Observer<extra></extra>",
        )
    )

    gp.plot(
        prs_spacecraft,
        t_span,
        label="Trajectory",
        color="#FF3503",
        line_style={"width": 2},
        marker={
            "size": 15,
            "symbol": "circle"
        },
    )
    for data in gp.fig.data:
        if isinstance(data, go.Scattergeo) and data.name == "Trajectory":
            latitudes = data.lat
            longitudes = data.lon
            hover_text = [f"({lat:.4f}°, {lon:.4f}°)" for lat,
                          lon in zip(latitudes, longitudes)]
            data.hovertext = hover_text
            data.hovertemplate = "%{hovertext}<extra></extra>"

    return gp.fig


if __name__ == '__main__':
    ShowOrbit().show()
