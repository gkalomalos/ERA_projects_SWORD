from pathlib import Path
from time import time, sleep

import folium
from matplotlib import cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap, Colormap

import branca.colormap
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from PIL import Image

import numpy as np
import geopandas as gpd
import pandas as pd

from constants import (
    CLIENT_ASSETS_DIR,
    FEATHERS_DIR,
    TEMP_DIR,
    REQUIREMENTS_DIR,
    RESOURCES_DIR,
    SHAPEFILES_DIR,
)
from handlers import (
    get_country_country_codes_from_country_names,
    calculate_impact_output_per_nuts2,
    generate_hazard_gdf,
    get_polygons,
    is_connected,
)

from climada.engine import Impact
from climada.hazard import Hazard


def replace_links_with_local(html_file_path, repr=False):
    """
    Replace the URLs in an HTML file with the paths to local files.

    Parameters
    -----------
    html_file_path : str
        A string representing the path to the HTML file that needs to be updated with local file paths.

    Returns
    --------
    None

    Notes
    ------
    This function reads an HTML file and replaces all URLs that point to external resources with paths to local files.
    The mapping from URLs to local file paths is defined in a dictionary inside the function. After replacing the URLs,
    it writes the modified HTML back to the file.

    The function assumes that the URLs and local file paths are correctly matched in the dictionary. It does not check 
    if the local files actually exist. The local files are expected to be in a folder named 'res' in the same directory
    as the HTML file.
    """

    # Define a dictionary that maps URLs to local file names
    url_to_filename = {
        "https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/leaflet.js": "leaflet.js",
        "https://code.jquery.com/jquery-1.12.4.min.js": "jquery-1.12.4.min.js",
        "https://cdn.jsdelivr.net/npm/bootstrap@5.2.2/dist/js/bootstrap.bundle.min.js": "bootstrap.bundle.min.js",
        "https://cdnjs.cloudflare.com/ajax/libs/Leaflet.awesome-markers/2.0.2/leaflet.awesome-markers.js": "leaflet.awesome-markers.js",
        "https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/leaflet.css": "leaflet.css",
        "https://cdn.jsdelivr.net/npm/bootstrap@5.2.2/dist/css/bootstrap.min.css": "bootstrap.min.css",
        "https://netdna.bootstrapcdn.com/bootstrap/3.0.0/css/bootstrap.min.css": "bootstrap.netdna.min.css",
        "https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.2.0/css/all.min.css": "all.min.css",
        "https://cdnjs.cloudflare.com/ajax/libs/Leaflet.awesome-markers/2.0.2/leaflet.awesome-markers.css": "leaflet.awesome-markers.css",
        "https://cdn.jsdelivr.net/gh/python-visualization/folium/folium/templates/leaflet.awesome.rotate.min.css": "leaflet.awesome.rotate.min.css",
        "https://cdnjs.cloudflare.com/ajax/libs/d3/3.5.5/d3.min.js": "d3.min.js",
    }

    try:
        # Open the HTML file in read mode
        with open(html_file_path, 'r') as file:
            # Read the entire file into a string
            filedata = file.read()

        # For each URL in the dictionary...
        for url, filename in url_to_filename.items():
            # Construct the path to the local file
            if repr:
                local_path = f"static:///{filename}"
            else:
                local_path = f"{filename}"
            # Replace the URL with the local path in the string
            filedata = filedata.replace(url, local_path)

        # Open the HTML file in write mode
        with open(html_file_path, 'w') as file:
            # Write the modified string back to the file
            file.write(filedata)
    except FileNotFoundError:
        print(f"File {html_file_path} does not exist.")
    except IOError as e:
        print(f"An I/O error occurred: {str(e)}")


