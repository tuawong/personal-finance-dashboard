"""
Spending Analysis Page
"""

import pandas as pd
from dash import html, dcc, callback, Output, Input, register_page, dash_table

from main.visuals import (
    create_daily_spending_chart,
    create_category_bar_chart,
    create_spending_vs_savings_pie,
    create_spending_breakdown_pie
)
from main.sql import load_all_spending_from_db

# Register page
register_page(__name__, path='/spending', name='Spending')

# Load and prepare data
# spending_by_source = pd.read_csv('data/Processed/spending_by_source.csv')
# account_balance = pd.read_csv('data/Processed/account_balance.csv')
all_spending = load_all_spending_from_db()
spending_by_source = all_spending.loc[~all_spending.Category.isin(['Transfer', 'Credit card payment', 'Salary'])].copy()
spending_by_source['Amount'] = spending_by_source['Amount'].replace('$', '', regex=True).astype(float)

account_balance = all_spending.loc[all_spending.Source=='Scotia Debit'].copy()

spending_by_source['Date'] = pd.to_datetime(spending_by_source['Date'])
account_balance['Date'] = pd.to_datetime(account_balance['Date'])
spending_by_source['Month'] = spending_by_source['Date'].dt.to_period('M').astype(str)
account_balance['Month'] = account_balance['Date'].dt.to_period('M').astype(str)
spending_by_source['Date_Display'] = spending_by_source['Date'].dt.strftime('%Y-%m-%d')
if 'Subdescription' not in spending_by_source.columns:
    spending_by_source['Subdescription'] = ''

# Get available months and sources for dropdowns
all_months = ['All'] + sorted(spending_by_source['Month'].unique(), reverse=True)
all_sources = spending_by_source['Source'].unique().tolist()
all_categories = ['All'] + sorted(spending_by_source['Category'].dropna().unique().tolist())

# Chart sizing (tweak here to test layout changes)
VS_SAVINGS_HEIGHT = 350
BREAKDOWN_HEIGHT = 750

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
    
    # Row 1: Spending vs savings pie + daily spending by source
    html.Div([
        html.Div([
            dcc.Graph(id='spending-vs-savings-pie', style={'height': f'{VS_SAVINGS_HEIGHT}px'})
        ], style={'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top'}),

        html.Div([
            dcc.Graph(id='daily-spending-chart')
        ], style={'width': '68%', 'display': 'inline-block', 'marginLeft': '2%', 'verticalAlign': 'top'}),
    ], style={'marginBottom': '20px'}),

    # Row 2: Category bar chart (double height) and spending breakdown pie
    html.Div([
        html.Div([
            dcc.Graph(id='category-bar-chart', style={'height': '750px'})
        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),

        html.Div([
            dcc.Graph(id='spending-breakdown-pie', style={'height': f'{BREAKDOWN_HEIGHT}px'})
        ], style={'width': '48%', 'display': 'inline-block', 'marginLeft': '2%', 'verticalAlign': 'top'}),
    ], style={'marginBottom': '20px'}),

    # Line items by category
    html.Div([
        html.H3("Spending Line Items", style={'marginBottom': '10px'}),
        html.Div([
            html.Label("Filter by Category:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='spending-category-dropdown',
                options=[{'label': c, 'value': c} for c in all_categories],
                value='All',
                clearable=False,
                style={'width': '300px'}
            )
        ], style={'marginBottom': '15px'}),
        dash_table.DataTable(
            id='spending-line-items-table',
            columns=[
                {'name': 'Date', 'id': 'Date_Display'},
                {'name': 'Description', 'id': 'Description'},
                {'name': 'Details', 'id': 'Subdescription'},
                {'name': 'Category', 'id': 'Category'},
                {'name': 'Source', 'id': 'Source'},
                {'name': 'Amount', 'id': 'Amount', 'type': 'numeric', 'format': {'specifier': '$.2f'}},
            ],
            data=[],
            page_size=15,
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
    ], style={'marginBottom': '20px'}),
])


# Callbacks
@callback(
    Output('daily-spending-chart', 'figure'),
    [Input('spending-month-dropdown', 'value'),
     Input('spending-source-dropdown', 'value')]
)
def update_daily_spending(selected_month, selected_sources):
    if not selected_sources:
        selected_sources = all_sources
    df = spending_by_source[spending_by_source['Source'].isin(selected_sources)]
    if selected_month != 'All':
        df = df[df['Month'] == selected_month]
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
    return create_spending_vs_savings_pie(
        df,
        account_balance,
        selected_month,
        height=VS_SAVINGS_HEIGHT
    )


@callback(
    Output('spending-breakdown-pie', 'figure'),
    [Input('spending-month-dropdown', 'value'),
     Input('spending-source-dropdown', 'value')]
)
def update_spending_breakdown_pie(selected_month, selected_sources):
    if not selected_sources:
        selected_sources = all_sources
    df = spending_by_source[spending_by_source['Source'].isin(selected_sources)]
    return create_spending_breakdown_pie(
        df,
        account_balance,
        selected_month,
        height=BREAKDOWN_HEIGHT
    )


@callback(
    Output('spending-line-items-table', 'data'),
    [Input('spending-month-dropdown', 'value'),
     Input('spending-source-dropdown', 'value'),
     Input('spending-category-dropdown', 'value'),
     Input('spending-breakdown-pie', 'clickData')]
)
def update_spending_line_items(selected_month, selected_sources, selected_category, pie_click):
    if not selected_sources:
        selected_sources = all_sources

    df = spending_by_source[spending_by_source['Source'].isin(selected_sources)]
    if selected_month != 'All':
        df = df[df['Month'] == selected_month]

    category_filter = selected_category
    if pie_click and selected_category == 'All':
        category_filter = pie_click.get('points', [{}])[0].get('label', 'All')

    if category_filter != 'All':
        if category_filter == 'Others':
            category_totals = df.groupby('Category')['Amount'].sum()
            total_expenses = category_totals.sum()
            threshold = 0.01 * total_expenses if total_expenses > 0 else 0
            small_categories = category_totals[category_totals < threshold].index.tolist()
            df = df[df['Category'].isin(small_categories)]
        else:
            df = df[df['Category'] == category_filter]

    df = df.sort_values('Date', ascending=False)
    display_columns = ['Date_Display', 'Description', 'Subdescription', 'Category', 'Source', 'Amount']
    return df[display_columns].to_dict('records')