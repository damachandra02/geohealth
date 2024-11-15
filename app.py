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

# App title with description
st.title("🌡️ Temperature Data Visualization Across Karnataka")
st.markdown(
    """
    Welcome to the Karnataka Temperature Dashboard! 
    Select a date to view temperature distribution across Karnataka's districts, 
    or explore the temperature trends over time in specific districts.
    """
)

# Sidebar controls for customization
st.sidebar.header("Map Options")
selected_date = st.sidebar.date_input("Choose a Date:", date.today())

# Checkbox to show state border
show_state_border = st.sidebar.checkbox("Highlight State Border", value=True)
# Checkbox to show district borders
show_district_borders = st.sidebar.checkbox("Highlight District Borders", value=True)

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

# Define custom color scale and range
color_scale = "Turbo"

# Create the choropleth map using Plotly
fig = px.choropleth_mapbox(
    map_data,
    geojson=map_data.set_geometry(map_data.geometry).__geo_interface__,
    locations=map_data.index,  # Use index for locations since we merged the data
    color="temperature",
    color_continuous_scale=color_scale,
    range_color=(filtered_data["temperature"].min(), filtered_data["temperature"].max()),
    hover_name="district",
    hover_data={"temperature": True},
    mapbox_style="open-street-map",
    center={"lat": 15.3173, "lon": 75.7139},
    zoom=6,
    featureidkey="properties.district"
)

# Conditionally add district borders in black
if show_district_borders:
    fig.update_traces(marker_line_width=1.5, marker_line_color="black")  # District borders

# Conditionally add state border in black
if show_state_border:
    fig.update_geos(fitbounds="locations", visible=True)
    fig.update_layout(geo=dict(
        projection_scale=5.5,  # Scale map to state level
        visible=True,
        bgcolor='rgba(0,0,0,0)',  # Transparent background for geos
        showframe=True,
        framecolor="black",  # State border color set to black
        framewidth=3          # State border thickness
    ))

# Update layout with aesthetic margins and padding
fig.update_layout(
    title="District-wise Temperature Map",
    title_x=0.5,
    margin={"r":0, "t":40, "l":0, "b":0},
    coloraxis_colorbar=dict(
        title="Temperature (°C)",
        title_side="right",
        thicknessmode="pixels",
        thickness=15,
        lenmode="pixels",
        len=250,
    )
)

# Display map
st.plotly_chart(fig)

# Optional: Add temperature trend over time (line chart) with improved styling
if st.sidebar.checkbox("Show Temperature Trend Analysis Over Time"):
    st.subheader("📈 Temperature Trend Analysis")
    district = st.selectbox("Select District", temp_data["district"].unique())
    trend_data = temp_data[temp_data["district"] == district]
    
    # Line chart with improved aesthetics
    fig_line = px.line(
        trend_data,
        x="date",
        y="temperature",
        title=f"Temperature Trend for {district}",
        labels={"date": "Date", "temperature": "Temperature (°C)"},
        template="plotly_white",
        markers=True,
    )
    fig_line.update_traces(line=dict(color="darkorange", width=2), marker=dict(size=4))
    fig_line.update_layout(title_x=0.5, margin={"r":10, "t":50, "l":10, "b":10})

    st.plotly_chart(fig_line)
