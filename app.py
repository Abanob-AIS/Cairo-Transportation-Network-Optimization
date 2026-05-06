"""
Smart City Transportation Network Optimization
=================================================
Main Streamlit application - Home page with system overview.
CSE112 - Design and Analysis of Algorithms
Alamein International University
"""
import streamlit as st

st.set_page_config(
    page_title="Cairo Transportation Optimizer",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    .main { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); }
    
    .stApp { background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%); }
    
    .hero-title {
        font-size: 3rem; font-weight: 700;
        background: linear-gradient(135deg, #00d2ff, #3a7bd5, #00d2ff);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; margin-bottom: 0.5rem;
    }
    .hero-subtitle {
        font-size: 1.2rem; color: #a0aec0; text-align: center; margin-bottom: 2rem;
    }
    .feature-card {
        background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1);
        border-radius: 16px; padding: 1.5rem; margin: 0.5rem 0;
        backdrop-filter: blur(10px); transition: transform 0.3s, border-color 0.3s;
    }
    .feature-card:hover { transform: translateY(-2px); border-color: rgba(0,210,255,0.5); }
    .feature-card h3 { color: #00d2ff; margin-bottom: 0.5rem; }
    .feature-card p { color: #cbd5e0; font-size: 0.9rem; }
    
    .metric-card {
        background: rgba(255,255,255,0.08); border-radius: 12px; padding: 1.2rem;
        text-align: center; border: 1px solid rgba(255,255,255,0.1);
    }
    .metric-value { font-size: 2rem; font-weight: 700; color: #00d2ff; }
    .metric-label { font-size: 0.85rem; color: #a0aec0; }
    
    .algo-badge {
        display: inline-block; padding: 4px 12px; border-radius: 20px;
        font-size: 0.75rem; font-weight: 600; margin: 2px;
        background: rgba(0,210,255,0.15); color: #00d2ff; border: 1px solid rgba(0,210,255,0.3);
    }
    
    section[data-testid="stSidebar"] { background: rgba(15,12,41,0.95); }
    
    div[data-testid="stMetric"] {
        background: rgba(255,255,255,0.05); border-radius: 12px; padding: 1rem;
        border: 1px solid rgba(255,255,255,0.1);
    }
</style>
""", unsafe_allow_html=True)

# ── Hero Section ────────────────────────────────────────────────────────────
st.markdown('<h1 class="hero-title">🏙️ Cairo Transportation Optimizer</h1>', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">Smart City Transportation Network Optimization System<br>'
            '<em>CSE112 — Design and Analysis of Algorithms</em></p>', unsafe_allow_html=True)

# ── Network Stats ───────────────────────────────────────────────────────────
from src.data.cairo_data import NEIGHBORHOODS, FACILITIES, EXISTING_ROADS, POTENTIAL_ROADS, METRO_LINES, BUS_ROUTES

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("🏘️ Neighborhoods", len(NEIGHBORHOODS))
col2.metric("🏥 Facilities", len(FACILITIES))
col3.metric("🛣️ Existing Roads", len(EXISTING_ROADS))
col4.metric("🚇 Metro Lines", len(METRO_LINES))
col5.metric("🚌 Bus Routes", len(BUS_ROUTES))

st.divider()

# ── Feature Cards ───────────────────────────────────────────────────────────
st.markdown("### 📋 System Modules")

features = [
    ("🏗️ Infrastructure Design", "MST algorithms (Kruskal's & Prim's) to design cost-efficient road networks prioritizing high-population areas and critical facilities.",
     "Kruskal's, Prim's, Union-Find"),
    ("🚗 Traffic Optimization", "Dijkstra's algorithm with time-dependent traffic modeling using BPR congestion function for optimal route planning.",
     "Dijkstra's, BPR Function"),
    ("🚑 Emergency Response", "A* search with Haversine heuristic for emergency vehicle routing with signal preemption at intersections.",
     "A*, Haversine, Greedy Preemption"),
    ("🚌 Public Transit", "Dynamic programming for optimal bus allocation and road maintenance budget distribution with diminishing returns model.",
     "Knapsack DP, Memoization"),
    ("🚦 Traffic Signals", "Greedy approach for real-time traffic signal optimization with proportional green-time allocation.",
     "Greedy, Priority Queue"),
    ("🤖 ML Prediction", "Random Forest / Gradient Boosting models trained on temporal traffic data to forecast congestion levels.",
     "Random Forest, Cross-Validation"),
]

cols = st.columns(3)
for i, (title, desc, algos) in enumerate(features):
    with cols[i % 3]:
        algo_badges = "".join(f'<span class="algo-badge">{a.strip()}</span>' for a in algos.split(","))
        st.markdown(f'''<div class="feature-card">
            <h3>{title}</h3>
            <p>{desc}</p>
            <div style="margin-top: 0.8rem">{algo_badges}</div>
        </div>''', unsafe_allow_html=True)

st.divider()

# ── Network Preview ─────────────────────────────────────────────────────────
st.markdown("### 🗺️ Network Overview")
from src.models.graph import TransportationGraph
from src.visualization.network_viz import plot_network

graph = TransportationGraph(include_potential=False)
fig = plot_network(title="Greater Cairo Transportation Network")
st.plotly_chart(fig, use_container_width=True)

# ── Population Distribution ─────────────────────────────────────────────────
st.markdown("### 📊 Population Distribution")
import plotly.graph_objects as go

sorted_areas = sorted(NEIGHBORHOODS.items(), key=lambda x: x[1]["population"], reverse=True)
names = [d["name"] for _, d in sorted_areas]
pops = [d["population"] for _, d in sorted_areas]
colors = ["#4FC3F7" if d["type"] == "Residential" else "#81C784" if d["type"] == "Mixed"
          else "#FFB74D" if d["type"] == "Business" else "#E57373" if d["type"] == "Industrial"
          else "#CE93D8" for _, d in sorted_areas]

pop_fig = go.Figure(go.Bar(x=names, y=pops, marker_color=colors,
                           text=[f"{p:,}" for p in pops], textposition="auto"))
pop_fig.update_layout(
    title="Neighborhood Population", xaxis_title="", yaxis_title="Population",
    plot_bgcolor="#1a1a2e", paper_bgcolor="#16213e", font=dict(color="white"),
    height=400, xaxis=dict(tickangle=45, color="white"), yaxis=dict(color="white"),
)
st.plotly_chart(pop_fig, use_container_width=True)

# ── Footer ──────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<p style="text-align:center; color:#64748b; font-size:0.85rem;">'
    'Smart City Transportation Optimizer • CSE112 Project • '
    'Alamein International University</p>',
    unsafe_allow_html=True,
)
