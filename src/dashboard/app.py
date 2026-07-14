import dash
from dash import dcc, html, dash_table, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import httpx
import pandas as pd
import os
import asyncio
from loguru import logger

# Configuration for reaching the FastAPI backend
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")

# Initialize Dash app with Darkly theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY], suppress_callback_exceptions=True)
server = app.server

def fetch_data(endpoint: str, params: dict = None) -> list:
    """Fetches data from the FastAPI backend."""
    try:
        response = httpx.get(f"{API_BASE_URL}/{endpoint}", params=params, timeout=10.0, follow_redirects=True)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"API Error fetching {endpoint}: {e}")
        return []

async def fetch_data_async(client, endpoint: str, params: dict = None) -> list:
    """Fetches data from the FastAPI backend asynchronously."""
    try:
        response = await client.get(f"{API_BASE_URL}/{endpoint}", params=params, timeout=10.0, follow_redirects=True)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"API Error fetching {endpoint}: {e}")
        return []

# Layout
app.layout = dbc.Container([
    dcc.Location(id='url', refresh=False),
    dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Employees", href="/employees")),
            dbc.NavItem(dbc.NavLink("Telemetry", href="/telemetry")),
            dbc.NavItem(dbc.NavLink("AI Report", href="/ai-report")),
        ],
        brand="Claude Code Analytics Platform",
        color="dark",
        dark=True,
    ),
    html.Div(id='page-content', className="p-4")
], fluid=True)

@callback(Output('page-content', 'children'),
          Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/telemetry':
        return render_telemetry_dashboard()
    elif pathname == '/ai-report':
        return render_ai_report_page()
    else:
        return render_employees_dashboard()

def render_ai_report_page():
    return dbc.Container([
        html.H2("🤖 AI Insights Report", className="mb-4"),
        dbc.Button("Generate AI Summary", id="generate-summary-btn", color="primary", className="mb-3"),
        dbc.Card([
            dbc.CardHeader("AI Insights"),
            dbc.CardBody(
                dcc.Loading(
                    dcc.Markdown(id="ai-summary-output", children="Click the button to generate a summary...")
                )
            )
        ])
    ], fluid=True)

@callback(
    Output('ai-summary-output', 'children'),
    [Input('generate-summary-btn', 'n_clicks')]
)
def update_ai_report(n_clicks):
    if not n_clicks:
        return "Click the button to generate a summary..."
    
    # Use synchronous call for simplicity in callback, or wrap in a thread/async
    try:
        response = httpx.get(f"{API_BASE_URL}/ai/telemetry-summary", timeout=60.0)
        if response.status_code == 200:
            return response.json().get("summary", "No summary generated.")
        else:
            return f"Error generating AI summary: {response.status_code}"
    except Exception as e:
        logger.error(f"Error fetching AI summary: {e}")
        return "Error generating AI summary."

def render_employees_dashboard():
    return dbc.Container([
        html.H2("🏢 Employees Overview", className="mb-4"),
        
        # Action Buttons
        dbc.Row([
            dbc.Col(dbc.Button("Seed Employee Data", id="seed-employee-btn", color="success", className="mr-2")),
            dbc.Col(dbc.Button("Delete Employee Data", id="delete-employee-btn", color="danger")),
        ], className="mb-4"),
        
        # Filters Card
        dbc.Card([
            dbc.CardHeader("Filters"),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.Label("Filter by Level"),
                        dcc.Dropdown(id='level-filter', multi=True, className="text-dark"),
                    ], md=3),
                    dbc.Col([
                        html.Label("Filter by Location"),
                        dcc.Dropdown(id='location-filter', multi=True, className="text-dark"),
                    ], md=3),
                    dbc.Col([
                        html.Label("Filter by Practice"),
                        dcc.Dropdown(id='practice-filter', multi=True, className="text-dark"),
                    ], md=3),
                    dbc.Col([
                        html.Label("Search by Name or Email"),
                        dcc.Input(id='search-input', type='text', placeholder="Enter name or email...", className="form-control"),
                    ], md=3),
                ]),
            ])
        ], className="mb-4"),
        
        # Charts Row
        dbc.Row([
            dbc.Col(dbc.Card([dbc.CardHeader("Distribution by Level"), dbc.CardBody(dcc.Loading(dcc.Graph(id='level-chart')))]), width=4),
            dbc.Col(dbc.Card([dbc.CardHeader("Distribution by Location"), dbc.CardBody(dcc.Loading(dcc.Graph(id='location-chart')))]), width=4),
            dbc.Col(dbc.Card([dbc.CardHeader("Distribution by Practice"), dbc.CardBody(dcc.Loading(dcc.Graph(id='practice-chart')))]), width=4),
        ], className="mb-4"),
        
        # Data Table Card
        dbc.Card([
            dbc.CardHeader("Employee Records"),
            dbc.CardBody(
                dcc.Loading(
                    dash_table.DataTable(
                        id='employee-table', 
                        page_size=10, 
                        style_table={'overflowX': 'auto'},
                        style_cell={'backgroundColor': '#222', 'color': '#fff', 'border': '1px solid #444'},
                        style_header={'backgroundColor': '#333', 'color': '#fff', 'fontWeight': 'bold'}
                    )
                )
            )
        ])
    ], fluid=True)

