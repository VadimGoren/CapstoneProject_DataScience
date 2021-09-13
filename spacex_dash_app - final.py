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

launch_sites = spacex_df['Launch Site'].unique()

options=[
            {'label': 'All Sites', 'value': 'ALL'},
            {'label': launch_sites[0], 'value': launch_sites[0]},
            {'label': launch_sites[1], 'value': launch_sites[1]},
            {'label': launch_sites[2], 'value': launch_sites[2]},
            {'label': launch_sites[3], 'value': launch_sites[3]}
        ]

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',options=options, value='ALL',
                                             placeholder='Select a Launch Site here', searchable=True),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',min=0,max=10000,step=1000,value=[min_payload,max_payload],
                                                marks={0: '0', 2500: '2500', 5000: '5000', 7500: '7500', 10000: '10000'}),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# add callback decorator
@app.callback(Output(component_id='success-pie-chart', component_property='figure') ,
              Input(component_id='site-dropdown', component_property='value'))
def generate_chart(launch_site):
    
    if launch_site == 'ALL':
        x_success = spacex_df.groupby(['Launch Site'], as_index=False).mean()
        title = 'Total launches by Site'
        fig = px.pie(data_frame=x_success, title=title, names='Launch Site', values='class')
    else:
        rate = spacex_df['class'].loc[spacex_df['Launch Site'] == launch_site].value_counts() / spacex_df['class'].loc[spacex_df['Launch Site'] == launch_site].count()          
        df_success = [[0, rate[0]],[1, rate[1]]]
        x_success = pd.DataFrame(df_success, columns=['class','count'])
        title = 'Success rate of launches for site ' + str(launch_site)
        fig = px.pie(data_frame=x_success, title=title, names='class', values='count')
        
    return (fig)
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
                [Input(component_id='site-dropdown', component_property='value'), 
               Input(component_id="payload-slider", component_property="value")]
               )
def generate_scat(launch_site,payload_range):
    
    if launch_site == 'ALL':
        all_site_df = spacex_df[['class','Payload Mass (kg)','Booster Version Category']].loc[(spacex_df['Payload Mass (kg)'] >= payload_range[0]) & (spacex_df['Payload Mass (kg)'] <= payload_range[1])]
        fig = px.scatter(data_frame=all_site_df, 
                        x="Payload Mass (kg)",
                        y="class", 
                        color='Booster Version Category',
                        title='Correlation between payload and success for All sites')
        
    else:
        site_df = pd.DataFrame(spacex_df.loc[spacex_df['Launch Site'] == launch_site])
        site_df = site_df[['class','Payload Mass (kg)','Booster Version Category']].loc[(site_df['Payload Mass (kg)'] >= payload_range[0]) & (site_df['Payload Mass (kg)'] <= payload_range[1])]
        fig = px.scatter(data_frame=site_df, 
                        x="Payload Mass (kg)",
                        y="class", 
                        color='Booster Version Category',
                        title='Correlation between payload and success for site : ' + str(launch_site))

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