def plot_map_offline(x_mean, y_mean):
    """
    Generate a folium map centered around the given geographical coordinates.

    Parameters
    ----------
    x_mean : float
        The mean latitude around which the map will be centered.

    y_mean : float
        The mean longitude around which the map will be centered.

    Returns
    -------
    folium.Map
        A folium Map object with added geographical features.

    Notes
    -----
    This function generates a folium map and adds various geographical features to it including countries, rivers, lakes, 
    and oceans. The colors and opacities used for these features are chosen to mimic the appearance of CartoDB Positron maps. 
    The map is centered around the provided mean latitude and longitude.
    """
    # Create a map centered around the mean latitude and longitude of the hazard data
    m = folium.Map(
        location=[x_mean, y_mean],
        tiles=None,
        zoom_start=6,
        control_scale=True,
        prefer_canvas=True,
        name="Basemap"
    )

    # Define the paths to the shapefiles for various geographical features
    countries_path = Path(
        SHAPEFILES_DIR, 'ne_10m_admin_0_scale_rank_minor_islands.shp')
    rivers_path = Path(SHAPEFILES_DIR, 'ne_10m_rivers_europe.shp')
    lakes_path = Path(SHAPEFILES_DIR, 'ne_10m_lakes.shp')
    ocean_path = Path(SHAPEFILES_DIR, 'ne_10m_ocean.shp')

    # Read the shapefiles into GeoDataFrames
    countries = gpd.read_file(countries_path)
    rivers = gpd.read_file(rivers_path)
    lakes = gpd.read_file(lakes_path)
    ocean = gpd.read_file(ocean_path)

    # Create a feature group for the basemap
    basemap = folium.FeatureGroup(name="Basemap", control=False)

    # Add the countries to the feature group with specified style
    folium.GeoJson(
        countries, style_function=lambda x: {
            "color": "#752f45", "weight": 0.3, "opacity": 0.5, "fillColor": "#ffffff", "fillOpacity": 0.8}
    ).add_to(basemap)

    # Add the rivers to the feature group with specified style
    folium.GeoJson(
        rivers, style_function=lambda x: {
            "color": "#afc4c4", "weight": 0.8, "opacity": 0.8}
    ).add_to(basemap)

    # Add the lakes to the feature group with specified style
    folium.GeoJson(
        lakes, style_function=lambda x: {
            "color": "#afc4c4", "weight": 1, "opacity": 0.9}
    ).add_to(basemap)

    # Add the ocean to the feature group with specified style
    folium.GeoJson(
        ocean, style_function=lambda x: {
            "color": "#afc4c4", "weight": 1, "opacity": 0.9}
    ).add_to(basemap)

    # Add the feature group to the map
    basemap.add_to(m)

    return m


def generate_exposure_geojsonpopup(admin: str = "countries") -> folium.GeoJsonPopup:
    """
    Generate a GeoJsonPopup object with specified fields and aliases.

    Parameters
    -----------
    admin : str, optional
        Administrative level for which to generate the GeoJsonPopup. Can be one of the following:
        'countries': generates a popup with fields ['CNTR_CODE', 'value'] and aliases ['Country code', 'Total Exposure (EUR)']
        'nuts1': generates a popup with fields ['CNTR_CODE', 'NAME_LATN', 'value'] and aliases ['Country code', 'NUTS 1 code', 'Total Exposure (EUR)']
        'nuts2': generates a popup with fields ['CNTR_CODE', 'NAME_LATN', 'value'] and aliases ['Country code', 'NUTS 2 code', 'Total Exposure (EUR)']
        'nuts3': generates a popup with fields ['CNTR_CODE', 'NAME_LATN', 'value'] and aliases ['Country code', 'NUTS 3 code', 'Total Exposure (EUR)']

    Returns
    --------
    popup : folium.GeoJsonPopup
        The generated GeoJsonPopup object.

    Examples
    ---------
    >>> popup = generate_geojsonpopup()
    >>> m.add_child(popup)

    Notes
    ------
    This function generates a GeoJsonPopup object to be used with a folium.GeoJson layer. The GeoJsonPopup object
    allows for customized popups to appear when a feature is clicked on the map.
    """
    try:
        if admin == "countries":
            return folium.GeoJsonPopup(
                fields=["CNTR_CODE", "value"],
                aliases=["Country code", "Total Exposure (EUR)"],
            )
        elif admin == "nuts1":
            return folium.GeoJsonPopup(
                fields=["CNTR_CODE", "NAME_LATN", "value"],
                aliases=["Country code", "NUTS 1 code",
                         "Total Exposure (EUR)"],
            )
        elif admin == "nuts2":
            return folium.GeoJsonPopup(
                fields=["CNTR_CODE", "NAME_LATN", "value"],
                aliases=["Country code", "NUTS 2 code",
                         "Total Exposure (EUR)"],
            )
        elif admin == "nuts3":
            return folium.GeoJsonPopup(
                fields=["CNTR_CODE", "NAME_LATN", "value"],
                aliases=["Country code", "NUTS 3 code",
                         "Total Exposure (EUR)"],
            )
        else:
            raise ValueError(f'Invalid value for "admin" parameter: {admin}')
    except Exception as exc:
        raise ValueError(
            f"Exception while generating GeoJsonPopup objects: {exc}")