@callback(
    [Output('level-filter', 'options'),
     Output('location-filter', 'options'),
     Output('practice-filter', 'options'),
     Output('employee-table', 'data'),
     Output('employee-table', 'columns'),
     Output('level-chart', 'figure'),
     Output('location-chart', 'figure'),
     Output('practice-chart', 'figure')],
    [Input('level-filter', 'value'),
     Input('location-filter', 'value'),
     Input('practice-filter', 'value'),
     Input('search-input', 'value'),
     Input('seed-employee-btn', 'n_clicks'),
     Input('delete-employee-btn', 'n_clicks')]
)
def update_employees_dashboard(level, location, practice, search_query, seed_clicks, delete_clicks):
    # Handle seeding/deletion
    ctx = dash.callback_context
    if ctx.triggered:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id == 'seed-employee-btn':
            httpx.post(f"{API_BASE_URL}/employees/seed")
        elif button_id == 'delete-employee-btn':
            httpx.delete(f"{API_BASE_URL}/employees")
            
    data = fetch_data("employees?limit=1000")
    if not data:
        return [], [], [], [], [], {}, {}, {}
    
    df = pd.DataFrame(data)
    
    # Get unique options
    level_opts = [{"label": i, "value": i} for i in df["level"].dropna().unique()]
    loc_opts = [{"label": i, "value": i} for i in df["location"].dropna().unique()]
    prac_opts = [{"label": i, "value": i} for i in df["practice"].dropna().unique()]
    
    # Apply filters
    filtered_df = df.copy()
    if level:
        filtered_df = filtered_df[filtered_df["level"].isin(level)]
    if location:
        filtered_df = filtered_df[filtered_df["location"].isin(location)]
    if practice:
        filtered_df = filtered_df[filtered_df["practice"].isin(practice)]
    if search_query:
        query = search_query.lower()
        filtered_df = filtered_df[
            filtered_df["full_name"].str.lower().str.contains(query, na=False) |
            filtered_df["email"].str.lower().str.contains(query, na=False)
        ]
        
    # Charts with plotly_dark template
    level_fig = px.pie(filtered_df, names='level', template='plotly_dark')
    loc_fig = px.pie(filtered_df, names='location', template='plotly_dark')
    prac_fig = px.pie(filtered_df, names='practice', template='plotly_dark')
    
    # Update chart margins for better fit in cards
    for fig in [level_fig, loc_fig, prac_fig]:
        fig.update_layout(margin=dict(t=20, b=20, l=20, r=20))
    
    table_data = filtered_df.to_dict('records')
    table_cols = [{"name": i, "id": i} for i in df.columns]
    
    return level_opts, loc_opts, prac_opts, table_data, table_cols, level_fig, loc_fig, prac_fig

def render_telemetry_dashboard():
    return dbc.Container([
        html.H2("📡 Telemetry Analytics", className="mb-4"),
        
        dcc.Loading([
            # KPI Cards (Usage Overview)
            dbc.Row(id="telemetry-kpis", className="mb-4"),
            
            # Activity Chart
            dbc.Row([
                dbc.Col(dbc.Card([dbc.CardHeader("Activity Over Time"), dbc.CardBody(dcc.Graph(id='telemetry-activity-chart'))]), width=12),
            ], className="mb-4"),
            
            # Other Analytics
            dbc.Row([
                dbc.Col(dbc.Card([dbc.CardHeader("Cost by Model"), dbc.CardBody(dcc.Graph(id='telemetry-cost-chart'))]), width=6),
                dbc.Col(dbc.Card([dbc.CardHeader("Token Usage by Model"), dbc.CardBody(dcc.Graph(id='telemetry-token-chart'))]), width=6),
            ], className="mb-4"),
            dbc.Row([
                dbc.Col(dbc.Card([dbc.CardHeader("Tool Usage"), dbc.CardBody(dcc.Graph(id='telemetry-tool-chart'))]), width=12),
            ], className="mb-4"),
            
            # New Event Distribution Row
            dbc.Row([
                dbc.Col(dbc.Card([dbc.CardHeader("Event Type Distribution"), dbc.CardBody(dcc.Graph(id='telemetry-event-dist-chart'))]), width=6),
                dbc.Col(dbc.Card([dbc.CardHeader("Terminal Breakdown"), dbc.CardBody(dcc.Graph(id='telemetry-terminal-chart'))]), width=6),
            ], className="mb-4"),
            
            # Data Tables
            dbc.Row([
                dbc.Col(dbc.Card([dbc.CardHeader("Error Analysis"), dbc.CardBody(dcc.Graph(id='error-analysis-chart'))]), width=12),
            ])
        ])
    ], fluid=True)

