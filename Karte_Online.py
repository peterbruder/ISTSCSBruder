import streamlit as st
import folium
import geopandas as gpd
from streamlit_folium import folium_static
import os
import numpy as np
import mapclassify
import branca.colormap as cm
from shapely.geometry import LineString
from folium.features import DivIcon
from PIL import Image
import math
from shapely.geometry import LineString, MultiLineString



#Focussing on Passenger Needs
st.title("Focusing on Passenger Needs ")
st.subheader("How Can On-Demand Ridepooling Data Make Transport Planning More User-Centered?")
st.markdown(
    '<span style="color:gray">Peter Bruder (FH Münster), Robin Kersten (FH Münster), Jeanette Klemmer (FH Münster), Dennis Schöne (RVM GmbH)</span>',
    unsafe_allow_html=True
)


with st.expander(label="Overview of G-Mobil"):
    # Function to load shapefiles from a directory
    def load_shapefile(file_path):
        if os.path.exists(file_path):
            return gpd.read_file(file_path)
        else:
            st.error(f"File not found: {file_path}")
            return None

    # Define file paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    betriebsgebiet_path = os.path.join(base_dir, "Betriebsgebiet.shp")
    gronau_bhf_path = os.path.join(base_dir, "GronauBhf.shp")
    haltestellen_path = os.path.join(base_dir, "Haltestellen.shp")
    Buslinien_path = os.path.join(base_dir, "FrühereBuslinie.shp")
    taxibuslinien_path = os.path.join(base_dir, "FrühereTaxibuslinie.shp")

    # Streamlit App
    st.header("Overview of Mein G-Mobil")

    # Load Haltestellen to determine map center
    haltestellen = load_shapefile(haltestellen_path)
    if haltestellen is not None and not haltestellen.empty:
        centroid = [haltestellen.geometry.y.mean(), haltestellen.geometry.x.mean()]
        zoom_start = 12.3
    else:
        centroid = [51.933, 7.628]
        zoom_start = 12.3

    # Initialize Second Map
    m = folium.Map(
        location=centroid, 
        zoom_start=zoom_start, 
        tiles="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", 
        attr="© CartoDB",
        name="CartoDB Positron"
    )


    # Load and plot Betriebsgebiet (Polygon)
    betriebsgebiet = load_shapefile(betriebsgebiet_path)
    if betriebsgebiet is not None:
        folium.GeoJson(betriebsgebiet, name="Operting area", style_function=lambda x: {'fillColor': 'green', 'color': 'blue', 'weight': 1, 'fillOpacity': 0.05 }).add_to(m)


    # Feature Group for Haltestellen
    haltestellen_group = folium.FeatureGroup(name="G-Mobil stops")
    if haltestellen is not None:
        for idx, row in haltestellen.iterrows():
            color = "green" if row.get("Typ") == "physisch" else "blue"
            folium.CircleMarker(
                location=[row.geometry.y, row.geometry.x],
                radius=1,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=1.0,
                popup=row.get("Haltestell", "Haltestelle")
            ).add_to(haltestellen_group)
        haltestellen_group.add_to(m)
    
    # Load and group Buslinien (Lines)
    buslinien_group = folium.FeatureGroup(name="Scheduled bus lines (2021)")
    buslinien = load_shapefile(Buslinien_path)
    
    if buslinien is not None:
        colors =  ["purple"]  # Example colors
    
        # Stelle sicher, dass die Geometrie gültig ist und transformiere ins richtige Koordinatensystem
        buslinien = buslinien.to_crs(epsg=4326)
        buslinien = buslinien[buslinien.geometry.notnull() & ~buslinien.geometry.is_empty]
    
        for idx, row in buslinien.iterrows():
            geom = row.geometry
            color = colors[idx % len(colors)]
    
            # MultiLineString auf einzelne Linien zerlegen
            if isinstance(geom, MultiLineString):
                lines = geom.geoms
            elif isinstance(geom, LineString):
                lines = [geom]
            else:
                continue  # Unsupported geometry type
    
            for line in lines:
                coords = [(lat, lon) for lon, lat in line.coords]  # folium erwartet (lat, lon)
                folium.PolyLine(
                    coords,
                    color=color,
                    weight=2,
                    opacity=0.8
                ).add_to(buslinien_group)
    
        buslinien_group.add_to(m)

    # Load and group Taxibuslinien (Lines)
    taxibuslinien_group = folium.FeatureGroup(name="Taxi-buslines (2021)")
    taxibuslinien = load_shapefile(taxibuslinien_path)
    if taxibuslinien is not None:
        colors = ["brown", "cyan", "magenta", "yellow", "pink"]  # Example colors for Taxibuslinien
        for idx, row in taxibuslinien.iterrows():
            color = colors[idx % len(colors)]  # Assign colors based on index
            folium.GeoJson(
                row.geometry,
                style_function=lambda x, color=color: {'color': color, 'weight': 2, 'dashArray': '5, 5'}
            ).add_to(taxibuslinien_group)
        taxibuslinien_group.add_to(m)


    # Add Layer Control
    folium.LayerControl().add_to(m)

    # Display Map
    folium_static(m)


