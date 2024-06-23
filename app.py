import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

# Read the CSV file
df = pd.read_csv('Amazon Sale Report.csv', encoding='latin1', low_memory=False)

# Clean the Date column
def clean_date(date_str):
    try:
        return pd.to_datetime(date_str, errors='coerce')
    except Exception as e:
        return pd.NaT

df['Date'] = df['Date'].apply(clean_date)
df.dropna(subset=['Date'], inplace=True)

# Convert Amount to numeric and handle errors
df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
df.dropna(subset=['Amount'], inplace=True)

# Initialize the app with a theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Define the layout
app.layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(html.H1("Amazon Sale Report", className="text-center text-primary mb-4"), width=12)
        ),
        dbc.Row(
            dbc.Col(
                dcc.DatePickerRange(
                    id='date-picker-range',
                    start_date=df['Date'].min(),
                    end_date=df['Date'].max(),
                    display_format='YYYY-MM-DD',
                    style={'margin-bottom': '20px'}
                ),
                width=4
            )
        ),
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id='sales-trend'), width=12),
                dbc.Col(dcc.Graph(id='amount-by-city'), width=6),
                dbc.Col(dcc.Graph(id='status-distribution'), width=6),
                dbc.Col(dcc.Graph(id='sales-map'), width=12),
            ]
        )
    ],
    fluid=True,
)

# Define the callbacks
@app.callback(
    [Output('sales-trend', 'figure'),
     Output('amount-by-city', 'figure'),
     Output('status-distribution', 'figure'),
     Output('sales-map', 'figure')],
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_charts(start_date, end_date):
    filtered_df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
    
    if filtered_df.empty:
        return {}, {}, {}, {}

    # Sales Trend over Time
    try:
        sales_trend_fig = px.line(
            filtered_df.groupby('Date').sum(numeric_only=True).reset_index(),
            x='Date', y='Amount',
            title='Sales Trend Over Time',
            labels={'Amount': 'Amount (INR)', 'Date': 'Date'}
        )
    except Exception as e:
        print(f"Error creating sales_trend_fig: {e}")
        sales_trend_fig = {}

    # Amount by City
    try:
        amount_by_city = filtered_df.groupby('ship-city').agg({'Amount': 'sum'}).reset_index()
        amount_by_city_fig = px.bar(
            amount_by_city.sort_values('Amount', ascending=False).head(10),
            x='ship-city', y='Amount',
            title='Top 10 Cities by Amount',
            labels={'Amount': 'Amount (INR)', 'ship-city': 'City'}
        )
    except Exception as e:
        print(f"Error creating amount_by_city_fig: {e}")
        amount_by_city_fig = {}

    # Status Distribution
    try:
        status_distribution_fig = px.pie(
            filtered_df,
            names='Status',
            values='Amount',
            title='Distribution of Order Status'
        )
    except Exception as e:
        print(f"Error creating status_distribution_fig: {e}")
        status_distribution_fig = {}

    # Sales Map
    try:
        sales_map_fig = px.scatter_mapbox(
            filtered_df,
            lat='Latitude', lon='Longitude',
            size='Amount',
            color='Amount',
            hover_name='ship-city',
            title='Sales Map',
            mapbox_style="carto-positron",
            zoom=3,
        )
    except Exception as e:
        print(f"Error creating sales_map_fig: {e}")
        sales_map_fig = {}

    return sales_trend_fig, amount_by_city_fig, status_distribution_fig, sales_map_fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
