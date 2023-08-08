# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                             options=[
                                                 {'label': 'All Sites', 'value': 'ALL'},
                                                 {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                                 {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                                                 {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                                 {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
                                             ],
                                             value='ALL',  # Default selected value
                                             placeholder="Select a Launch Site here",
                                             searchable=True
                                             ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                                min=0, max=10000, step=1000,
                                                value=[min_payload, max_payload],
                                                marks={0: '0 Kg', 10000: '10000 Kg'}
                                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])


# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # For 'ALL' sites, calculate the percentage of successful launches per site
        success_counts = spacex_df[spacex_df['class'] == 1].groupby('Launch Site').size().reset_index(name='Counts')
        success_counts['Percentage'] = (success_counts['Counts'] / success_counts['Counts'].sum()) * 100

        fig = px.pie(success_counts, names='Launch Site', values='Percentage',
                     title='Total Success Launches for All Sites'
                     )
        return fig
    else:
        # For a specific launch site, filter the dataframe and render a pie chart
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        success_counts = filtered_df[filtered_df['class'] == 1].shape[0]
        failed_counts = filtered_df[filtered_df['class'] == 0].shape[0]
        total_counts = success_counts + failed_counts
        success_percentage = (success_counts / total_counts) * 100
        failed_percentage = 100 - success_percentage
        labels = ['Success', 'Failed']
        values = [success_percentage, failed_percentage]
        fig = px.pie(names=labels, values=values,
                     title=f'Total Success Launches {entered_site}'
                     )
        return fig


# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'),
              Input(component_id='payload-slider', component_property='value'))
def get_scatter_chart(entered_site, payload_range):
    if entered_site == 'ALL':
        # For 'ALL' sites, use all rows in the dataframe to render a scatter chart
        filtered_df = spacex_df[
            (spacex_df['Payload Mass (kg)'] >= payload_range[0]) & (spacex_df['Payload Mass (kg)'] <= payload_range[1])
        ]
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', color='Booster Version Category',
                         title='Payload vs. Launch Outcome (All Sites)')
        return fig
    else:
        # For a specific launch site, filter the dataframe and render a scatter chart
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        filtered_df = filtered_df[
            (filtered_df['Payload Mass (kg)'] >= payload_range[0]) & (filtered_df['Payload Mass (kg)'] <= payload_range[1])
        ]
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', color='Booster Version Category',
                         title=f'Payload vs. Launch Outcome for {entered_site}')
        return fig


# Run the app
if __name__ == '__main__':
    app.run_server()
