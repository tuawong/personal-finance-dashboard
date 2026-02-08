"""
Personal Finance Dashboard - Multi-Page Dash Application
"""

from dash import Dash, html, dcc, page_container, page_registry

# Initialize app with pages
app = Dash(__name__, use_pages=True, pages_folder='pages')
app.title = "Personal Finance Dashboard"

# Layout with navigation
app.layout = html.Div([
    # Header
    html.H1(
        "Personal Finance Dashboard",
        style={'textAlign': 'center', 'marginBottom': '20px', 'color': '#2c3e50'}
    ),
    
    # Navigation
    html.Div([
        dcc.Link(
            page['name'],
            href=page['path'],
            style={
                'marginRight': '20px',
                'padding': '10px 20px',
                'textDecoration': 'none',
                'backgroundColor': '#3498db',
                'color': 'white',
                'borderRadius': '5px',
                'fontWeight': 'bold'
            }
        )
        for page in page_registry.values()
    ], style={
        'textAlign': 'center',
        'marginBottom': '30px',
        'padding': '20px',
        'backgroundColor': '#f8f9fa',
        'borderRadius': '10px'
    }),
    
    # Page content
    page_container
    
], style={'padding': '20px', 'fontFamily': 'Arial, sans-serif', 'backgroundColor': '#ffffff'})


if __name__ == '__main__':
    app.run(debug=True, port=8051)