######################
# Tagesganglinien


with st.expander(label="Applications of Ridepooling Data"):

    st.header("Temporal Distribution of Requests and Bookings")
    # Bildpfad
    image_path = r"heatmap_diagrams_ppt.png"

    # Bild laden und anzeigen
    if os.path.exists(image_path):
        image = Image.open(image_path)
        st.image(image,  use_container_width=True)
    else:
        st.error(f"Bild nicht gefunden: {image_path}")


    #Karte Ein&Ausstiege
    ######################################################################################



    # Function to load shapefiles from a directory
    def load_shapefile(file_path):
        if os.path.exists(file_path):
            return gpd.read_file(file_path)
        else:
            st.error(f"File not found: {file_path}")
            return None

    # Define file paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    betriebsgebiet_path = os.path.join(base_dir, "Betriebsgebiet.shp")
    haltestellen_path = os.path.join(base_dir, "Haltestellen.shp")
    g_mobil_ein_aus_path = os.path.join(base_dir, "G-Mobil_Ein-undAusstiege.shp")

    # Load Haltestellen to determine map center
    haltestellen = load_shapefile(haltestellen_path)
    if haltestellen is not None and not haltestellen.empty:
        centroid = [haltestellen.geometry.y.mean(), haltestellen.geometry.x.mean()]
        zoom_start = 12.3
    else:
        centroid = [51.933, 7.628]
        zoom_start = 12.3

    #######################################################################################################################################
    # Second Map - Ein- und Ausstiegen

    st.header("Spatial distribution of Pickups")
    # Initialize Second Map
    m2 = folium.Map(
        location=centroid, 
        zoom_start=zoom_start, 
        tiles="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", 
        attr="© CartoDB",
        name="CartoDB Positron"
    )

    # Load and plot Betriebsgebiet (Polygon) again for second map
    if betriebsgebiet is not None:
        folium.GeoJson(betriebsgebiet, name="Betriebsgebiet", style_function=lambda x: {'fillColor': 'green', 'color': 'blue', 'weight': 1, 'fillOpacity': 0.05 }).add_to(m2)


    # Load and plot G-Mobil Ein- und Ausstiege (Points) using Jenks Natural Breaks
    g_mobil_ein_aus = load_shapefile(g_mobil_ein_aus_path)
    if g_mobil_ein_aus is not None:
        values = g_mobil_ein_aus["Ein+Aussti"].values
        if len(values) > 5:
            classifier = mapclassify.JenksCaspall(values, k=5)
            bins = classifier.bins
        else:
            bins = np.linspace(min(values), max(values), 6)
        
        def get_radius(value):
            for i, bin_edge in enumerate(bins):
                if value <= bin_edge:
                    return (i + 1) * 1  # Increasing radius for visibility
            return 40
        
        for idx, row in g_mobil_ein_aus.iterrows():
            count = row.get("Ein+Aussti", 1)
            radius = get_radius(count)
            
            folium.CircleMarker(
                location=[row.geometry.y, row.geometry.x],
                radius=radius,
                color='black',
                weight=0.5,  # Reduce border thickness
                fill=True,
                fill_color='red',
                fill_opacity=0.2,  # Adjust transparency
                popup=folium.Popup(f"Einstiege: {count}", parse_html=True),
                tooltip=f"Einstiege: {count}"
            ).add_to(m2)

    # Display Second Map
    folium_static(m2)


    #####################################################################################################
    # Third Map - Ausstiege    
    st.header("Spatial distribution of Dropoffs")

    # Initialize Third Map
    m3 = folium.Map(
        location=centroid, 
        zoom_start=zoom_start, 
        tiles="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", 
        attr="© CartoDB",
        name="CartoDB Positron"
    )

    # Load and plot Betriebsgebiet (Polygon) again for third map
    if betriebsgebiet is not None:
        folium.GeoJson(betriebsgebiet, name="Betriebsgebiet", style_function=lambda x: {'fillColor': 'green', 'color': 'blue', 'weight': 1, 'fillOpacity': 0.05 }).add_to(m3)

    # Load and plot G-Mobil Ausstiege (Points) using Jenks Natural Breaks
    if g_mobil_ein_aus is not None:
        values = g_mobil_ein_aus["Ein+Auss_1"].values
        if len(values) > 5:
            classifier = mapclassify.JenksCaspall(values, k=5)
            bins = classifier.bins
        else:
            bins = np.linspace(min(values), max(values), 6)
        
        for idx, row in g_mobil_ein_aus.iterrows():
            count = row.get("Ein+Auss_1", 1)
            radius = get_radius(count)
            
            folium.CircleMarker(
                location=[row.geometry.y, row.geometry.x],
                radius=radius,
                color='black',
                weight=0.5,  # Reduce border thickness
                fill=True,
                fill_color='blue',
                fill_opacity=0.2,  # Adjust transparency
                popup=folium.Popup(f"Ausstiege: {count}", parse_html=True),
                tooltip=f"Ausstiege: {count}"
            ).add_to(m3)

    # Display Third Map
    folium_static(m3)


    ############################################################################
    # Hochfrequentierte Wegerelationen

    st.header("High Demand Route Relations")
    # Shapefile laden
    Wegerelationen_path = os.path.join(base_dir, "Wegerelationen.shp")
    Wegerelationen_gdf = load_shapefile(Wegerelationen_path)

    # In WGS 84 transformieren (für Folium notwendig)
    Wegerelationen_gdf = Wegerelationen_gdf.to_crs(epsg=4326)

    # Optional: Betriebsgebiet ebenfalls transformieren
    if betriebsgebiet is not None:
        betriebsgebiet = betriebsgebiet.to_crs(epsg=4326)

    # Sicherstellen, dass die Geometrie gültig ist
    Wegerelationen_gdf = Wegerelationen_gdf[Wegerelationen_gdf.geometry.notnull()]

    # Filter auf Fahrtenl_2 > 100
    Wegerelationen_gdf = Wegerelationen_gdf[Wegerelationen_gdf['Fahrtenl_2'] > 100]

    # Farbskala definieren (je höher der Wert, desto blauer)
    colormap = cm.linear.Reds_09.scale(
        Wegerelationen_gdf['Fahrtenl_2'].min(),
        Wegerelationen_gdf['Fahrtenl_2'].max()
    )

    # Kartenzentrum berechnen
    centroid_geom = Wegerelationen_gdf.unary_union.centroid
    centroid = (centroid_geom.y, centroid_geom.x)  # lat, lon

    # Karte initialisieren
    m5 = folium.Map(
        location=centroid,
        zoom_start=zoom_start,
        tiles="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
        attr="© CartoDB",
        name="CartoDB Positron"
    )

    # Betriebsgebiet (falls vorhanden) zur Karte hinzufügen
    if betriebsgebiet is not None:
        folium.GeoJson(
            betriebsgebiet,
            name="Betriebsgebiet",
            style_function=lambda x: {
                'fillColor': 'green',
                'color': 'blue',
                'weight': 1,
                'fillOpacity': 0.05
            }
        ).add_to(m5)

    # Linien und ggf. Pfeile zeichnen
    for _, row in Wegerelationen_gdf.iterrows():
        geom = row.geometry
        color = colormap(row['Fahrtenl_2'])

        # MultiLineString auf einzelne Linien zerlegen
        if isinstance(geom, MultiLineString):
            lines = geom.geoms
        elif isinstance(geom, LineString):
            lines = [geom]
        else:
            lines = []

        for line in lines:
            coords = list(line.coords)
            if len(coords) >= 2:
                # Koordinaten in (lat, lon) umwandeln
                latlon_coords = [(lat, lon) for lon, lat in coords]

                # Linie zeichnen
                folium.PolyLine(
                    latlon_coords,
                    color=color,
                    weight=4,
                    popup=f"Amount of Passengers per Relation: {row['Fahrtenl_2']}",
                    opacity=0.7
                ).add_to(m5)



    # Legende zur Karte hinzufügen
    colormap.caption = "Fahrten pro Relation"
    m5.add_child(colormap)

    # Karte in Streamlit anzeigen
    folium_static(m5)


    ##########################################################
    #Route Rerouting

    st.header("Route Rerouting – CW 43")

    # Shapefile laden
    routenumlegung_path = os.path.join(base_dir, "Routenumlegung_KW43_2.shp")
    routenumlegung_gdf = load_shapefile(routenumlegung_path)

    # In WGS 84 transformieren (für Folium notwendig)
    routenumlegung_gdf = routenumlegung_gdf.to_crs(epsg=4326)

    # Optional: Betriebsgebiet ebenfalls transformieren
    if betriebsgebiet is not None:
        betriebsgebiet = betriebsgebiet.to_crs(epsg=4326)

    # Sicherstellen, dass die Geometrie gültig ist
    routenumlegung_gdf = routenumlegung_gdf[routenumlegung_gdf.geometry.notnull()]

    # Filter auf Anzahl_Üb > 0
    routenumlegung_gdf = routenumlegung_gdf[routenumlegung_gdf['Anzahl_Üb'] > 0]

    # Farbskala definieren (z. B. Orange-Rot)
    colormap = cm.linear.OrRd_09.scale(
        routenumlegung_gdf['Anzahl_Üb'].min(),
        routenumlegung_gdf['Anzahl_Üb'].max()
    )

    # Kartenzentrum berechnen
    centroid_geom = routenumlegung_gdf.unary_union.centroid
    centroid = (centroid_geom.y, centroid_geom.x)  # lat, lon

    # Karte initialisieren
    m6 = folium.Map(
        location=centroid,
        zoom_start=zoom_start,
        tiles="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
        attr="© CartoDB",
        name="CartoDB Positron"
    )

    # Betriebsgebiet (falls vorhanden) zur Karte hinzufügen
    if betriebsgebiet is not None:
        folium.GeoJson(
            betriebsgebiet,
            name="Betriebsgebiet",
            style_function=lambda x: {
                'fillColor': 'green',
                'color': 'blue',
                'weight': 1,
                'fillOpacity': 0.05
            }
        ).add_to(m6)

    # Linien zeichnen
    for _, row in routenumlegung_gdf.iterrows():
        geom = row.geometry
        color = colormap(row['Anzahl_Üb'])

        # MultiLineString auf einzelne Linien zerlegen
        if isinstance(geom, MultiLineString):
            lines = geom.geoms
        elif isinstance(geom, LineString):
            lines = [geom]
        else:
            lines = []

        for line in lines:
            coords = list(line.coords)
            if len(coords) >= 2:
                latlon_coords = [(lat, lon) for lon, lat in coords]

                folium.PolyLine(
                    latlon_coords,
                    color=color,
                    weight=4,
                    opacity=0.7,
                    popup=f"Amount of overlapping Routes: {row['Anzahl_Üb']}"
                ).add_to(m6)

    # Legende zur Karte hinzufügen
    colormap.caption = "Amount of overlapping Routes (CW 43, 2023)"
    m6.add_child(colormap)

    # Karte in Streamlit anzeigen
    folium_static(m6)