def generate_exposure_choropleth(
    data: gpd.GeoDataFrame = None, admin: str = "countries", countries: list = []
) -> folium.Choropleth:
    """
    Generate a folium.Choropleth object for a given administrative level, with the ability to filter by country.

    Parameters
    -----------
    data : gpd.GeoDataFrame, optional
        The data to be used in the Choropleth. If not provided, it will be loaded from a Feather file.
    admin : str, optional
        Administrative level for which to generate the Choropleth. Can be one of the following:
        'countries': generates a Choropleth with country-level data
        'nuts1': generates a Choropleth with NUTS 1-level data
        'nuts2': generates a Choropleth with NUTS 2-level data
        'nuts3': generates a Choropleth with NUTS 3-level data
    countries : list of str, optional
        A list of country names to filter the data by.

    Returns
    --------
    choropleth : folium.Choropleth
        The generated Choropleth object.

    Examples
    ---------
    >>> data = gpd.read_file('path/to/data.shp')
    >>> generate_exposure_choropleth(data=data, admin='nuts1', countries=['France', 'Germany'])

    Notes
    ------
    This function generates a folium.Choropleth object to be used with a folium.Map object. The Choropleth object
    displays a map with a color scale that represents the value of the data at each administrative boundary.
    The administrative level can be specified using the `admin` parameter, and the data can be filtered by country
    using the `countries` parameter.
    """
    try:
        if data is None:
            data = gpd.read_feather(
                Path(FEATHERS_DIR, "EEA_RG_01M_2021_values.feather")
            )
            if admin == "countries":
                data = data[data["LEVL_CODE"] == 0]
            if admin == "nuts1":
                data = data[data["LEVL_CODE"] == 1]
            if admin == "nuts2":
                data = data[data["LEVL_CODE"] == 2]
            if admin == "nuts3":
                data = data[data["LEVL_CODE"] == 3]
        if countries:
            country_codes = get_country_country_codes_from_country_names(
                countries)
            data = data[data["CNTR_CODE"].isin(country_codes)]

            vmax = data["value"].max()
            vmin = 0
            # Define the color scale
            threshold_scale = np.linspace(vmin, vmax)

            # Add a Choropleth layer for each group
            choropleth = folium.Choropleth(
                geo_data=data,
                name=admin,
                data=data,
                columns=["NUTS_ID", "value"],
                key_on="feature.properties.NUTS_ID",
                fill_color="RdYlGn_r",
                fill_opacity=0.4,
                nan_fill_color="grey",
                line_opacity=0.2,
                legend_name=f"Exposure {admin} (EUR)",
                highlight=True,
                overlay=False,
                threshold_scale=threshold_scale,
            )
            tooltip = generate_exposure_geojsonpopup(admin)
            # Add tooltip upon clicking
            tooltip.add_to(choropleth.geojson)
            return choropleth
    except Exception as exc:
        # print(f"Exception while generating Choropleth objects. More info: {exc}")
        return None


