# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

launch_sites = spacex_df['Launch Site'].unique()
launch_site_options = [{'label': 'All Sites', 'value': 'ALL'}]
launch_site_options += [{'label': site1, 'value': site1} for site1 in launch_sites]

slider_marks = {}
for i in range(0, 10001, 2500):
    slider_marks[i] = i 

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                    options=launch_site_options,
                                    value='ALL',
                                    placeholder='place holder here',
                                    searchable=True
                                ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(
                                    id='payload-slider',
                                    min=0, 
                                    max=10000, 
                                    step=1000,
                                    marks= slider_marks,
                                    value=[min_payload, max_payload]
                                ),
                                html.Br(),
                                html.Br(),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output

# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    filtered_df = spacex_df
    if entered_site == 'ALL':
        success_by_site = spacex_df[spacex_df['class'] == 1].groupby('Launch Site').size()
        fig = px.pie(
            success_by_site, 
            values = success_by_site.values,
            names = success_by_site.index,
            title='Total Success Launch by site'
        )
        # return fig
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site] 
        success_count = filtered_df[filtered_df['class'] == 1].shape[0]
        failure_count = filtered_df[filtered_df['class'] == 0].shape[0]
        fig = px.pie(
            values=[success_count, failure_count],
            names=['Success', 'Failure'],
            title=f'Success vs Failure for {entered_site}'
        )
    return fig
        
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [
        Input(component_id = 'site-dropdown', component_property='value'),
        Input(component_id = 'payload-slider', component_property='value')
    ]
)
def update_scatter_chart(entered_site, payload_range):
    low, high = payload_range[0], payload_range[1]
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) &
        (spacex_df['Payload Mass (kg)'] <= high)
    ]

    if entered_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
    
    fig = px.scatter(
        filtered_df, 
        x = 'Payload Mass (kg)',
        y = 'class',
        color = 'Booster Version Category',
        title = 'Correlation between Payload Mass and Launch Success',
        labels = {
            'Payload Mass (kg)': 'Payload Mass (kg)',
            'class': 'Launch Outcome',
            'Booster Version Category': 'Booster Version'
        },
        hover_data=['Launch Site', 'Booster Version']
    )
    fig.update_layout(
        yaxis=dict(
            tickmode='array',
            tickvals=[0, 1],
            ticktext=['Failure', 'Success']
        )
    )

    # Update marker size for better visibility
    fig.update_traces(marker=dict(size=12, opacity=0.7, line=dict(width=1, color='DarkSlateGrey')))
    
    return fig

# Run the app
if __name__ == '__main__':
    app.run()