###########################################################
#Biases

with st.expander(label="Possible Data Biases"):


    #Age and Gender
    st.header("Age Disparities:\nRidepooling Users vs. Inhabitants")

    # Bildpfad
    image_path = r"Age_and_Gender.png"

    # Bild laden und anzeigen
    if os.path.exists(image_path):
        image = Image.open(image_path)
        st.image(image, use_container_width=True)
    else:
        st.error(f"Bild nicht gefunden: {image_path}")

    #Heavy Users
    st.header("Usage Disparities:\nHeavy Users vs Irregular Users")

    # Bildpfad
    image_path = r"Nutzungsverteilung_Poster.png"

    # Bild laden und anzeigen
    if os.path.exists(image_path):
        image = Image.open(image_path)
        st.image(image,  use_container_width=True)
    else:
        st.error(f"Bild nicht gefunden: {image_path}")


    ###################
    # Verfügbarkeitsanalyse

    st.header("Spatial Availability:\nEfficiency vs. Basic Public Mobility")
    Verfügbarkeiten_path = os.path.join(base_dir, "Verfügbarkeitsanalyse.shp")

    verfuegbarkeiten_gdf = gpd.read_file(Verfügbarkeiten_path)

    # Werte von Dezimalform in Prozent umwandeln
    verfuegbarkeiten_gdf["Verfügbar"] = verfuegbarkeiten_gdf["Verfügbar"] * 100

    # Klassen für Verfügbarkeit definieren (10 Klassen: 0-10%, 10-20%, ..., 90-100%)
    bins = np.linspace(0, 100, 11)  # Erstellt die Intervalle 0-10, 10-20, ..., 90-100
    labels = np.arange(1, 11)  # Klassen von 1 bis 10
    verfuegbarkeiten_gdf["Verfügbarkeitsklasse"] = np.digitize(verfuegbarkeiten_gdf["Verfügbar"], bins, right=True)

    # Begrenzen der Klassenzuordnung auf Werte zwischen 1 und 10, um KeyError zu vermeiden
    verfuegbarkeiten_gdf["Verfügbarkeitsklasse"] = verfuegbarkeiten_gdf["Verfügbarkeitsklasse"].clip(1, 10)

    # Mittelpunkt für die Karte setzen (z. B. Mittelpunkt der Geometrien)
    centroid = [verfuegbarkeiten_gdf.geometry.centroid.y.mean(), verfuegbarkeiten_gdf.geometry.centroid.x.mean()]
    zoom_start = 12  # Passe den Zoomfaktor an

    # Map erstellen
    m4 = folium.Map(
        location=centroid,
        zoom_start=zoom_start,
        tiles="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
        attr="© CartoDB",
        name="CartoDB Positron"
    )

    # Umgekehrte Transparenzwerte (geringe Verfügbarkeit = hohe Transparenz)
    opacity_values = {
        1: 0.1, 2: 0.2, 3: 0.3, 4: 0.4, 5: 0.5,
        6: 0.6, 7: 0.7, 8: 0.8, 9: 0.9, 10: 1.0
    }

    # Polygone mit abgestufter Transparenz und Hover-Beschriftung hinzufügen
    for _, row in verfuegbarkeiten_gdf.iterrows():
        if np.isnan(row["Verfügbar"]):  # Falls Wert NaN ist
            fill_opacity = 0.0  # Komplett durchsichtig
            tooltip_text = "no inquiries"
        else:
            fill_opacity = opacity_values[row["Verfügbarkeitsklasse"]]
            tooltip_text = f"Verfügbarkeit: {row['Verfügbar']:.1f}%"

        folium.GeoJson(
            row.geometry,
            name=f"Verfügbarkeit {row['Verfügbarkeitsklasse']*10-10} - {row['Verfügbarkeitsklasse']*10} %",
            style_function=lambda x, opacity=fill_opacity: {
                'fillColor': 'green',  # Grün als Hauptfarbe
                'color': 'black',  # Randfarbe der Polygone
                'weight': 0.2,
                'fillOpacity': opacity  # Transparenz basierend auf Verfügbarkeitsklasse oder NaN (0.0)
            },
            tooltip=tooltip_text  # Hover-Beschriftung
        ).add_to(m4)

    # Map in Streamlit anzeigen
    folium_static(m4)


