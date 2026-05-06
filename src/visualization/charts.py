"""
Performance Charts
====================
Plotly charts for algorithm analysis, comparison, and traffic flow visualization.
"""
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import time


DARK_THEME = dict(
    plot_bgcolor="#1a1a2e", paper_bgcolor="#16213e",
    font=dict(color="white"),
)


def plot_complexity_comparison(results, title="Algorithm Complexity Comparison"):
    """Bar chart comparing algorithm performance metrics."""
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Execution Time", "Nodes Explored"))
    names = [r.get("algorithm", "?") for r in results]
    times = [r.get("execution_time", 0) * 1000 for r in results]
    explored = [r.get("nodes_explored", r.get("steps", 0)) for r in results]
    colors = ["#4FC3F7", "#81C784", "#FFB74D", "#E57373", "#CE93D8"]

    fig.add_trace(go.Bar(x=names, y=times, marker_color=colors[:len(names)],
                         text=[f"{t:.3f}ms" for t in times], textposition="auto",
                         name="Time (ms)"), row=1, col=1)
    fig.add_trace(go.Bar(x=names, y=explored, marker_color=colors[:len(names)],
                         text=explored, textposition="auto",
                         name="Nodes/Steps"), row=1, col=2)
    fig.update_layout(title=title, showlegend=False, height=400, **DARK_THEME)
    
    # ✅ Force categorical axis to prevent datetime interpretation
    fig.update_xaxes(type='category', color="white")
    fig.update_yaxes(color="white")
    return fig


def plot_traffic_flow(time_periods_data, road_label=""):
    """Line chart showing traffic flow across time periods."""
    periods = ["Morning", "Afternoon", "Evening", "Night"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=periods, y=time_periods_data, mode="lines+markers",
        line=dict(width=3, color="#4FC3F7"),
        marker=dict(size=10, color="#4FC3F7"),
        fill="tozeroy", fillcolor="rgba(79,195,247,0.2)",
        name=road_label or "Traffic Flow",
    ))
    fig.update_layout(
        title=f"Traffic Flow Pattern {road_label}",
        xaxis_title="Time Period", yaxis_title="Vehicles/Hour",
        height=350, **DARK_THEME,
    )
    
    # ✅ Force categorical axis to prevent datetime interpretation
    fig.update_xaxes(type='category', color="white")
    fig.update_yaxes(color="white")
    return fig


def plot_algorithm_race(dijkstra_result, astar_result, graph):
    """Side-by-side comparison of Dijkstra vs A* exploration."""
    fig = make_subplots(rows=1, cols=2,
                        subplot_titles=("Dijkstra's Algorithm", "A* Search"))
    
    metrics = [
        ("Nodes Explored", dijkstra_result.get("nodes_explored", 0), astar_result.get("nodes_explored", 0)),
        ("Execution Time (ms)", dijkstra_result.get("execution_time", 0)*1000, astar_result.get("execution_time", 0)*1000),
        ("Path Length", dijkstra_result.get("path_distance", 0), astar_result.get("path_distance", 0)),
    ]

    categories = [m[0] for m in metrics]
    fig.add_trace(go.Bar(
        x=categories, y=[m[1] for m in metrics],
        marker_color="#4FC3F7", name="Dijkstra's",
        text=[f"{m[1]:.2f}" for m in metrics], textposition="auto",
    ), row=1, col=1)
    fig.add_trace(go.Bar(
        x=categories, y=[m[2] for m in metrics],
        marker_color="#FF6B35", name="A*",
        text=[f"{m[2]:.2f}" for m in metrics], textposition="auto",
    ), row=1, col=2)

    fig.update_layout(title="Dijkstra's vs A* Performance", height=400, **DARK_THEME)
    
    # ✅ Force categorical axis to prevent datetime interpretation
    fig.update_xaxes(type='category', color="white")
    fig.update_yaxes(color="white")
    return fig


