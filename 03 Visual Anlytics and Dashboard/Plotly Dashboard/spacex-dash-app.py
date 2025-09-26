# spacex_dash_app.py
# Completed Plotly Dash app for the SpaceX lab

import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = int(spacex_df['Payload Mass (kg)'].max())
min_payload = int(spacex_df['Payload Mass (kg)'].min())

# Create a dash application
app = dash.Dash(__name__)
server = app.server  # for deployment if needed

# Helper: dropdown options (All + individual sites)
site_options = [{'label': 'All Sites', 'value': 'ALL'}] + \
               [{'label': s, 'value': s} for s in sorted(spacex_df['Launch Site'].unique())]

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),

    # TASK 1: Launch Site dropdown
    dcc.Dropdown(
        id='site-dropdown',
        options=site_options,
        value='ALL',
        placeholder="Select a Launch Site here",
        searchable=True
    ),
    html.Br(),

    # TASK 2: Pie chart
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),

    # TASK 3: Payload RangeSlider
    dcc.RangeSlider(
        id='payload-slider',
        min=0, max=10000, step=1000,
        marks={
            0: '0',
            2500: '2500',
            5000: '5000',
            7500: '7500',
            10000: '10000'
        },
        value=[min_payload, max_payload]
    ),
    html.Br(),

    # TASK 4: Scatter chart
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])


# TASK 2:
# Callback to update pie chart based on selected site
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        # Sum successes per site (class == 1)
        df_grouped = spacex_df.groupby('Launch Site')['class'].sum().reset_index()
        fig = px.pie(df_grouped, values='class', names='Launch Site',
                     title='Total Successful Launches by Site')
    else:
        # For a specific site: success vs failure counts
        df_site = spacex_df[spacex_df['Launch Site'] == selected_site]
        counts = df_site['class'].value_counts().reset_index()
        counts.columns = ['class', 'count']
        counts['outcome'] = counts['class'].map({1: 'Success', 0: 'Failure'})
        fig = px.pie(counts, values='count', names='outcome',
                     title=f'Success vs Failure for site {selected_site}')
    return fig


# TASK 4:
# Callback to update scatter chart based on site + payload slider
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_chart(selected_site, payload_range):
    low, high = payload_range
    # Filter by payload range
    dff = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) &
                    (spacex_df['Payload Mass (kg)'] <= high)]

    # If a specific site is selected, filter by site too
    if selected_site != 'ALL':
        dff = dff[dff['Launch Site'] == selected_site]

    # Scatter: payload vs class, colored by booster category
    fig = px.scatter(
        dff,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        hover_data=['Launch Site', 'Payload Mass (kg)', 'Booster Version Category'],
        title=('Payload vs. Outcome (class=1 success, class=0 failure)'
               + (f' — {selected_site}' if selected_site != 'ALL' else ' — All Sites'))
    )

    # Improve y-axis ticks to emphasize 0/1
    fig.update_yaxes(tickmode='array', tickvals=[0, 1], ticktext=['Failure (0)', 'Success (1)'])
    return fig


# Run the app
if __name__ == '__main__':
    app.run(debug=True, port=8050)
