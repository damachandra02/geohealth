import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
from datetime import date

# Load GeoJSON for Karnataka districts (use st.cache_resource for static data)
@st.cache_resource
def load_geojson():
    return gpd.read_file("data/karnataka_districts.geojson")

# Load temperature data (use st.cache_data for frequently accessed data)
@st.cache_data
def load_temperature_data():
    return pd.read_csv("data/temperature_data.csv")

# App title
st.title("Temperature Data Visualization Across Karnataka")

# Date picker for temperature data
selected_date = st.date_input("Select a Date", date.today())

# Load data
geojson_data = load_geojson()
temp_data = load_temperature_data()

# Filter temperature data for the selected date
filtered_data = temp_data[temp_data['date'] == selected_date.strftime('%Y-%m-%d')]

# Clean and standardize district names in both datasets
geojson_data['district'] = geojson_data['district'].str.strip().str.upper()
filtered_data['district'] = filtered_data['district'].str.strip().str.upper()

# Merge data with GeoJSON
map_data = geojson_data.merge(filtered_data, on="district", how="left")

# Create the choropleth map using Plotly
fig = px.choropleth_mapbox(
    map_data,
    geojson=map_data.geometry,
    locations=map_data.index,  # Use index for locations since we merged the data
    color="temperature",
    color_continuous_scale="Viridis",
    range_color=(filtered_data["temperature"].min(), filtered_data["temperature"].max()),
    hover_name="district",
    hover_data={"temperature": True},
    mapbox_style="carto-positron",
    center={"lat": 15.3173, "lon": 75.7139},
    zoom=6,
)

# Update layout
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

# Display map
st.plotly_chart(fig)

# Optional: Add temperature trend over time (line chart)
if st.checkbox("Show temperature trend analysis over time"):
    district = st.selectbox("Select District", temp_data["district"].unique())
    trend_data = temp_data[temp_data["district"] == district]
    st.line_chart(trend_data.set_index("date")["temperature"])