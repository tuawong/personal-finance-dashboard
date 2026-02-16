"""
Analytics Page - Spending Trends and Patterns
"""

import pandas as pd
from dash import html, dcc, callback, Output, Input, register_page

from main.visuals import (
    create_monthly_trend_chart,
    create_day_of_week_chart,
    create_top_merchants_chart
)
from main.sql import load_all_spending_from_db

# Register page
register_page(__name__, path='/analytics', name='Analytics')

# Load and prepare data
all_spending = load_all_spending_from_db()
spending_by_source = all_spending.loc[~all_spending.Category.isin(['Transfer', 'Credit card payment', 'Salary'])]
spending_by_source['Amount'] = spending_by_source['Amount'].replace('$', '', regex=True).astype(float)

spending_by_source['Date'] = pd.to_datetime(spending_by_source['Date'])
spending_by_source['Month'] = spending_by_source['Date'].dt.to_period('M').astype(str)

# Get available sources for dropdown
all_sources = spending_by_source['Source'].unique().tolist()

# Layout
layout = html.Div([
    html.H2("Spending Analytics", style={'textAlign': 'center', 'color': '#2c3e50'}),
    
    # Filters row
    html.Div([
        html.Div([
            html.Label("Filter by Source:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='analytics-source-dropdown',
                options=[{'label': s, 'value': s} for s in all_sources],
                value=all_sources,
                multi=True,
                style={'width': '100%'}
            )
        ], style={'width': '400px', 'display': 'inline-block'}),
    ], style={'marginBottom': '30px', 'padding': '20px', 'backgroundColor': '#f8f9fa', 'borderRadius': '10px'}),
    
    # Row 1: Monthly trend and Day of week
    html.Div([
        html.Div([
            dcc.Graph(id='analytics-monthly-trend-chart')
        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        
        html.Div([
            dcc.Graph(id='analytics-day-of-week-chart')
        ], style={'width': '48%', 'display': 'inline-block', 'marginLeft': '2%', 'verticalAlign': 'top'}),
    ], style={'marginBottom': '20px'}),
    
    # Row 2: Top merchants (full width)
    html.Div([
        dcc.Graph(id='analytics-top-merchants-chart')
    ], style={'marginBottom': '20px'}),
])


# Callbacks
@callback(
    Output('analytics-monthly-trend-chart', 'figure'),
    Input('analytics-source-dropdown', 'value')
)
def update_monthly_trend(selected_sources):
    if not selected_sources:
        selected_sources = all_sources
    df = spending_by_source[spending_by_source['Source'].isin(selected_sources)]
    return create_monthly_trend_chart(df)


@callback(
    Output('analytics-day-of-week-chart', 'figure'),
    Input('analytics-source-dropdown', 'value')
)
def update_day_of_week(selected_sources):
    if not selected_sources:
        selected_sources = all_sources
    df = spending_by_source[spending_by_source['Source'].isin(selected_sources)]
    return create_day_of_week_chart(df)


@callback(
    Output('analytics-top-merchants-chart', 'figure'),
    Input('analytics-source-dropdown', 'value')
)
def update_top_merchants(selected_sources):
    if not selected_sources:
        selected_sources = all_sources
    df = spending_by_source[spending_by_source['Source'].isin(selected_sources)]
    return create_top_merchants_chart(df)