def plot_exposure(countries: list):
    """
    Plots the exposure for the given countries.

    Parameters
    -----------
    countries : list of str
        A list of country names for which to plot the exposure.

    Returns
    --------
    None

    Examples
    ---------
    >>> plot_exposure(['France', 'Germany', 'Italy'])

    Notes
    ------
    This function generates a Folium map object that displays the exposure for the given countries at different administrative
    levels (countries, NUTS 1, NUTS 2, and NUTS 3). The resulting map is saved to an HTML file in the client's assets directory.
    """
    start_time = time()
    country_codes = get_country_country_codes_from_country_names(countries)

    countries_gdf = gpd.read_feather(
        Path(FEATHERS_DIR, "EEA_RG_01M_2021_values.feather")
    )
    countries_gdf = countries_gdf[countries_gdf["LEVL_CODE"] == 0]
    countries_gdf = countries_gdf[countries_gdf["CNTR_CODE"].isin(
        country_codes)]
    x_mean = countries_gdf["geometry"].iloc[0].centroid.y
    y_mean = countries_gdf["geometry"].iloc[0].centroid.x
    try:
        online = is_connected()

        if online:
            # Create a Folium map object
            exposure_map = folium.Map(
                location=[x_mean, y_mean],
                tiles="CartoDB Positron",
                zoom_start=6,
                control_scale=True,
                prefer_canvas=True,
            )

            # Add an always visible base map to avoid hiding when selecting different layers.
            base_map = folium.FeatureGroup(
                name="Basemap",
                overlay=True,
                control=False,
            )

            folium.TileLayer(tiles="CartoDB Positron",
                             opacity=1).add_to(base_map)
            base_map.add_to(exposure_map)
        else:
            exposure_map = plot_map_offline(x_mean, y_mean)

        # Create a LayerControl object
        layer_control = folium.LayerControl()

        for admin in ["countries", "nuts1", "nuts2", "nuts3"]:
            choropleth = generate_exposure_choropleth(
                admin=admin, countries=countries)
            choropleth.add_to(exposure_map)

            # Hackey way to delete the legend.
            for key in choropleth._children:
                if key.startswith("color_map"):
                    del choropleth._children[key]

        # Add the LayerControl object to the map
        layer_control.add_to(exposure_map)

        # Add custom JavaScript to limit zoom levels
        min_zoom = 5
        max_zoom = 9
        zoom_limit_js = f"""
            <script>
                function limitZoomLevels() {{
                    var map = {exposure_map.get_name()};
                    map.options.minZoom = {min_zoom};
                    map.options.maxZoom = {max_zoom};
                    map.on('zoomend', function() {{
                        if (map.getZoom() < map.options.minZoom) {{
                            map.setZoom(map.options.minZoom);
                        }} else if (map.getZoom() > map.options.maxZoom) {{
                            map.setZoom(map.options.maxZoom);
                        }}
                    }});
                }}
                document.addEventListener("DOMContentLoaded", limitZoomLevels);
            </script>
        """

        # Add the JavaScript function to the header
        exposure_map.get_root().header.add_child(folium.Element(zoom_limit_js))

        # Add custom JavaScript to click nuts2 preselected layer
        click_nuts2_js = f"""
            <script>
                function clickNuts2() {{
                    var xpath = "//input[contains(@class, 'leaflet-control-layers-selector')]/following-sibling::span[text()=' nuts2']";
                    var iterator = document.evaluate(xpath, document, null, XPathResult.UNORDERED_NODE_ITERATOR_TYPE, null);
                    var span = iterator.iterateNext();

                    if (span) {{
                        var input = span.previousElementSibling;
                        input.click();
                    }} else {{
                        setTimeout(clickNuts2, 100);
                    }}
                }}

                document.addEventListener("DOMContentLoaded", clickNuts2);
            </script>
        """

        # Add the JavaScript function to the header
        exposure_map.get_root().header.add_child(folium.Element(click_nuts2_js))

        # Save the map to an HTML file
        exposure_html_file = Path(CLIENT_ASSETS_DIR, "exposure_europe.html")
        exposure_map.save(exposure_html_file)

        if online:
            save_map_as_image(map_type="exposure",
                              html_path=exposure_html_file)
        else:
            replace_links_with_local(exposure_html_file, repr=True)

            exposure_html_screenshot_file = Path(
                CLIENT_ASSETS_DIR, "exposure_europe_sc.html")
            exposure_map.save(exposure_html_screenshot_file)
            replace_links_with_local(exposure_html_screenshot_file, repr=False)
            save_map_as_image(map_type="exposure",
                              html_path=exposure_html_screenshot_file)
        # print(
        #     "\033[92m"
        #     + f"Finished plotting exposure maps in {time() - start_time}sec."
        #     + "\033[0m"
        # )
        return exposure_map
    except Exception as exception:
        # print(f"Exception while plotting exposure. More info: {exception}")
        pass


