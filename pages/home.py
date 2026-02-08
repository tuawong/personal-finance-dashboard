"""
Home Page - Landing Page
"""

from dash import html, register_page

# Register as the home page
register_page(__name__, path='/', name='Home')

# Layout
layout = html.Div([
    html.H2("Welcome to Your Personal Finance Dashboard", 
            style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '40px'}),
    
    html.Div([
        html.P(
            "Track your spending, monitor your account balance, and review your transaction history.",
            style={'textAlign': 'center', 'fontSize': '18px', 'color': '#7f8c8d'}
        ),
    ], style={'marginBottom': '50px'}),
    
    # Quick navigation cards
    html.Div([
        # Spending card
        html.Div([
            html.H3("📊 Spending", style={'color': '#3498db'}),
            html.P("Analyze your spending patterns by category, source, and time period."),
            html.A("Go to Spending →", href='/spending', 
                   style={'color': '#3498db', 'textDecoration': 'none', 'fontWeight': 'bold'})
        ], style={
            'width': '280px',
            'display': 'inline-block',
            'padding': '30px',
            'backgroundColor': '#f8f9fa',
            'borderRadius': '10px',
            'margin': '15px',
            'verticalAlign': 'top',
            'textAlign': 'center',
            'minHeight': '150px'
        }),
        
        # Balance card
        html.Div([
            html.H3("💰 Balance", style={'color': '#27ae60'}),
            html.P("Track your account balance over time."),
            html.A("Go to Balance →", href='/balance',
                   style={'color': '#27ae60', 'textDecoration': 'none', 'fontWeight': 'bold'})
        ], style={
            'width': '280px',
            'display': 'inline-block',
            'padding': '30px',
            'backgroundColor': '#f8f9fa',
            'borderRadius': '10px',
            'margin': '15px',
            'verticalAlign': 'top',
            'textAlign': 'center',
            'minHeight': '150px'
        }),
        
        # Transactions card
        html.Div([
            html.H3("📋 Transactions", style={'color': '#9b59b6'}),
            html.P("View and search your complete transaction history."),
            html.A("Go to Transactions →", href='/transactions',
                   style={'color': '#9b59b6', 'textDecoration': 'none', 'fontWeight': 'bold'})
        ], style={
            'width': '280px',
            'display': 'inline-block',
            'padding': '30px',
            'backgroundColor': '#f8f9fa',
            'borderRadius': '10px',
            'margin': '15px',
            'verticalAlign': 'top',
            'textAlign': 'center',
            'minHeight': '150px'
        }),
    ], style={'textAlign': 'center', 'maxWidth': '1100px', 'margin': '0 auto'}),
], style={'padding': '40px'})