@callback(
    [Output('telemetry-kpis', 'children'),
     Output('telemetry-activity-chart', 'figure'),
     Output('telemetry-cost-chart', 'figure'),
     Output('telemetry-token-chart', 'figure'),
     Output('telemetry-tool-chart', 'figure'),
     Output('telemetry-event-dist-chart', 'figure'),
     Output('telemetry-terminal-chart', 'figure'),
     Output('error-analysis-chart', 'figure')],
    [Input('url', 'pathname')]
)
def update_telemetry_dashboard(_):
    # Fetch data in parallel
    return asyncio.run(update_telemetry_dashboard_async())

async def update_telemetry_dashboard_async():
    async with httpx.AsyncClient() as client:
        # Fetch data from new endpoints in parallel
        results = await asyncio.gather(
            fetch_data_async(client, "telemetry/usage-overview"),
            fetch_data_async(client, "telemetry/activity-over-time"),
            fetch_data_async(client, "telemetry/cost-breakdown"),
            fetch_data_async(client, "telemetry/tool-usage"),
            fetch_data_async(client, "telemetry/event-type-distribution"),
            fetch_data_async(client, "telemetry/terminal-breakdown"),
            fetch_data_async(client, "telemetry/error-analysis")
        )
        
        overview, activity, cost, tools, event_dist, terminal_breakdown, errors = results
    
    # ... KPI Cards ...
    kpis = [
        dbc.Col(dbc.Card([dbc.CardBody([html.H4("Prompts"), html.H2(overview.get("total_prompts", 0))])], color="primary", outline=True)),
        dbc.Col(dbc.Card([dbc.CardBody([html.H4("Sessions"), html.H2(overview.get("total_sessions", 0))])], color="secondary", outline=True)),
        dbc.Col(dbc.Card([dbc.CardBody([html.H4("Tool Calls"), html.H2(overview.get("total_tool_calls", 0))])], color="warning", outline=True)),
        dbc.Col(dbc.Card([dbc.CardBody([html.H4("API Requests"), html.H2(overview.get("total_api_requests", 0))])], color="success", outline=True)),
        dbc.Col(dbc.Card([dbc.CardBody([html.H4("Cost (USD)"), html.H2(f"${overview.get('total_cost_usd', 0):.2f}")])], color="info", outline=True)),
        dbc.Col(dbc.Card([dbc.CardBody([html.H4("Errors"), html.H2(overview.get("total_errors", 0))])], color="danger", outline=True)),
    ]
    
    # Activity Chart
    activity_fig = {}
    if activity:
        df_act = pd.DataFrame(activity)
        if not df_act.empty:
            df_melted = df_act.melt(id_vars='day', value_vars=['prompt_count', 'request_count'], var_name='type', value_name='count')
            activity_fig = px.line(df_melted, x='day', y='count', color='type', title="Activity Over Time", template='plotly_dark', labels={'day': 'Date', 'count': 'Count', 'type': 'Event Type'})
        else:
            activity_fig = px.line(title="No activity data available", template='plotly_dark')
    
    cost_fig = {}
    token_fig = {}
    if cost:
        df_cost = pd.DataFrame(cost)
        cost_fig = px.bar(df_cost, x='model', y='cost', title="Cost by Model", template='plotly_dark', labels={'model': 'Model', 'cost': 'Cost (USD)'})
        
        # Token Usage Chart
        df_tokens = df_cost.melt(id_vars='model', value_vars=['input_tokens', 'output_tokens'], var_name='token_type', value_name='count')
        token_fig = px.bar(df_tokens, x='model', y='count', color='token_type', barmode='group', title="Tokens by Model", template='plotly_dark', labels={'model': 'Model', 'count': 'Token Count'})
        
    tool_fig = {}
    if tools and 'results' in tools:
        df_tools = pd.DataFrame(tools['results'])
        tool_fig = px.bar(df_tools, x='tool_name', y='total_calls', title="Tool Usage", template='plotly_dark', labels={'tool_name': 'Tool Name', 'total_calls': 'Total Calls'})
        
    # Event Distribution Pie Chart
    dist_fig = {}
    if event_dist:
        df_dist = pd.DataFrame(event_dist)
        dist_fig = px.pie(df_dist, names='event_type', values='count', title="Event Type Distribution", template='plotly_dark')

    # Terminal Breakdown Pie Chart
    term_fig = {}
    if terminal_breakdown:
        df_term = pd.DataFrame(terminal_breakdown)
        term_fig = px.pie(df_term, names='terminal_type', values='count', title="Terminal Breakdown", template='plotly_dark')
        
    # Error Analysis Chart
    error_fig = {}
    if errors:
        df_errors = pd.DataFrame(errors)
        error_fig = px.bar(df_errors, x='model', y='count', color='error', title="Error Analysis", template='plotly_dark', labels={'model': 'Model', 'count': 'Error Count', 'error': 'Error Message'})

    return kpis, activity_fig, cost_fig, token_fig, tool_fig, dist_fig, term_fig, error_fig

if __name__ == "__main__":
    app.run(debug=True, port=8501, host="0.0.0.0")
