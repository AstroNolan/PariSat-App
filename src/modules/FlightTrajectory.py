from astropy import units as u
from poliastro.earth import EarthSatellite
from poliastro.earth.plotting import GroundtrackPlotter
from sgp4.api import Satrec
from poliastro.bodies import Earth
from poliastro.twobody import Orbit
from astropy.time import Time
from poliastro.util import time_range
from astropy.coordinates import SphericalRepresentation
import numpy as np
import plotly.graph_objects as go
from datetime import timedelta
from math import sqrt, degrees, radians, cos, sin


def GetTLE():
    tle_line0 = "0 ARIANE 6 R/B"
    tle_line1 = "1 60239U 24128A   24191.83752928  .00000000  00000-0  00000-0 0    12"
    tle_line2 = "2 60239  61.9940 161.6170 0002691 303.0960 283.4570 14.96533815    17"
    return {'tle0': tle_line0, 'tle1': tle_line1, 'tle2': tle_line2}


def OrbitFromTLE(tle):
    satellite = Satrec.twoline2rv(tle['tle1'], tle['tle2'])
    jd, fr = satellite.jdsatepoch, satellite.jdsatepochF
    epoch = Time(jd + fr, format='jd')
    _, r, v = satellite.sgp4(jd, fr)
    r = np.array(r) * u.km
    v = np.array(v) * u.km / u.s
    orbit = Orbit.from_vectors(Earth, r, v, epoch)

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


def AddPhoto(parisat, gp, i, delta):
    prs_prop = parisat.propagate(parisat.epoch + timedelta(seconds=delta-3966))
    lat_photo, lon_photo = LatLon(prs_prop, gp)
    PHOTO = [lat_photo, lon_photo] * u.deg

    gp.add_trace(
        go.Scattergeo(
            lat=PHOTO[0],
            lon=PHOTO[-1],
            name=f"Photo {i}",
            marker={
                "color": "#ECEFF1",
                "size": 15,
                "symbol": "star-diamond",
            },
            hoverinfo='none',
            customdata=[f"Photo n°{i}"],
        )
    )


def AddVisibility(parisat, gp, i, delta):
    prs_prop = parisat.propagate(parisat.epoch + timedelta(seconds=delta-3966))
    lat_photo, lon_photo = LatLon(prs_prop, gp)
    altitude_km = np.linalg.norm(prs_prop.r.to(u.km).value) - 6371.0
    visibility_radius_km = CalculateVisibilityRadius(altitude_km)
    circle_lats, circle_lons = GenerateCirclePoints(
        lat_photo, lon_photo, visibility_radius_km)

    gp.add_trace(
        go.Scattergeo(
            lon=circle_lons,
            lat=circle_lats,
            name=f"Visibility {i}",
            mode='lines',
            line=dict(width=0, color='#ECEFF1'),
            fill='toself',
            fillcolor='rgba(236, 239, 241, 0.5)',
            opacity=0.5,
            hoverinfo='skip',
            visible=False
        )
    )


def ShowOrbit():
    tle = GetTLE()
    parisat = OrbitFromTLE(tle)
    prs_spacecraft = EarthSatellite(parisat, None)
    t_span = time_range(
        parisat.epoch, end=parisat.epoch + (10874.28 - 3955.92) * u.s
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
            line=dict(width=0, color='#FFB703'),
            fill='toself',
            fillcolor='rgba(255, 183, 3, 0.5)',
            opacity=0.5,
            hoverinfo='skip'
        )
    )

    STATION = [67.889663108, 21.10416625] * u.deg
    gp.add_trace(
        go.Scattergeo(
            lat=STATION[0],
            lon=STATION[-1],
            name="Esrange",
            marker={
                "color": "#ECEFF1",
                "size": 15,
                "symbol": "x-thin",
                "line": {"width": 4, "color": "#ECEFF1"}
            },
            hoverinfo='none',
            customdata=[["Esrange", "Esrange Space Center (SSC)"]],
        )
    )

    LAUNCHPAD = [5.2360, -52.7750] * u.deg
    gp.add_trace(
        go.Scattergeo(
            lat=LAUNCHPAD[0],
            lon=LAUNCHPAD[-1],
            name="Kourou",
            marker={
                "color": "#ECEFF1",
                "size": 15,
                "symbol": "x-thin",
                "line": {"width": 4, "color": "#ECEFF1"}
            },
            hoverinfo='none',
            customdata=[["Kourou", "Guiana Space Center (CNES)"]],
        )
    )

    gp.plot(
        prs_spacecraft,
        t_span,
        label="Trajectory",
        color="#FFB703",
        line_style={"width": 2},
        marker={
            "size": 15,
            "symbol": "circle"
        }
    )
    for data in gp.fig.data:
        if data.name == "Trajectory":
            if data.marker['symbol'] == 'circle':
                data.hovertemplate = "PariSat Initialization • T0+3966s<extra></extra>"
            else:
                data.hoverinfo = 'skip'

    photo_deltas = [4166, 4297, 4565, 4925, 4963, 5006, 5768, 6118, 6522, 6560]
    visibility_traces = []
    photo_traces = []
    for i in range(len(photo_deltas)):
        AddVisibility(parisat, gp, i+1, photo_deltas[i])
        visibility_traces.append(len(gp.fig.data) - 1)
    for i in range(len(photo_deltas)):
        AddPhoto(parisat, gp, i+1, photo_deltas[i])
        photo_traces.append(len(gp.fig.data) - 1)

    return gp.fig, visibility_traces, photo_traces


if __name__ == '__main__':
    fig, _, _ = ShowOrbit()
    fig.show()