def plot_hazard(hazard: Hazard, return_periods: tuple = None):
    """
    Generates a folium map to visualize hazard intensity by NUTS2 region for different return periods using circles.

    Parameters
    ----------
    hazard : Hazard
        A Hazard object containing information on hazard events and their intensity.
    return_periods : tuple, optional
        A tuple of return periods to display on the map. The default value is None, which generates maps for
        return periods of 1000, 750, 500, 400, 250, 200, 150, 100, 50, and 10.

    Returns
    -------
    folium.Map
        A folium Map object that displays the hazard intensity by NUTS2 region for different return periods using circles.

    Raises
    ------
    Exception
        If an error occurs while generating the map with circles, an error message is printed.

    Notes
    -----
    The function uses the 'generate_hazard_gdf' function to create a pandas DataFrame of the hazard data for
    different return periods.
    The function uses the folium library to generate a map with NUTS2 regions and hazard
    intensity as the color scale of circles. The generated map is saved to an HTML file.
    """
    if not return_periods:
        return_periods = (1000, 750, 500, 400, 250, 200, 150, 100, 50, 10)
    try:
        hazard_gdf = generate_hazard_gdf(hazard, return_periods)

        # Calculate vmin and vmax
        vmin = hazard.intensity_thres
        vmax = hazard_gdf[[f"rp{rp}" for rp in return_periods]].max(
            axis=1).max()
        x_mean = hazard_gdf["latitude"].mean()
        y_mean = hazard_gdf["longitude"].mean()

        online = is_connected()

        if online:
            # Use CartoDB Positron tiles
            tiles = "CartoDB Positron"

            # create a folium map
            hazard_map = folium.Map(
                location=[x_mean, y_mean],
                tiles=tiles,
                zoom_start=6,
                control_scale=True,
                prefer_canvas=True,
                name="Basemap"
            )

            # Add an always visible base map to avoid hiding when selecting different layers
            base_map = folium.FeatureGroup(
                name="Basemap",
                overlay=True,
                control=False,
            )

            folium.TileLayer(tiles=tiles, opacity=1,).add_to(base_map)
            base_map.add_to(hazard_map)
        else:
            hazard_map = plot_map_offline(x_mean, y_mean)

        # Create a LayerControl object
        layer_control = folium.LayerControl()

        cmap = branca.colormap.LinearColormap(
            colors=[
                "#67ac64",
                "#90bf5c",
                "#b2d155",
                "#dde049",
                "#ffff99",
                "#fed976",
                "#fcaf61",
                "#f17c4a",
                "#e05232",
                "#a50026",
            ],
            vmin=vmin,
            vmax=vmax,
        ).to_step(n=10)

        # Add caption to the map
        cmap.caption = f"Hazard Intensity ({hazard.units})"
        cmap.add_to(hazard_map)

        # Loop through each return period and create a separate heatmap layer
        for rp in return_periods:

            circle_group = folium.FeatureGroup(name=f"RP {rp}", overlay=False)
            for index, row in hazard_gdf.iterrows():
                if row[f"rp{rp}"] > 0:
                    folium.Circle(
                        location=[row["latitude"], row["longitude"]],
                        radius=2000,  # 2 km in meters
                        color=None,  # No outline
                        fill_color=cmap(row[f"rp{rp}"]),
                        fill=True,
                        fill_opacity=0.7,
                        opacity=None,  # No outline
                        popup=folium.Popup(
                            html=f"Intensity: {row[f'rp{rp}']:.2f}({hazard.units})",
                            max_width=150,
                        ),
                    ).add_to(circle_group)
            circle_group.add_to(hazard_map)

        # Add the LayerControl object to the map
        hazard_map.add_child(layer_control)

        # Add custom JavaScript to limit zoom levels
        min_zoom = 5
        max_zoom = 9
        zoom_limit_js = f"""
            <script>
                function limitZoomLevels() {{
                    var map = {hazard_map.get_name()};
                    map.options.minZoom = {min_zoom};
                    map.options.maxZoom = {max_zoom};
                    map.on('zoomend', function() {{
                        if (map.getZoom() < map.options.minZoom) {{
                            map.setZoom(map.options.minZoom);
                        }} else if (map.getZoom() > map.options.maxZoom) {{
                            map.setZoom(map.options.maxZoom);
                        }}
                    }});
                }}
                document.addEventListener("DOMContentLoaded", limitZoomLevels);
            </script>
        """

        # Add the JavaScript function to the header
        hazard_map.get_root().header.add_child(folium.Element(zoom_limit_js))

        # Add custom JavaScript to click RP 10 preselected layer
        click_rp10_js = f"""
            <script>
                function clickRp10() {{
                    var xpath = "//span[text()=' RP 10']//preceding-sibling::input[contains(@class, 'leaflet-control-layers-selector')]";
                    var iterator = document.evaluate(xpath, document, null, XPathResult.UNORDERED_NODE_ITERATOR_TYPE, null);
                    var input = iterator.iterateNext();

                    if (input) {{
                        input.click();
                    }} else {{
                        setTimeout(clickRp10, 100);
                    }}
                }}

                document.addEventListener("DOMContentLoaded", clickRp10);
            </script>
        """

        # Add the JavaScript function to the header
        hazard_map.get_root().header.add_child(folium.Element(click_rp10_js))

        # Save the map to an HTML file
        hazard_html_file = Path(CLIENT_ASSETS_DIR, "hazard_nuts2.html")
        hazard_map.save(hazard_html_file)

        if online:
            save_map_as_image(map_type="hazard", html_path=hazard_html_file)
        else:
            replace_links_with_local(hazard_html_file, repr=True)

            hazard_html_screenshot_file = Path(
                CLIENT_ASSETS_DIR, "hazard_nuts2_sc.html")
            hazard_map.save(hazard_html_screenshot_file)
            replace_links_with_local(hazard_html_screenshot_file, repr=False)

            save_map_as_image(map_type="hazard",
                              html_path=hazard_html_screenshot_file)

        return hazard_map
    except Exception as exc:
        # print(exc)
        pass


