"""
Spending Analysis Page
"""

import pandas as pd
from dash import html, dcc, callback, Output, Input, register_page

from main.visuals import (
    create_daily_spending_chart,
    create_category_bar_chart,
    create_spending_vs_savings_pie,
    create_spending_breakdown_pie,
    create_monthly_trend_chart,
    create_day_of_week_chart,
    create_top_merchants_chart
)
from main.sql import load_all_spending_from_db

# Register page
register_page(__name__, path='/spending', name='Spending')

# Load and prepare data
# spending_by_source = pd.read_csv('data/Processed/spending_by_source.csv')
# account_balance = pd.read_csv('data/Processed/account_balance.csv')
all_spending = load_all_spending_from_db()
spending_by_source = all_spending.loc[~all_spending.Category.isin(['Transfer', 'Credit card payment', 'Salary'])]
spending_by_source['Amount'] = spending_by_source['Amount'].replace('[\$,]', '', regex=True).astype(float)

account_balance = all_spending.loc[all_spending.Source=='Scotia Debit']

spending_by_source['Date'] = pd.to_datetime(spending_by_source['Date'])
account_balance['Date'] = pd.to_datetime(account_balance['Date'])
spending_by_source['Month'] = spending_by_source['Date'].dt.to_period('M').astype(str)
account_balance['Month'] = account_balance['Date'].dt.to_period('M').astype(str)

# Get available months and sources for dropdowns
all_months = ['All'] + sorted(spending_by_source['Month'].unique(), reverse=True)
all_sources = spending_by_source['Source'].unique().tolist()

# Layout
layout = html.Div([
    html.H2("Spending Analysis", style={'textAlign': 'center', 'color': '#2c3e50'}),
    
    # Filters row
    html.Div([
        html.Div([
            html.Label("Select Month:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='spending-month-dropdown',
                options=[{'label': m, 'value': m} for m in all_months],
                value=all_months[0] if all_months else None,
                clearable=False,
                style={'width': '100%'}
            )
        ], style={'width': '200px', 'display': 'inline-block', 'marginRight': '30px'}),
        
        html.Div([
            html.Label("Filter by Source:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='spending-source-dropdown',
                options=[{'label': s, 'value': s} for s in all_sources],
                value=all_sources,
                multi=True,
                style={'width': '100%'}
            )
        ], style={'width': '400px', 'display': 'inline-block'}),
    ], style={'marginBottom': '30px', 'padding': '20px', 'backgroundColor': '#f8f9fa', 'borderRadius': '10px'}),
    
    # Row 1: Daily spending by source
    html.Div([
        dcc.Graph(id='daily-spending-chart')
    ], style={'marginBottom': '20px'}),
    
    # Row 2: Category bar chart (double height) and two pie charts stacked
    html.Div([
        html.Div([
            dcc.Graph(id='category-bar-chart', style={'height': '750px'})
        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        
        html.Div([
            dcc.Graph(id='spending-vs-savings-pie'),
            dcc.Graph(id='spending-breakdown-pie')
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
])


# Callbacks
@callback(
    Output('daily-spending-chart', 'figure'),
    [Input('spending-source-dropdown', 'value')]
)
def update_daily_spending(selected_sources):
    if not selected_sources:
        selected_sources = all_sources
    df = spending_by_source[spending_by_source['Source'].isin(selected_sources)]
    return create_daily_spending_chart(df)


@callback(
    Output('category-bar-chart', 'figure'),
    [Input('spending-month-dropdown', 'value'),
     Input('spending-source-dropdown', 'value')]
)
def update_category_bar(selected_month, selected_sources):
    if not selected_sources:
        selected_sources = all_sources
    df = spending_by_source[spending_by_source['Source'].isin(selected_sources)]
    return create_category_bar_chart(df, selected_month)


@callback(
    Output('spending-vs-savings-pie', 'figure'),
    [Input('spending-month-dropdown', 'value'),
     Input('spending-source-dropdown', 'value')]
)
def update_spending_vs_savings_pie(selected_month, selected_sources):
    if not selected_sources:
        selected_sources = all_sources
    df = spending_by_source[spending_by_source['Source'].isin(selected_sources)]
    return create_spending_vs_savings_pie(df, account_balance, selected_month)


@callback(
    Output('spending-breakdown-pie', 'figure'),
    [Input('spending-month-dropdown', 'value'),
     Input('spending-source-dropdown', 'value')]
)
def update_spending_breakdown_pie(selected_month, selected_sources):
    if not selected_sources:
        selected_sources = all_sources
    df = spending_by_source[spending_by_source['Source'].isin(selected_sources)]
    return create_spending_breakdown_pie(df, account_balance, selected_month)


@callback(
    Output('monthly-trend-chart', 'figure'),
    Input('spending-source-dropdown', 'value')
)
def update_monthly_trend(selected_sources):
    if not selected_sources:
        selected_sources = all_sources
    df = spending_by_source[spending_by_source['Source'].isin(selected_sources)]
    return create_monthly_trend_chart(df)


@callback(
    Output('day-of-week-chart', 'figure'),
    Input('spending-source-dropdown', 'value')
)
def update_day_of_week(selected_sources):
    if not selected_sources:
        selected_sources = all_sources
    df = spending_by_source[spending_by_source['Source'].isin(selected_sources)]
    return create_day_of_week_chart(df)


@callback(
    Output('top-merchants-chart', 'figure'),
    Input('spending-source-dropdown', 'value')
)
def update_top_merchants(selected_sources):
    if not selected_sources:
        selected_sources = all_sources
    df = spending_by_source[spending_by_source['Source'].isin(selected_sources)]
    return create_top_merchants_chart(df)