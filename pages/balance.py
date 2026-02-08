"""
Account Balance Page
"""

import pandas as pd
from dash import html, dcc, register_page

from main.visuals import create_account_balance_chart

# Register page
register_page(__name__, path='/balance', name='Balance')

# Load and prepare data
account_balance = pd.read_csv('data/Processed/account_balance.csv')
account_balance['Date'] = pd.to_datetime(account_balance['Date'])

# Create the chart
balance_fig = create_account_balance_chart(account_balance)

# Layout
layout = html.Div([
    html.H2("Account Balance", style={'textAlign': 'center', 'color': '#2c3e50'}),
    
    html.Div([
        dcc.Graph(figure=balance_fig)
    ], style={'marginBottom': '20px'}),
])