def plot_impact(impact: Impact):
    """
    Compute and plot exceedance impact maps in nuts2 level for different return periods.

    Parameters
    ----------
    impact_output: gpd.GeoDataFrame, required
        GeoDataFrame
    kwargs : optional

    Returns
    -------
    Saves impact plot html folium maps.
    """
    start_time = time()
    impact_output_nuts2 = calculate_impact_output_per_nuts2(impact)
    grouped = impact_output_nuts2.groupby("RP", sort=False, as_index=False)
    countries = list(impact_output_nuts2["country"].unique())
    polygons = get_polygons(countries)

    # Calculate vmin and vmax
    vmin = 0
    vmax = impact_output_nuts2["sum_loss"].max()

    x_mean = polygons["geometry"].centroid.y.mean()
    y_mean = polygons["geometry"].centroid.x.mean()

    try:
        online = is_connected()

        if online:
            # Create a Folium map object
            impact_map = folium.Map(
                location=[x_mean, y_mean],
                tiles="CartoDB Positron",
                zoom_start=6,
                control_scale=True,
                prefer_canvas=True,
            )

            # Add an always visible base map to avoid hiding when selecting different layers.
            base_map = folium.FeatureGroup(
                name="Basemap",
                overlay=True,
                control=False,
            )
            folium.TileLayer(tiles="CartoDB Positron",
                             opacity=1).add_to(base_map)
            base_map.add_to(impact_map)

        else:
            impact_map = plot_map_offline(x_mean, y_mean)

        # Create a LayerControl object
        layer_control = folium.LayerControl()

        # Define the color scale
        threshold_scale = np.linspace(vmin, vmax)

        # Loop through each group of data
        for name, group in grouped:
            impact_present_output_nuts2_rp = impact_output_nuts2[
                impact_output_nuts2["RP"] == name
            ]
            group = polygons.merge(
                impact_present_output_nuts2_rp,
                how="left",
                on=["nuts2", "nuts_description", "country"],
            )

            # Add a Choropleth layer for each group
            choropleth = folium.Choropleth(
                geo_data=group,
                name=name,
                data=group,
                columns=["nuts_description", "sum_loss"],
                key_on="feature.properties.nuts_description",
                threshold_scale=threshold_scale,
                fill_opacity=0.4,
                fill_color="RdYlGn_r",
                nan_fill_color="grey",
                line_opacity=0.2,
                legend_name="Impact (EUR)",
                highlight=True,
                overlay=False,
            )
            # Add the Choropleth layer to the map
            choropleth.add_to(impact_map)

            # Hackey way to delete the legend.
            for key in choropleth._children:
                if key.startswith("color_map"):
                    del choropleth._children[key]

            # Add tooltip upon clicking
            folium.GeoJsonPopup(
                fields=["country", "nuts_description", "nuts2", "sum_loss"],
                aliases=["Country", "NUTS2", "NUTS2 code", "Losses"],
            ).add_to(choropleth.geojson)

        # Add the LayerControl object to the map
        layer_control.add_to(impact_map)

        # Add custom JavaScript to limit zoom levels
        min_zoom = 5
        max_zoom = 9
        zoom_limit_js = f"""
        <script>
        function limitZoomLevels() {{
            var map = {impact_map.get_name()};
            map.options.minZoom = {min_zoom};
            map.options.maxZoom = {max_zoom};
            map.on('zoomend', function() {{
                if (map.getZoom() < map.options.minZoom) {{
                    map.setZoom(map.options.minZoom);
                }} else if (map.getZoom() > map.options.maxZoom) {{
                    map.setZoom(map.options.maxZoom);
                }}
            }});
        }}
        document.addEventListener("DOMContentLoaded", limitZoomLevels);
        </script>
        """

        # Add the JavaScript function to the header
        impact_map.get_root().header.add_child(folium.Element(zoom_limit_js))

        # Add custom JavaScript to click RP 10 preselected layer
        click_rp10_js = f"""
            <script>
                function clickRp10() {{
                    var xpath = "//span[text()=' RPL 10']//preceding-sibling::input[contains(@class, 'leaflet-control-layers-selector')]";
                    var iterator = document.evaluate(xpath, document, null, XPathResult.UNORDERED_NODE_ITERATOR_TYPE, null);
                    var input = iterator.iterateNext();

                    if (input) {{
                        input.click();
                    }} else {{
                        setTimeout(clickRp10, 100);
                    }}
                }}

                document.addEventListener("DOMContentLoaded", clickRp10);
            </script>
        """

        # Add the JavaScript function to the header
        impact_map.get_root().header.add_child(folium.Element(click_rp10_js))

        # Save the map to an HTML file
        impact_html_file = Path(CLIENT_ASSETS_DIR, "impact_nuts2.html")
        impact_map.save(impact_html_file)

        if not online:
            replace_links_with_local(impact_html_file, True)

        # print(
        #     "\033[92m"
        #     + f"Finished plotting impact maps in {time() - start_time}sec."
        #     + "\033[0m"
        # )

        return impact_map
    except Exception as exception:
        # print(f"Exception while plotting impact. More info: {exception}")
        pass


