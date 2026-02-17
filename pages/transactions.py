"""
Transaction History Page
"""

import pandas as pd
from dash import html, dcc, callback, Output, Input, register_page, dash_table

from main.sql import load_all_spending_from_db

# Register page
register_page(__name__, path='/transactions', name='Transactions')

# Load and prepare data

#spending_by_source = pd.read_csv('data/Processed/spending_by_source.csv')
all_spending = load_all_spending_from_db()
spending_by_source = all_spending.loc[~all_spending.Category.isin(['Transfer', 'Credit card payment', 'Salary'])]
spending_by_source['Amount'] = spending_by_source['Amount'].replace('[\$,]', '', regex=True).astype(float)
spending_by_source['Date'] = pd.to_datetime(spending_by_source['Date'])
spending_by_source['Month'] = spending_by_source['Date'].dt.to_period('M').astype(str)

# Format date for display
spending_by_source['Date_Display'] = spending_by_source['Date'].dt.strftime('%Y-%m-%d')

# Get available months and sources for dropdowns
all_months = ['All'] + sorted(spending_by_source['Month'].unique(), reverse=True)
all_sources = spending_by_source['Source'].unique().tolist()
all_categories = ['All'] + sorted(spending_by_source['Category'].unique().tolist())

# Prepare display data
display_columns = ['Date_Display', 'Description', 'Subdescription', 'Category', 'Source', 'Amount']

# Layout
layout = html.Div([
    html.H2("Transaction History", style={'textAlign': 'center', 'color': '#2c3e50'}),
    
    # Filters row
    html.Div([
        html.Div([
            html.Label("Filter by Month:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='txn-month-dropdown',
                options=[{'label': m, 'value': m} for m in all_months],
                value='All',
                clearable=False,
                style={'width': '100%'}
            )
        ], style={'width': '150px', 'display': 'inline-block', 'marginRight': '20px'}),
        
        html.Div([
            html.Label("Filter by Source:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='txn-source-dropdown',
                options=[{'label': s, 'value': s} for s in all_sources],
                value=all_sources,
                multi=True,
                style={'width': '100%'}
            )
        ], style={'width': '300px', 'display': 'inline-block', 'marginRight': '20px'}),
        
        html.Div([
            html.Label("Filter by Category:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='txn-category-dropdown',
                options=[{'label': c, 'value': c} for c in all_categories],
                value='All',
                clearable=False,
                style={'width': '100%'}
            )
        ], style={'width': '200px', 'display': 'inline-block'}),
    ], style={'marginBottom': '30px', 'padding': '20px', 'backgroundColor': '#f8f9fa', 'borderRadius': '10px'}),
    
    # Transaction count and total
    html.Div(id='txn-summary', style={'marginBottom': '20px', 'fontSize': '16px'}),
    
    # Transaction table
    dash_table.DataTable(
        id='transaction-table',
        columns=[
            {'name': 'Date', 'id': 'Date_Display'},
            {'name': 'Description', 'id': 'Description'},
            {'name': 'Details', 'id': 'Subdescription'},
            {'name': 'Category', 'id': 'Category'},
            {'name': 'Source', 'id': 'Source'},
            {'name': 'Amount', 'id': 'Amount', 'type': 'numeric', 'format': {'specifier': '$.2f'}},
        ],
        data=spending_by_source[display_columns].sort_values('Date_Display', ascending=False).to_dict('records'),
        page_size=20,
        sort_action='native',
        filter_action='native',
        style_table={'overflowX': 'auto'},
        style_cell={
            'textAlign': 'left',
            'padding': '10px',
            'fontFamily': 'Arial, sans-serif',
        },
        style_header={
            'backgroundColor': '#3498db',
            'color': 'white',
            'fontWeight': 'bold',
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': '#f8f9fa',
            },
            {
                'if': {'filter_query': '{Amount} < 0'},
                'color': 'green',
            },
        ],
    ),
])


# Callbacks
@callback(
    [Output('transaction-table', 'data'),
     Output('txn-summary', 'children')],
    [Input('txn-month-dropdown', 'value'),
     Input('txn-source-dropdown', 'value'),
     Input('txn-category-dropdown', 'value')]
)
def update_transactions(selected_month, selected_sources, selected_category):
    df = spending_by_source.copy()
    
    # Apply filters
    if selected_month != 'All':
        df = df[df['Month'] == selected_month]
    
    if selected_sources:
        df = df[df['Source'].isin(selected_sources)]
    
    if selected_category != 'All':
        df = df[df['Category'] == selected_category]
    
    # Sort by date descending
    df = df.sort_values('Date', ascending=False)
    
    # Calculate summary
    total_transactions = len(df)
    total_amount = df['Amount'].sum()
    
    summary = html.Div([
        html.Span(f"Total Transactions: {total_transactions}", style={'marginRight': '30px', 'fontWeight': 'bold'}),
        html.Span(f"Total Amount: ${total_amount:,.2f}", style={'fontWeight': 'bold'}),
    ])
    
    return df[display_columns].to_dict('records'), summary
