"""
Dashboard created in lecture Week 10
"""

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
#import plotly.figure_factory as ff


stylesheet = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

### pandas dataframe to html table

app = dash.Dash(__name__, external_stylesheets=stylesheet)



Pay2020=pd.read_csv('/Users/check4068/Desktop/已完成课业/Jasmine Data Science/Payroll2020.csv',header=0)

fname = "/Users/check4068/Desktop/已完成课业/Jasmine Data Science/US (1)/US.txt"

with open(fname) as fin:
    data_str = fin.read()

data_list = []
for line in data_str.split('\n'):
    mylist = line.split('\t')
    if len(mylist) > 11:
        data_list.append(mylist)


geo=pd.DataFrame(data_list, columns=['Country', 'POSTAL','City','State','StateCode','county','x2','x3','x4','longitude','latitude','number'])
Pay2020=Pay2020.rename(columns={"DEPARTMENT_NAME": "Department", "QUINN / EDUCATION INCENTIVE": "Education Incentive", "TITLE": "Title", "REGULAR": "Regular", "OTHER":"Other", "OVERTIME": "Overtime", "INJURED": "Injured", "DETAIL": "Detail", "TOTAL EARNINGS": "Total.Earnings" })
Pay2020=Pay2020.loc[Pay2020['POSTAL'].isnull()!=True]
#去掉data

Pay2020new= Pay2020[['Department','Total.Earnings','POSTAL']]

#加上lambda
#Pay2020.loc[Pay2020['Postal']].zfill(5)

df= pd.merge(Pay2020new,geo, on='POSTAL',how='inner')
#df=df.loc[Pay2020county['county'].isnull()!=True]
df= df[df["StateCode"]=="MA"]
df['Total.Earnings']=df['Total.Earnings'].str.replace('$','').str.replace(' ','').str.replace(',','').str.replace(')','').str.replace('(','').astype('float')
df=df.groupby(['county','Department'],as_index=False)['Total.Earnings'].agg({'Total.Earnings':'sum'}).sort_values(by='Total.Earnings',ascending=False)
#.rank(method='first',ascending=False)
#df=df.loc[df['Rank']<50]
df['Rank']=df.groupby('county')['Total.Earnings'].rank(method='first',ascending=False)
df=df.loc[df['Rank']<=10]


df_map= pd.merge(Pay2020new,geo, on='POSTAL',how='inner')
df_map['Total.Earnings']=df_map['Total.Earnings'].str.replace('$','').str.replace(' ','').str.replace(',','').str.replace(')','').str.replace('(','').astype('float')
df_map= df_map[df_map["StateCode"]=="MA"]
df_map=df_map.groupby(['county','POSTAL'],as_index=False)['Total.Earnings'].agg({'Total.Earnings':'sum'}).sort_values(by='Total.Earnings',ascending=False)
df_map


#
fig = px.bar(df, x="Department", y="Total.Earnings", color="county")
fig2 = px.pie(df_map,names='county',values='Total.Earnings')


app.layout = html.Div([
    html.H1('My First MA705 Dashboard!',
            style={'textAlign' : 'center'}),
    html.H5('Users can click on one or multiple counties to study the top 50 departments with the highest total payroll expenses in the state of Massachusetts. Moreover, the pie chart would allow us to compare the proportion of total payroll earnings across the selected counties. Users who are interested in discovering high payroll expense on the department and county level could utilize this dashboard as an initial observation to generate idea for further research directions.',
            style={'textAlign' : 'center'}),
    html.A('Click here to go to Bentley',
           href='http://www.bentley.edu',
           target='_blank'),
    dcc.Graph(figure=fig, id='univ_plot'),
    dcc.Graph(figure=fig2, id='map_plot'),
    html.Div([html.H4('Countys to Display for Pie Chart:'),
              dcc.Checklist(
                  options=[{'label':'Suffolk', 'value':'Suffolk'},
                           {'label':'Norfolk', 'value': 'Norfolk'},
                           {'label':'Middlesex', 'value': 'Middlesex'},
                           {'label':'Worcester', 'value': 'Worcester'},
                           {'label':'Plymouth', 'value':  'Plymouth'},
                           {'label':'Essex', 'value':  'Essex'},
                           {'label':'Bristol', 'value':  'Bristol'},
                           {'label':'Barnstable', 'value': 'Barnstable'},
                           {'label':'Hampden', 'value':  'Hampden'},
                           {'label':'Dukes', 'value':  'Dukes'},
                           {'label':'Nantucket', 'value':  'Nantucket'},
                           {'label':'Berkshire', 'value':  'Berkshire'}],
                  value=['Suffolk','Norfolk','Middlesex','Worcester','Plymouth','Essex',
                         'Bristol','Barnstable','Hampden','Dukes','Nantucket','Berkshire'],
                  id = 'County_checklist')],
             style={'width' : '50%', 'float' : 'right'}),

    html.Div([html.H4('Countys to Display for Bar Plot:'),
              dcc.Dropdown(
                  options=[{'label':'Suffolk', 'value':'Suffolk'},
                           {'label':'Norfolk', 'value': 'Norfolk'},
                           {'label':'Middlesex', 'value': 'Middlesex'},
                           {'label':'Worcester', 'value': 'Worcester'},
                           {'label':'Plymouth', 'value':  'Plymouth'},
                           {'label':'Essex', 'value':  'Essex'},
                           {'label':'Bristol', 'value':  'Bristol'},
                           {'label':'Barnstable', 'value': 'Barnstable'},
                           {'label':'Hampden', 'value':  'Hampden'},
                           {'label':'Dukes', 'value':  'Dukes'},
                           {'label':'Nantucket', 'value':  'Nantucket'},
                           {'label':'Berkshire', 'value':  'Berkshire'}],
                  value='Suffolk',
                  id = 'County_Dropdown')],
             style={'width' : '50%', 'float' : 'right'}),
    #html.Div(id='table_div')
    ])

@app.callback(
    Output(component_id="map_plot", component_property="figure"),
    [Input(component_id="County_checklist", component_property="value")]
)
def update_map(counties):
    df1 = df_map[df_map.county.isin(counties)].sort_values('county')
    df1 = df1[['Total.Earnings','county']]
    fig2 = px.pie(df1,names='county',values='Total.Earnings')
    return fig2

@app.callback(
    Output(component_id="univ_plot", component_property="figure"),
    [Input(component_id="County_Dropdown", component_property="value")]
)
def update_plot(counties):
    df2 = df.loc[df['county']==counties].sort_values('Total.Earnings', ascending=False)
    df2 = df2[['Department', 'Total.Earnings', 'county']]
    fig = px.bar(df2,x="Department", y="Total.Earnings", color="county")
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)