def plot_stacked_aggregated_exposure(df: pd.DataFrame):
    """
    Compute and plot the stacked aggregated exposure.

    Parameters
    ----------
    df: pandas.DataFrame, required
        pandas DataFrame containing the exposure data to plot the aggregated exposure.

    Returns
    -------
    Saves stacked aggregated exposure plot figure.
    """
    try:
        dft = df.set_index("Country").T
        axe = dft.plot(
            kind="bar",
            stacked=True,
            rot=0,
            title="Stacked aggregated values per country",
            figsize=(13, 9),
        )
        for x in axe.containers:
            axe.bar_label(
                x, label_type="edge", weight="semibold", fmt="%.0f€", padding=2
            )
        axe.get_figure().savefig(
            fname=Path(TEMP_DIR, "aggregated_stacked_exposure.jpg"),
            bbox_inches="tight",
        )
    except Exception as exception:
        # print(f"Exception while plotting aggregated exposure. More info: {exception}")
        pass


def plot_exceedance_freq_curve(baseline: bool = True):
    """
    Compute and plot the exceedance frequency curve. The impact data is based on
    the temp impact_output_aggregated_baseline.xlsx that is generated while calculating
    impact.

    Parameters
    ----------
    baseline: bool, optional
        True to calculate baseline or False to calculate future projection.

    Returns
    -------
    Saves exceedance frequency plot figure.
    """
    try:
        impact_output_aggregated = pd.read_feather(
            Path(TEMP_DIR, "impact_output_aggregated_baseline.feather")
        )
        impact_output_aggregated = impact_output_aggregated[["RP", "sum_loss"]]
        impact_output_aggregated.plot(
            x="RP",
            y="sum_loss",
            grid=True,
            xlabel="Return period (year)",
            ylabel="Impact (EUR)",
            title="Current aggregated EP curve",
        ).get_figure().savefig(
            fname=Path(TEMP_DIR, "exceedance_freq_curve_present.jpg"),
            bbox_inches="tight",
        )

        if not baseline:
            future_impact_output_aggregated = pd.read_feather(
                Path(TEMP_DIR, "impact_output_aggregated_future.feather")
            )
            future_impact_output_aggregated = future_impact_output_aggregated[
                ["RP", "sum_loss"]
            ]
            future_impact_output_aggregated.plot(
                x="RP",
                y="sum_loss",
                grid=True,
                xlabel="Return period (year)",
                ylabel="Impact (EUR)",
                title="Future aggregated EP curve",
            ).get_figure().savefig(
                fname=Path(TEMP_DIR, "exceedance_freq_curve_future.jpg"),
                bbox_inches="tight",
            )
    except Exception as exception:
        # print(
        #     f"Exception while plotting exceedance frequency curve. More info: {exception}"
        # )
        pass


def get_cmap(colormap: str, light: float = None) -> Colormap:
    """
    Helper method to generate the colormap for the maps.

    Parameters
    ----------
    colormap: str, required
        Parameter for the matplotlib.cm.get_cmap method, to get the specified
        global colormap object.
    light: float: optional.
        If selected the colormap will fade. Values must be between [0,1].

    Returns
    -------
    Get the colormap instance.
    """
    cmap = cm.get_cmap(colormap).copy()
    newcmp = ListedColormap(cmap(np.linspace(0.15, 1, 256)))
    if light:
        return cmap_map(lambda x: x / 2 + light, newcmp)
    else:
        return newcmp


def cmap_map(function, cmap):
    """
    Applies function (which should operate on vectors of shape 3: [r, g, b]),
    on colormap cmap. This routine will break any discontinuous points in a colormap.

    Parameters
    ----------
    function: Any, required
        Parameter for the matplotlib.cm.get_cmap method, to get the specified
        global colormap object.
    cmap: colors.Colormap, required.
        Global colormap object

    Returns
    -------
    Get the colormap instance.
    """
    cdict = cmap._segmentdata
    step_dict = {}
    # First get the list of points where the segments start or end
    for key in ("red", "green", "blue"):
        step_dict[key] = list(map(lambda x: x[0], cdict[key]))
    step_list = sum(step_dict.values(), [])
    step_list = np.array(list(set(step_list)))
    # Then compute the LUT, and apply the function to the LUT
    def reduced_cmap(step): return np.array(cmap(step)[0:3])
    old_LUT = np.array(list(map(reduced_cmap, step_list)))
    new_LUT = np.array(list(map(function, old_LUT)))
    # Now try to make a minimal segment definition of the new LUT
    cdict = {}
    for i, key in enumerate(["red", "green", "blue"]):
        this_cdict = {}
        for j, step in enumerate(step_list):
            if step in step_dict[key]:
                this_cdict[step] = new_LUT[j, i]
            elif new_LUT[j, i] != old_LUT[j, i]:
                this_cdict[step] = new_LUT[j, i]
        colorvector = list(map(lambda x: x + (x[1],), this_cdict.items()))
        colorvector.sort()
        cdict[key] = colorvector

    return LinearSegmentedColormap("colormap", cdict, 1024)


