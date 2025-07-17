# spacex_dash_app.py
import os, pandas as pd, dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# (Optional) print cwd & files to be sure:
print("CWD:", os.getcwd())
print("FILES:", os.listdir())

# Load data
df = pd.read_csv("spacex_launch_dash.csv")
# strip any stray whitespace in column names
df.columns = df.columns.str.strip()

# Build the app
app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1("SpaceX Launch Records Dashboard", style={'textAlign':'center'}),
    dcc.Dropdown(
        id="site-dropdown",
        options=[{'label':s,'value':s} for s in ["ALL"]+df["Launch Site"].unique().tolist()],
        value="ALL"
    ),
    html.Br(),
    dcc.Graph(id="success-pie-chart"),
    html.Br(),
    html.P("Payload range (kg):"),
    dcc.RangeSlider(
        id="payload-slider",
        min=df["Payload Mass (kg)"].min(),
        max=df["Payload Mass (kg)"].max(),
        step=1000,
        value=[df["Payload Mass (kg)"].min(), df["Payload Mass (kg)"].max()]
    ),
    html.Br(),
    dcc.Graph(id="success-payload-scatter-chart"),
])

# Debug prints in callbacks
@app.callback(
    Output("success-pie-chart","figure"),
    Input("site-dropdown","value")
)
def update_pie(site):
    print("▶ PIE callback, site =", site)
    d = df if site=="ALL" else df[df["Launch Site"]==site]
    success = d[d["class"]==1]
    print("   rows in pie df =", len(success))
    fig = px.pie(
        success, names="Launch Site", 
        title="Successes by Site" if site=="ALL" else f"Success vs Failure at {site}"
    )
    return fig

@app.callback(
    Output("success-payload-scatter-chart","figure"),
    [Input("site-dropdown","value"), Input("payload-slider","value")]
)
def update_scatter(site, payload_range):
    low, high = payload_range
    print("▶ SCATTER callback, site=",site,"payload=",payload_range)
    d = df[(df["Payload Mass (kg)"]>=low)&(df["Payload Mass (kg)"]<=high)]
    if site!="ALL":
        d = d[d["Launch Site"]==site]
    print("   rows in scatter df =", len(d))
    fig = px.scatter(
        d, x="Payload Mass (kg)", y="class",
        color="Booster Version Category",
        title="Payload vs Outcome"
    )
    return fig

if __name__=="__main__":
    # use app.run() if you're on Dash v2+
    app.run()
