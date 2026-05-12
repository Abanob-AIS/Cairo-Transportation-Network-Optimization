# 🏙️ Cairo Transportation Network Optimizer

> Smart City Transportation Network Optimization System  
> **CSE112 — Design and Analysis of Algorithms**  
> Alamein International University

Live Demo: https://drive.google.com/file/d/18Xa98gIur07AksCTmxPRy4EbjpIpXWBE/view?usp=sharing
Hugging Face Demo: https://huggingface.co/spaces/Abanob-AIS/cairo-network


## 📋 Overview

A comprehensive transportation management system for the Greater Cairo metropolitan area that implements and integrates multiple algorithmic concepts to analyze, optimize, and manage urban transportation challenges including traffic congestion, infrastructure development, and public transit optimization.

## 🚀 Features

| Module | Algorithm | Description |
|--------|-----------|-------------|
| 🏗️ Infrastructure Design | Kruskal's & Prim's MST | Cost-efficient road network design prioritizing high-population areas |
| 🚗 Traffic Optimization | Dijkstra's (standard + time-dependent) | Optimal route planning with BPR congestion modeling |
| 🚑 Emergency Response | A* Search + Greedy Preemption | Emergency vehicle routing with signal preemption |
| 🚌 Public Transit | Dynamic Programming | Optimal bus allocation and road maintenance budgeting |
| 🚦 Traffic Signals | Greedy Algorithms | Real-time traffic signal timing optimization |
| 🤖 ML Prediction | Random Forest / Gradient Boosting | Traffic congestion prediction from temporal data |
| 📊 Comparison | All algorithms | Side-by-side performance visualization |

## 🛠️ Tech Stack

- **Python 3.11+** — Core language
- **Streamlit** — Interactive web UI
- **Plotly** — Data visualization
- **scikit-learn** — ML traffic prediction
- **NetworkX** — Graph utilities
- **Docker** — Containerization

## 📦 Installation

### Option 1: Local Setup

```bash
# Clone the repository
git clone <repo-url>
cd algo2

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

### Option 2: Docker

```bash
# Build and run with Docker Compose
docker-compose up --build

# OR build manually
docker build -t cairo-transport .
docker run -p 8501:8501 cairo-transport
```

Access the app at **http://localhost:8501**

## 🧪 Running Tests

```bash
# Run all tests
python -m tests.test_mst
python -m tests.test_shortest_path
python -m tests.test_dp
python -m tests.test_greedy
```

## 📁 Project Structure

```
algo2/
├── app.py                              # Main Streamlit home page
├── pages/
│   ├── 1_Infrastructure_Design.py      # MST algorithms
│   ├── 2_Traffic_Optimization.py       # Dijkstra's routing
│   ├── 3_Emergency_Response.py         # A* emergency routing
│   ├── 4_Public_Transit.py             # DP optimization
│   ├── 5_Traffic_Signals.py            # Greedy signals
│   ├── 6_ML_Prediction.py             # ML traffic prediction
│   └── 7_Algorithm_Comparison.py       # Performance comparison
├── src/
│   ├── data/cairo_data.py              # All Cairo transportation data
│   ├── models/graph.py                 # Graph data structure
│   ├── algorithms/
│   │   ├── mst.py                      # Kruskal's & Prim's
│   │   ├── shortest_path.py            # Dijkstra's & A*
│   │   ├── dynamic_programming.py      # DP solutions
│   │   ├── greedy.py                   # Greedy algorithms
│   │   └── ml_prediction.py            # ML prediction
│   └── visualization/
│       ├── network_viz.py              # Network visualizations
│       └── charts.py                   # Performance charts
├── tests/                              # Unit tests
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .streamlit/config.toml              # Dark theme config
```

## 📐 Complexity Analysis

| Algorithm | Time | Space |
|-----------|------|-------|
| Kruskal's MST | O(E log E) | O(V + E) |
| Prim's MST | O(E log V) | O(V + E) |
| Dijkstra's | O((V+E) log V) | O(V) |
| A* Search | O((V+E) log V) | O(V) |
| Bus Allocation DP | O(R × B × M) | O(R × B) |
| Road Maintenance DP | O(R × B²/G²) | O(R × B/G) |
| Signal Optimization | O(V × E) | O(V) |

## 📊 Data

The system uses real-world data for Greater Cairo:
- **15 neighborhoods** with population and type classification
- **10 important facilities** (hospitals, airports, universities)
- **28 existing roads** with distance, capacity, and condition ratings
- **15 potential new roads** with construction costs
- **28 traffic flow patterns** across 4 time periods
- **3 metro lines** and **10 bus routes** with passenger data

## 👤 Author

CSE112 — Design and Analysis of Algorithms  
Alamein International University  
Faculty of Computer Science & Engineering
