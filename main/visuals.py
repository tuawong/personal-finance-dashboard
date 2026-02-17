"""
Visualization functions for the personal finance dashboard.
All functions return Plotly figure objects that can be used in Dash or displayed directly.
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Optional, List


def create_daily_spending_chart(spending_df: pd.DataFrame) -> go.Figure:
    """
    Create a scatter plot of daily spending over time, color-coded by source.
    
    Args:
        spending_df: DataFrame with columns ['Date', 'Source', 'Amount', 'Description']
        
    Returns:
        Plotly figure object
    """
    daily_spending = spending_df.groupby(['Date', 'Source']).agg({
        'Amount': 'sum',
        'Description': lambda x: '<br>'.join(x.astype(str))
    }).reset_index()

    fig = px.scatter(
        daily_spending,
        x='Date',
        y='Amount',
        color='Source',
        hover_data={'Description': True, 'Amount': ':.2f'},
        title='Daily Spending by Source'
    )

    # Add trend lines for each source
    for source in daily_spending['Source'].unique():
        source_data = daily_spending[daily_spending['Source'] == source].sort_values('Date')
        fig.add_trace(go.Scatter(
            x=source_data['Date'],
            y=source_data['Amount'],
            mode='lines',
            name=f'{source} (trend)',
            line=dict(width=1, dash='dot'),
            showlegend=False,
            hoverinfo='skip'
        ))

    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Amount ($)',
        hovermode='closest'
    )
    
    return fig


def create_account_balance_chart(account_df: pd.DataFrame) -> go.Figure:
    """
    Create a line chart showing account balance progression over time.
    
    Args:
        account_df: DataFrame with columns ['Date', 'Balance', 'Description']
        
    Returns:
        Plotly figure object
    """
    df_balance = account_df.dropna(subset=['Balance']).sort_values('Date')

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_balance['Date'],
        y=df_balance['Balance'],
        mode='lines+markers',
        name='Balance',
        line=dict(color='green', width=2),
        marker=dict(size=6),
        hovertemplate='<b>Date:</b> %{x}<br><b>Balance:</b> $%{y:,.2f}<br><b>Transaction:</b> %{customdata}<extra></extra>',
        customdata=df_balance['Description']
    ))

    fig.update_layout(
        title='Account Balance Over Time',
        xaxis_title='Date',
        yaxis_title='Balance ($)',
        hovermode='x unified'
    )
    
    return fig


def create_category_bar_chart(spending_df: pd.DataFrame, selected_month: str) -> go.Figure:
    """
    Create a horizontal bar chart of spending by category for a selected month.
    
    Args:
        spending_df: DataFrame with columns ['Month', 'Category', 'Amount']
        selected_month: Month string in format 'YYYY-MM' or 'All'
        
    Returns:
        Plotly figure object
    """
    if selected_month == 'All':
        month_data = spending_df
        title_suffix = 'All Time'
    else:
        month_data = spending_df[spending_df['Month'] == selected_month]
        title_suffix = selected_month
    
    category_spending = month_data.groupby('Category')['Amount'].sum().reset_index()
    category_spending = category_spending.sort_values('Amount', ascending=True)

    fig = px.bar(
        category_spending,
        x='Amount',
        y='Category',
        orientation='h',
        title=f'Spending by Category - {title_suffix}',
        color='Category',
        color_discrete_sequence=px.colors.qualitative.Bold,
        text=category_spending['Amount'].apply(lambda x: f'${x:,.2f}')
    )

    fig.update_traces(textposition='outside')
    fig.update_layout(
        xaxis_title='Total Amount ($)',
        yaxis_title='Category',
        showlegend=False
    )
    
    return fig


# Extended color palette (30 colors)
CATEGORY_COLORS = [
    '#66c2a5', '#fc8d62', '#8da0cb', '#e78ac3', '#a6d854', '#ffd92f',
    '#e5c494', '#b3b3b3', '#1f78b4', '#33a02c', '#fb9a99', '#e31a1c',
    '#fdbf6f', '#ff7f00', '#cab2d6', '#6a3d9a', '#ffff99', '#b15928',
    '#a6cee3', '#b2df8a', '#fb8072', '#80b1d3', '#fdb462', '#b3de69',
    '#fccde5', '#d9d9d9', '#bc80bd', '#ccebc5', '#ffed6f', '#8dd3c7'
]


def _get_payroll_and_expenses(spending_df, account_df, selected_month):
    """Helper function to calculate payroll and expenses for a given period."""
    if selected_month == 'All':
        month_income = account_df[
            account_df['Category'] == 'Salary'
        ]['Amount'].sum()
        month_spending = spending_df
        title_suffix = 'All Time'
    else:
        month_income = account_df[
            (account_df['Month'] == selected_month) &
            (account_df['Category'] == 'Salary')
        ]['Amount'].sum()
        month_spending = spending_df[spending_df['Month'] == selected_month]
        title_suffix = selected_month

    payroll = abs(month_income) if month_income < 0 else 0
    expenses_by_category = month_spending.groupby('Category')['Amount'].sum().to_dict()
    total_expenses = sum(expenses_by_category.values())
    
    return payroll, expenses_by_category, total_expenses, title_suffix


def create_spending_vs_savings_pie(
    spending_df: pd.DataFrame,
    account_df: pd.DataFrame,
    selected_month: str,
    height: Optional[int] = None
) -> go.Figure:
    """
    Create a donut pie chart comparing total spending vs savings.
    
    Args:
        spending_df: DataFrame with columns ['Month', 'Category', 'Amount']
        account_df: DataFrame with columns ['Month', 'Category', 'Amount']
        selected_month: Month string in format 'YYYY-MM' or 'All'
        
    Returns:
        Plotly figure object
    """
    payroll, expenses_by_category, total_expenses, title_suffix = _get_payroll_and_expenses(
        spending_df, account_df, selected_month
    )

    if payroll > 0:
        savings = max(0, payroll - total_expenses)
        
        fig = go.Figure(data=[go.Pie(
            labels=['Spending', 'Savings'],
            values=[total_expenses, savings],
            hole=0.4,
            marker_colors=['coral', 'lightgreen'],
            texttemplate='%{label}<br>$%{value:,.2f}<br>(%{percent})',
            textposition='outside',
            hovertemplate='<b>%{label}</b><br>Amount: $%{value:,.2f}<br>Percentage: %{percent}<extra></extra>'
        )])
        
        fig.update_layout(
            title=f'Spending vs Savings - {title_suffix}<br><sub>Payroll: ${payroll:,.2f}</sub>',
            margin=dict(t=80, b=60, l=60, r=60),
            showlegend=False
        )
    else:
        # No payroll - show placeholder
        fig = go.Figure(data=[go.Pie(
            labels=['Spending'],
            values=[total_expenses],
            hole=0.4,
            marker_colors=['coral'],
            texttemplate='%{label}<br>$%{value:,.2f}',
            textposition='outside'
        )])
        
        fig.update_layout(
            title=f'Spending vs Savings - {title_suffix}<br><sub>(No payroll data available)</sub>',
            margin=dict(t=80, b=60, l=60, r=60),
            showlegend=False
        )

    if height is not None:
        fig.update_layout(height=height)

    return fig


def create_spending_breakdown_pie(
    spending_df: pd.DataFrame,
    account_df: pd.DataFrame,
    selected_month: str,
    height: Optional[int] = None
) -> go.Figure:
    """
    Create a donut pie chart showing spending breakdown by category.
    Categories under 1% are grouped into 'Others'.
    
    Args:
        spending_df: DataFrame with columns ['Month', 'Category', 'Amount']
        account_df: DataFrame with columns ['Month', 'Category', 'Amount']
        selected_month: Month string in format 'YYYY-MM' or 'All'
        
    Returns:
        Plotly figure object
    """
    payroll, expenses_by_category, total_expenses, title_suffix = _get_payroll_and_expenses(
        spending_df, account_df, selected_month
    )

    # Group categories under 1% into "Others"
    threshold = 0.01 * total_expenses if total_expenses > 0 else 0
    grouped_expenses = {}
    others_total = 0

    for category, amount in expenses_by_category.items():
        if amount < threshold:
            others_total += amount
        else:
            grouped_expenses[category] = amount

    if others_total > 0:
        grouped_expenses['Others'] = others_total

    labels = list(grouped_expenses.keys())
    values = list(grouped_expenses.values())
    
    # Assign colors, with grey for "Others"
    colors = list(CATEGORY_COLORS[:len(labels)])
    if 'Others' in labels:
        others_idx = labels.index('Others')
        colors[others_idx] = 'lightgrey'
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker_colors=colors,
        texttemplate='%{label}<br>$%{value:,.2f}<br>(%{percent})',
        textposition='outside',
        hovertemplate='<b>%{label}</b><br>Amount: $%{value:,.2f}<br>Percentage: %{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        title=f'Spending Breakdown - {title_suffix}',
        margin=dict(t=80, b=80, l=100, r=100),
        showlegend=False
    )

    if height is not None:
        fig.update_layout(height=height)

    return fig


def create_savings_pie_chart(
    spending_df: pd.DataFrame,
    account_df: pd.DataFrame,
    selected_month: str,
    height: Optional[int] = None
) -> go.Figure:
    """
    Create a donut pie chart showing spending breakdown vs savings.
    If payroll data is available, shows savings as the gap between income and expenses.
    
    Args:
        spending_df: DataFrame with columns ['Month', 'Category', 'Amount']
        account_df: DataFrame with columns ['Month', 'Category', 'Amount']
        selected_month: Month string in format 'YYYY-MM' or 'All'
        
    Returns:
        Plotly figure object
    """
    payroll, expenses_by_category, total_expenses, title_suffix = _get_payroll_and_expenses(
        spending_df, account_df, selected_month
    )

    if payroll > 0:
        # Calculate savings and create pie with categories + savings
        savings = payroll - total_expenses
        labels = list(expenses_by_category.keys()) + ['Savings']
        values = list(expenses_by_category.values()) + [max(0, savings)]
        colors = list(CATEGORY_COLORS[:len(expenses_by_category)]) + ['lightgreen']
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.4,
            marker_colors=colors,
            texttemplate='%{label}<br>$%{value:,.2f} (%{percent})',
            textposition='outside',
            hovertemplate='<b>%{label}</b><br>Amount: $%{value:,.2f}<br>Percentage: %{percent}<extra></extra>'
        )])
        
        fig.update_layout(
            title=f'Income Allocation - {title_suffix}<br><sub>Payroll: ${payroll:,.2f}</sub>',
            annotations=[dict(text=f'${payroll:,.0f}', x=0.5, y=0.5, font_size=16, showarrow=False)],
            margin=dict(t=80, b=80, l=80, r=80)
        )
    else:
        # No payroll - just show spending breakdown
        labels = list(expenses_by_category.keys())
        values = list(expenses_by_category.values())
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.4,
            texttemplate='%{label}<br>$%{value:,.2f} (%{percent})',
            textposition='outside',
            hovertemplate='<b>%{label}</b><br>Amount: $%{value:,.2f}<br>Percentage: %{percent}<extra></extra>'
        )])
        
        fig.update_layout(
            title=f'Spending Breakdown - {title_suffix}<br><sub>(No payroll data available)</sub>',
            annotations=[dict(text=f'${total_expenses:,.0f}', x=0.5, y=0.5, font_size=16, showarrow=False)],
            margin=dict(t=80, b=80, l=80, r=80)
        )

    if height is not None:
        fig.update_layout(height=height)

    return fig


def create_monthly_trend_chart(spending_df: pd.DataFrame) -> go.Figure:
    """
    Create a line chart showing total spending per month.
    
    Args:
        spending_df: DataFrame with columns ['Month', 'Amount']
        
    Returns:
        Plotly figure object
    """
    monthly_totals = spending_df.groupby('Month')['Amount'].sum().reset_index()
    monthly_totals = monthly_totals.sort_values('Month')

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=monthly_totals['Month'],
        y=monthly_totals['Amount'],
        mode='lines+markers+text',
        name='Total Spending',
        line=dict(color='coral', width=3),
        marker=dict(size=10),
        text=monthly_totals['Amount'].apply(lambda x: f'${x:,.0f}'),
        textposition='top center',
        hovertemplate='<b>Month:</b> %{x}<br><b>Total:</b> $%{y:,.2f}<extra></extra>'
    ))

    fig.update_layout(
        title='Monthly Spending Trend',
        xaxis_title='Month',
        yaxis_title='Total Spending ($)',
        hovermode='x unified'
    )
    
    return fig


def create_day_of_week_chart(spending_df: pd.DataFrame) -> go.Figure:
    """
    Create a bar chart showing spending patterns by day of week.
    
    Args:
        spending_df: DataFrame with columns ['Date', 'Amount']
        
    Returns:
        Plotly figure object
    """
    df = spending_df.copy()
    df['DayOfWeek'] = df['Date'].dt.day_name()
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    dow_spending = df.groupby('DayOfWeek').agg({
        'Amount': ['sum', 'mean', 'count']
    }).reset_index()
    dow_spending.columns = ['DayOfWeek', 'Total', 'Average', 'Count']
    dow_spending['DayOfWeek'] = pd.Categorical(
        dow_spending['DayOfWeek'],
        categories=day_order,
        ordered=True
    )
    dow_spending = dow_spending.sort_values('DayOfWeek')

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=dow_spending['DayOfWeek'],
        y=dow_spending['Average'],
        name='Average Spending',
        marker_color='steelblue',
        text=dow_spending['Average'].apply(lambda x: f'${x:,.2f}'),
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Average: $%{y:,.2f}<br>Total: $%{customdata[0]:,.2f}<br>Transactions: %{customdata[1]}<extra></extra>',
        customdata=dow_spending[['Average', 'Count']].values
    ))

    fig.update_layout(
        title='Spending by Day of Week',
        xaxis_title='Day',
        yaxis_title='Average Spending ($)',
        showlegend=False
    )
    
    return fig


def create_top_merchants_chart(
    spending_df: pd.DataFrame,
    excluded_categories: Optional[List[str]] = None,
    top_n: int = 10,
    height: Optional[int] = None
) -> go.Figure:
    """
    Create a horizontal bar chart of top merchants by total spending.
    
    Args:
        spending_df: DataFrame with columns ['Description', 'Amount', 'Category']
        excluded_categories: List of category names to exclude (default: ['Trip', 'Insurance', 'Mortgage'])
        top_n: Number of top merchants to show (default: 10)
        
    Returns:
        Plotly figure object
    """
    if excluded_categories is None:
        excluded_categories = ['Trip', 'Insurance', 'Mortgage']
    
    filtered_spending = spending_df[~spending_df['Category'].isin(excluded_categories)]

    merchant_summary = filtered_spending.groupby('Description').agg({
        'Amount': ['sum', 'count']
    }).reset_index()
    merchant_summary.columns = ['Description', 'Total', 'Transactions']

    top_by_total = merchant_summary.nlargest(top_n, 'Total').sort_values('Total', ascending=True)
    top_by_txn = merchant_summary.nlargest(top_n, 'Transactions').sort_values('Transactions', ascending=True)

    fig = make_subplots(
        rows=1,
        cols=2,
        shared_yaxes=False,
        horizontal_spacing=0.12,
        subplot_titles=('Total Spending', 'Transactions')
    )

    fig.add_trace(
        go.Bar(
            x=top_by_total['Total'],
            y=top_by_total['Description'],
            orientation='h',
            name='Total Spending',
            marker_color='steelblue',
            text=top_by_total['Total'].apply(lambda x: f'${x:,.2f}'),
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>Total: $%{x:,.2f}<extra></extra>'
        ),
        row=1,
        col=1
    )

    fig.add_trace(
        go.Bar(
            x=top_by_txn['Transactions'],
            y=top_by_txn['Description'],
            orientation='h',
            name='Transactions',
            marker_color='lightgrey',
            text=top_by_txn['Transactions'],
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>Transactions: %{x}<extra></extra>'
        ),
        row=1,
        col=2
    )

    fig.update_layout(
        title=f'Top {top_n} Merchants (All Time)',
        showlegend=False
    )
    fig.update_xaxes(title_text='Total Spending ($)', row=1, col=1)
    fig.update_xaxes(title_text='Transactions', row=1, col=2)
    fig.update_yaxes(title_text='Merchant', row=1, col=1)
    fig.update_yaxes(title_text='Merchant', row=1, col=2)

    if height is not None:
        fig.update_layout(height=height)
    
    return fig