def plot_bus_allocation(allocation_data):
    """Bar chart of bus allocation per route."""
    routes = list(allocation_data.keys())
    buses = [allocation_data[r]["buses"] for r in routes]
    passengers = [allocation_data[r]["passengers_served"] for r in routes]

    fig = make_subplots(rows=1, cols=2,
                        subplot_titles=("Buses Allocated", "Passengers Served"))
    fig.add_trace(go.Bar(x=routes, y=buses, marker_color="#81C784",
                         text=buses, textposition="auto", name="Buses"), row=1, col=1)
    fig.add_trace(go.Bar(x=routes, y=passengers, marker_color="#FFB74D",
                         text=[f"{p:,}" for p in passengers], textposition="auto",
                         name="Passengers"), row=1, col=2)
    fig.update_layout(title="Optimal Bus Allocation (DP)", height=400, showlegend=False, **DARK_THEME)
    
    # ✅ Force categorical axis to prevent datetime interpretation
    fig.update_xaxes(type='category', color="white")
    fig.update_yaxes(color="white")
    return fig


def plot_maintenance_allocation(allocations):
    """Horizontal bar chart of road maintenance budget allocation."""
    if not allocations:
        fig = go.Figure()
        fig.add_annotation(text="No allocation needed", showarrow=False)
        fig.update_layout(**DARK_THEME)
        return fig

    roads = list(allocations.keys())
    investments = [allocations[r]["investment_million_egp"] for r in roads]
    improvements = [allocations[r]["improvement_score"] for r in roads]
    conditions = [allocations[r]["current_condition"] for r in roads]

    fig = make_subplots(rows=1, cols=2,
                        subplot_titles=("Investment (M EGP)", "Improvement Score"))
    
    fig.add_trace(go.Bar(y=roads, x=investments, orientation="h",
                         marker_color="#E57373", text=[f"{v}M" for v in investments],
                         textposition="auto", name="Investment"), row=1, col=1)
    fig.add_trace(go.Bar(y=roads, x=improvements, orientation="h",
                         marker_color="#4FC3F7", text=[f"{v:.1f}" for v in improvements],
                         textposition="auto", name="Improvement"), row=1, col=2)
    
    fig.update_layout(title="Road Maintenance Budget Allocation (DP)", 
                      height=max(300, len(roads)*40),
                      showlegend=False, **DARK_THEME)
    
    # ✅ Force categorical axis to prevent datetime interpretation
    # This fixes the issue where road names like "1-3" were being interpreted as dates (Jan 2003, etc.)
    fig.update_xaxes(type='category', color="white")
    fig.update_yaxes(type='category', color="white")
    
    return fig


def plot_signal_timing(signal_plan, intersection_name):
    """Pie chart of signal timing at an intersection."""
    labels = [f"From {s['from']}" for s in signal_plan]
    values = [s["green_time"] for s in signal_plan]
    colors = ["#4FC3F7", "#81C784", "#FFB74D", "#E57373", "#CE93D8", "#FF8A65"]

    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.4,
        marker=dict(colors=colors[:len(labels)]),
        textinfo="label+value",
        textfont=dict(color="white"),
    ))
    fig.update_layout(
        title=f"Signal Timing: {intersection_name}",
        height=350, **DARK_THEME,
    )
    return fig


def plot_prediction_results(predictions):
    """Bar chart of ML traffic predictions vs capacity."""
    roads = list(predictions.keys())[:15]
    predicted = [predictions[r]["predicted_flow"] for r in roads]
    capacity = [predictions[r]["road"]["capacity"] for r in roads]

    fig = go.Figure()
    fig.add_trace(go.Bar(x=roads, y=capacity, name="Capacity", marker_color="#4FC3F7", opacity=0.6))
    fig.add_trace(go.Bar(x=roads, y=predicted, name="Predicted Flow", marker_color="#FF6B35"))
    fig.update_layout(
        title="ML Traffic Predictions vs Road Capacity",
        xaxis_title="Road Segment", yaxis_title="Vehicles/Hour",
        barmode="overlay", height=450, **DARK_THEME,
    )
    
    # ✅ Force categorical axis to prevent datetime interpretation
    fig.update_xaxes(type='category', color="white", tickangle=45)
    fig.update_yaxes(color="white")
    return fig