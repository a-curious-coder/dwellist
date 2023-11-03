import dash
import pandas as pd
import plotly.express as px
from dash import dcc, html
from dash.dependencies import Input, Output

# Assuming data is your DataFrame containing the room data
# Load your data
data = pd.read_csv("test.csv")

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the app layout
app.layout = html.Div(
    [
        # Dropdown for filtering options
        dcc.Dropdown(
            id="filter-dropdown",
            options=[{"label": column, "value": column} for column in data.columns],
            placeholder="Select a filter option",
        ),
        # Map display
        dcc.Graph(id="map"),
    ]
)


# Define callback to update the map based on filter selection
@app.callback(Output("map", "figure"), [Input("filter-dropdown", "value")])
def update_map(selected_column):
    filtered_data = (
        data if selected_column is None else data[data[selected_column].notnull()]
    )
    fig = px.scatter_mapbox(
        filtered_data,
        lat="latitude",
        lon="longitude",
        text="area",
        center={
            "lat": filtered_data["latitude"].mean(),
            "lon": filtered_data["longitude"].mean(),
        },
        zoom=12,
        height=600,
    )
    fig.update_layout(mapbox_style="open-street-map")
    return fig


# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