def save_map_as_image(
    map_type: str, html_path: str, layers: tuple = (10, 100, 500)
) -> None:
    """
    Saves screenshots of a map rendered by a HTML file with Leaflet library for different map types and RP levels.

    Parameters
    ----------
    map_type : str
        The type of map, either 'exposure' or 'hazard'.
    html_path : str
        The path to the HTML file containing the map rendered by Leaflet library.
    layers : tuple, optional
        A tuple containing the RP levels to save the map screenshots for. Default is (10, 100, 500).

    Returns
    ----------
    None.

    Examples
    ----------
    >>> save_map_as_image('hazard', 'C:/maps/hazard_map.html', (10, 100, 500))
    >>> save_map_as_image('exposure', 'C:/maps/exposure_map.html')

    Notes
    ----------
    This function uses Selenium with Google Chrome driver to render and interact with the map. It first opens the HTML file
    in headless Chrome browser, locates the layer control on the map and clicks on it to show the options, then selects the
    specified map type and RP levels by clicking on the corresponding labels. Finally, it saves screenshots of the map to the specified image paths.
    """
    screenshot_saved = False
    try:
        options_chrome = ChromeOptions()
        options_chrome.add_argument("--headless")
        options_chrome.add_argument("--disable-gpu")

        options_firefox = FirefoxOptions()
        options_firefox.add_argument("--headless")

        options_edge = EdgeOptions()
        options_edge.use_chromium = True
        options_edge.add_argument("--headless")

        browsers = [
            {"driver": webdriver.Chrome, "options": options_chrome},
            {"driver": webdriver.Firefox, "options": options_firefox},
            {"driver": webdriver.Edge, "options": options_edge},
        ]

        driver = None
        for browser in browsers:
            try:
                driver = browser["driver"](options=browser["options"])
                # Load the HTML file in the browser
                driver.get(Path(html_path).resolve().as_uri())
                sleep(10)  # Wait for 10 seconds for the page to load
                break
            except Exception as e:
                print(
                    f"Failed to initialize {browser['driver'].__name__}: {e}")

        if driver is None:
            # Check the type of map
            if map_type == "exposure":
                layer = "nuts2"
                image_path = Path(CLIENT_ASSETS_DIR,
                                  f"exposure_europe_{layer}.png")
                img = Image.new('RGB', (500, 500), color=(255, 255, 255))
                img.save(image_path, "PNG")
            elif map_type == "hazard":
                for layer in layers:
                    # Save a screenshot of the map with the current RP level
                    image_path = Path(CLIENT_ASSETS_DIR,
                                      f"hazard_nuts2_rp{layer}.png")
                    # Generate a blank image
                    img = Image.new('RGB', (500, 500), color=(255, 255, 255))
                    img.save(image_path, "PNG")
            return

        # Check the type of map
        if map_type == "exposure":
            # Select the 'nuts2' layer for exposure maps
            layer = "nuts2"
            # Save a screenshot of the map with the current layer
            image_path = Path(CLIENT_ASSETS_DIR,
                              f"exposure_europe_{layer}.png")
            driver.save_screenshot(image_path)
            screenshot_saved = True
        elif map_type == "hazard":
            # Loop through each RP level in the provided tuple
            for layer in layers:
                # Save a screenshot of the map with the current RP level
                image_path = Path(CLIENT_ASSETS_DIR,
                                  f"hazard_nuts2_rp{layer}.png")
                driver.save_screenshot(image_path)
                screenshot_saved = True

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Quit the driver to release system resources
        if driver is not None:
            driver.quit()
        # If screenshot wasn't saved, create blank images
        if not screenshot_saved:
            if map_type == "exposure":
                layer = "nuts2"
                image_path = Path(CLIENT_ASSETS_DIR,
                                  f"exposure_europe_{layer}.png")
                img = Image.new('RGB', (500, 500), color=(255, 255, 255))
                img.save(image_path, "PNG")
            elif map_type == "hazard":
                for layer in layers:
                    # Save a screenshot of the map with the current RP level
                    image_path = Path(CLIENT_ASSETS_DIR,
                                      f"hazard_nuts2_rp{layer}.png")
                    # Generate a blank image
                    img = Image.new('RGB', (500, 500), color=(255, 255, 255))
                    img.save(image_path, "PNG")
