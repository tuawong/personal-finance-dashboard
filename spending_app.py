"""
Personal Finance Dashboard - Dash Application
"""

import pandas as pd
from dash import Dash, html, dcc, callback, Output, Input

from main.visuals import (
    create_daily_spending_chart,
    create_account_balance_chart,
    create_category_bar_chart,
    create_savings_pie_chart,
    create_monthly_trend_chart,
    create_day_of_week_chart,
    create_top_merchants_chart
)

# Load and prepare data
spending_by_source = pd.read_csv('data/Processed/spending_by_source.csv')
account_balance = pd.read_csv('data/Processed/account_balance.csv')

spending_by_source['Date'] = pd.to_datetime(spending_by_source['Date'])
account_balance['Date'] = pd.to_datetime(account_balance['Date'])
spending_by_source['Month'] = spending_by_source['Date'].dt.to_period('M').astype(str)
account_balance['Month'] = account_balance['Date'].dt.to_period('M').astype(str)

# Get available months and sources for dropdowns
all_months = sorted(spending_by_source['Month'].unique(), reverse=True)
all_sources = spending_by_source['Source'].unique().tolist()

# Initialize app
app = Dash(__name__)
app.title = "Personal Finance Dashboard"

# Layout
app.layout = html.Div([
    # Header
    html.H1(
        "Personal Finance Dashboard",
        style={'textAlign': 'center', 'marginBottom': '30px', 'color': '#2c3e50'}
    ),
    
    # Filters row
    html.Div([
        html.Div([
            html.Label("Select Month:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='month-dropdown',
                options=[{'label': m, 'value': m} for m in all_months],
                value=all_months[0] if all_months else None,
                clearable=False,
                style={'width': '100%'}
            )
        ], style={'width': '200px', 'display': 'inline-block', 'marginRight': '30px'}),
        
        html.Div([
            html.Label("Filter by Source:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='source-dropdown',
                options=[{'label': s, 'value': s} for s in all_sources],
                value=all_sources,
                multi=True,
                style={'width': '100%'}
            )
        ], style={'width': '400px', 'display': 'inline-block'}),
    ], style={'marginBottom': '30px', 'padding': '20px', 'backgroundColor': '#f8f9fa', 'borderRadius': '10px'}),
    
    # Row 1: Daily spending and Account balance
    html.Div([
        html.Div([
            dcc.Graph(id='daily-spending-chart')
        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        
        html.Div([
            dcc.Graph(id='account-balance-chart')
        ], style={'width': '48%', 'display': 'inline-block', 'marginLeft': '2%', 'verticalAlign': 'top'}),
    ], style={'marginBottom': '20px'}),
    
    # Row 2: Category bar chart and Savings pie chart
    html.Div([
        html.Div([
            dcc.Graph(id='category-bar-chart')
        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        
        html.Div([
            dcc.Graph(id='savings-pie-chart')
        ], style={'width': '48%', 'display': 'inline-block', 'marginLeft': '2%', 'verticalAlign': 'top'}),
    ], style={'marginBottom': '20px'}),
    
    # Row 3: Monthly trend and Day of week
    html.Div([
        html.Div([
            dcc.Graph(id='monthly-trend-chart')
        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        
        html.Div([
            dcc.Graph(id='day-of-week-chart')
        ], style={'width': '48%', 'display': 'inline-block', 'marginLeft': '2%', 'verticalAlign': 'top'}),
    ], style={'marginBottom': '20px'}),
    
    # Row 4: Top merchants (full width)
    html.Div([
        dcc.Graph(id='top-merchants-chart')
    ], style={'marginBottom': '20px'}),
    
], style={'padding': '20px', 'fontFamily': 'Arial, sans-serif', 'backgroundColor': '#ffffff'})


# Callbacks
@callback(
    Output('daily-spending-chart', 'figure'),
    [Input('source-dropdown', 'value')]
)
def update_daily_spending(selected_sources):
    if not selected_sources:
        selected_sources = all_sources
    df = spending_by_source[spending_by_source['Source'].isin(selected_sources)]
    return create_daily_spending_chart(df)


@callback(
    Output('account-balance-chart', 'figure'),
    Input('month-dropdown', 'value')
)
def update_account_balance(_):
    return create_account_balance_chart(account_balance)


@callback(
    Output('category-bar-chart', 'figure'),
    [Input('month-dropdown', 'value'),
     Input('source-dropdown', 'value')]
)
def update_category_bar(selected_month, selected_sources):
    if not selected_sources:
        selected_sources = all_sources
    df = spending_by_source[spending_by_source['Source'].isin(selected_sources)]
    return create_category_bar_chart(df, selected_month)


@callback(
    Output('savings-pie-chart', 'figure'),
    [Input('month-dropdown', 'value'),
     Input('source-dropdown', 'value')]
)
def update_savings_pie(selected_month, selected_sources):
    if not selected_sources:
        selected_sources = all_sources
    df = spending_by_source[spending_by_source['Source'].isin(selected_sources)]
    return create_savings_pie_chart(df, account_balance, selected_month)


@callback(
    Output('monthly-trend-chart', 'figure'),
    Input('source-dropdown', 'value')
)
def update_monthly_trend(selected_sources):
    if not selected_sources:
        selected_sources = all_sources
    df = spending_by_source[spending_by_source['Source'].isin(selected_sources)]
    return create_monthly_trend_chart(df)


@callback(
    Output('day-of-week-chart', 'figure'),
    Input('source-dropdown', 'value')
)
def update_day_of_week(selected_sources):
    if not selected_sources:
        selected_sources = all_sources
    df = spending_by_source[spending_by_source['Source'].isin(selected_sources)]
    return create_day_of_week_chart(df)


@callback(
    Output('top-merchants-chart', 'figure'),
    Input('source-dropdown', 'value')
)
def update_top_merchants(selected_sources):
    if not selected_sources:
        selected_sources = all_sources
    df = spending_by_source[spending_by_source['Source'].isin(selected_sources)]
    return create_top_merchants_chart(df)


if __name__ == '__main__':
    app.run(debug=True, port=8051)
