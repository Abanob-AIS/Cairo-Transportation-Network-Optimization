"""
Cairo Transportation Network Data
===================================
All geographic, road network, traffic flow, and public transportation data
for the Greater Cairo metropolitan area as provided by the city administration.
"""

# =============================================================================
# Neighborhoods and Districts
# Format: ID -> {name, population, type, x (longitude), y (latitude)}
# =============================================================================
NEIGHBORHOODS = {
    "1":  {"name": "Maadi",                     "population": 250000, "type": "Residential", "x": 31.25, "y": 29.96},
    "2":  {"name": "Nasr City",                 "population": 500000, "type": "Mixed",       "x": 31.34, "y": 30.06},
    "3":  {"name": "Downtown Cairo",            "population": 100000, "type": "Business",    "x": 31.24, "y": 30.04},
    "4":  {"name": "New Cairo",                 "population": 300000, "type": "Residential", "x": 31.47, "y": 30.03},
    "5":  {"name": "Heliopolis",                "population": 200000, "type": "Mixed",       "x": 31.32, "y": 30.09},
    "6":  {"name": "Zamalek",                   "population":  50000, "type": "Residential", "x": 31.22, "y": 30.06},
    "7":  {"name": "6th October City",          "population": 400000, "type": "Mixed",       "x": 30.98, "y": 29.93},
    "8":  {"name": "Giza",                      "population": 550000, "type": "Mixed",       "x": 31.21, "y": 29.99},
    "9":  {"name": "Mohandessin",               "population": 180000, "type": "Business",    "x": 31.20, "y": 30.05},
    "10": {"name": "Dokki",                     "population": 220000, "type": "Mixed",       "x": 31.21, "y": 30.03},
    "11": {"name": "Shubra",                    "population": 450000, "type": "Residential", "x": 31.24, "y": 30.11},
    "12": {"name": "Helwan",                    "population": 350000, "type": "Industrial",  "x": 31.33, "y": 29.85},
    "13": {"name": "New Administrative Capital", "population":  50000, "type": "Government", "x": 31.80, "y": 30.02},
    "14": {"name": "Al Rehab",                  "population": 120000, "type": "Residential", "x": 31.49, "y": 30.06},
    "15": {"name": "Sheikh Zayed",              "population": 150000, "type": "Residential", "x": 30.94, "y": 30.01},
}

# =============================================================================
# Important Facilities
# Format: ID -> {name, type, x (longitude), y (latitude)}
# =============================================================================
FACILITIES = {
    "F1":  {"name": "Cairo International Airport",  "type": "Airport",    "x": 31.41, "y": 30.11},
    "F2":  {"name": "Ramses Railway Station",        "type": "Transit Hub","x": 31.25, "y": 30.06},
    "F3":  {"name": "Cairo University",              "type": "Education",  "x": 31.21, "y": 30.03},
    "F4":  {"name": "Al-Azhar University",           "type": "Education",  "x": 31.26, "y": 30.05},
    "F5":  {"name": "Egyptian Museum",               "type": "Tourism",    "x": 31.23, "y": 30.05},
    "F6":  {"name": "Cairo International Stadium",   "type": "Sports",     "x": 31.30, "y": 30.07},
    "F7":  {"name": "Smart Village",                 "type": "Business",   "x": 30.97, "y": 30.07},
    "F8":  {"name": "Cairo Festival City",           "type": "Commercial", "x": 31.40, "y": 30.03},
    "F9":  {"name": "Qasr El Aini Hospital",         "type": "Medical",    "x": 31.23, "y": 30.03},
    "F10": {"name": "Maadi Military Hospital",       "type": "Medical",    "x": 31.25, "y": 29.95},
}

# Critical facility types that require enhanced connectivity
CRITICAL_FACILITY_TYPES = {"Medical", "Government", "Transit Hub", "Airport"}

# =============================================================================
# All nodes combined (neighborhoods + facilities)
# =============================================================================
def get_all_nodes():
    """Return a merged dictionary of all neighborhoods and facilities."""
    nodes = {}
    for nid, data in NEIGHBORHOODS.items():
        nodes[nid] = {**data, "category": "neighborhood"}
    for fid, data in FACILITIES.items():
        nodes[fid] = {**data, "category": "facility", "population": 0}
    return nodes

# =============================================================================
# Existing Road Network
# Format: list of {from, to, distance_km, capacity_vph, condition}
# =============================================================================
EXISTING_ROADS = [
    {"from": "1",  "to": "3",   "distance": 8.5,  "capacity": 3000, "condition": 7},
    {"from": "1",  "to": "8",   "distance": 6.2,  "capacity": 2500, "condition": 6},
    {"from": "2",  "to": "3",   "distance": 5.9,  "capacity": 2800, "condition": 8},
    {"from": "2",  "to": "5",   "distance": 4.0,  "capacity": 3200, "condition": 9},
    {"from": "3",  "to": "5",   "distance": 6.1,  "capacity": 3500, "condition": 7},
    {"from": "3",  "to": "6",   "distance": 3.2,  "capacity": 2000, "condition": 8},
    {"from": "3",  "to": "9",   "distance": 4.5,  "capacity": 2600, "condition": 6},
    {"from": "3",  "to": "10",  "distance": 3.8,  "capacity": 2400, "condition": 7},
    {"from": "4",  "to": "2",   "distance": 15.2, "capacity": 3800, "condition": 9},
    {"from": "4",  "to": "14",  "distance": 5.3,  "capacity": 3000, "condition": 10},
    {"from": "5",  "to": "11",  "distance": 7.9,  "capacity": 3100, "condition": 7},
    {"from": "6",  "to": "9",   "distance": 2.2,  "capacity": 1800, "condition": 8},
    {"from": "7",  "to": "8",   "distance": 24.5, "capacity": 3500, "condition": 8},
    {"from": "7",  "to": "15",  "distance": 9.8,  "capacity": 3000, "condition": 9},
    {"from": "8",  "to": "10",  "distance": 3.3,  "capacity": 2200, "condition": 7},
    {"from": "8",  "to": "12",  "distance": 14.8, "capacity": 2600, "condition": 5},
    {"from": "9",  "to": "10",  "distance": 2.1,  "capacity": 1900, "condition": 7},
    {"from": "10", "to": "11",  "distance": 8.7,  "capacity": 2400, "condition": 6},
    {"from": "11", "to": "F2",  "distance": 3.6,  "capacity": 2200, "condition": 7},
    {"from": "12", "to": "1",   "distance": 12.7, "capacity": 2800, "condition": 6},
    {"from": "13", "to": "4",   "distance": 45.0, "capacity": 4000, "condition": 10},
    {"from": "14", "to": "13",  "distance": 35.5, "capacity": 3800, "condition": 9},
    {"from": "15", "to": "7",   "distance": 9.8,  "capacity": 3000, "condition": 9},
    {"from": "F1", "to": "5",   "distance": 7.5,  "capacity": 3500, "condition": 9},
    {"from": "F1", "to": "2",   "distance": 9.2,  "capacity": 3200, "condition": 8},
    {"from": "F2", "to": "3",   "distance": 2.5,  "capacity": 2000, "condition": 7},
    {"from": "F7", "to": "15",  "distance": 8.3,  "capacity": 2800, "condition": 8},
    {"from": "F8", "to": "4",   "distance": 6.1,  "capacity": 3000, "condition": 9},
]

# =============================================================================
# Potential New Roads
# Format: list of {from, to, distance_km, capacity_vph, cost_million_egp}
# =============================================================================
POTENTIAL_ROADS = [
    {"from": "1",  "to": "4",   "distance": 22.8, "capacity": 4000, "cost": 450},
    {"from": "1",  "to": "14",  "distance": 25.3, "capacity": 3800, "cost": 500},
    {"from": "2",  "to": "13",  "distance": 48.2, "capacity": 4500, "cost": 950},
    {"from": "3",  "to": "13",  "distance": 56.7, "capacity": 4500, "cost": 1100},
    {"from": "5",  "to": "4",   "distance": 16.8, "capacity": 3500, "cost": 320},
    {"from": "6",  "to": "8",   "distance": 7.5,  "capacity": 2500, "cost": 150},
    {"from": "7",  "to": "13",  "distance": 82.3, "capacity": 4000, "cost": 1600},
    {"from": "9",  "to": "11",  "distance": 6.9,  "capacity": 2800, "cost": 140},
    {"from": "10", "to": "F7",  "distance": 27.4, "capacity": 3200, "cost": 550},
    {"from": "11", "to": "13",  "distance": 62.1, "capacity": 4200, "cost": 1250},
    {"from": "12", "to": "14",  "distance": 30.5, "capacity": 3600, "cost": 610},
    {"from": "14", "to": "5",   "distance": 18.2, "capacity": 3300, "cost": 360},
    {"from": "15", "to": "9",   "distance": 22.7, "capacity": 3000, "cost": 450},
    {"from": "F1", "to": "13",  "distance": 40.2, "capacity": 4000, "cost": 800},
    {"from": "F7", "to": "9",   "distance": 26.8, "capacity": 3200, "cost": 540},
]

# =============================================================================
# Traffic Flow Patterns (vehicles per hour by time of day)
# Format: (from_id, to_id) -> {morning, afternoon, evening, night}
# =============================================================================
TRAFFIC_FLOW = {
    ("1",  "3"):   {"morning": 2800, "afternoon": 1500, "evening": 2600, "night": 800},
    ("1",  "8"):   {"morning": 2200, "afternoon": 1200, "evening": 2100, "night": 600},
    ("2",  "3"):   {"morning": 2700, "afternoon": 1400, "evening": 2500, "night": 700},
    ("2",  "5"):   {"morning": 3000, "afternoon": 1600, "evening": 2800, "night": 650},
    ("3",  "5"):   {"morning": 3200, "afternoon": 1700, "evening": 3100, "night": 800},
    ("3",  "6"):   {"morning": 1800, "afternoon": 1400, "evening": 1900, "night": 500},
    ("3",  "9"):   {"morning": 2400, "afternoon": 1300, "evening": 2200, "night": 550},
    ("3",  "10"):  {"morning": 2300, "afternoon": 1200, "evening": 2100, "night": 500},
    ("4",  "2"):   {"morning": 3600, "afternoon": 1800, "evening": 3300, "night": 750},
    ("4",  "14"):  {"morning": 2800, "afternoon": 1600, "evening": 2600, "night": 600},
    ("5",  "11"):  {"morning": 2900, "afternoon": 1500, "evening": 2700, "night": 650},
    ("6",  "9"):   {"morning": 1700, "afternoon": 1300, "evening": 1800, "night": 450},
    ("7",  "8"):   {"morning": 3200, "afternoon": 1700, "evening": 3000, "night": 700},
    ("7",  "15"):  {"morning": 2800, "afternoon": 1500, "evening": 2600, "night": 600},
    ("8",  "10"):  {"morning": 2000, "afternoon": 1100, "evening": 1900, "night": 450},
    ("8",  "12"):  {"morning": 2400, "afternoon": 1300, "evening": 2200, "night": 500},
    ("9",  "10"):  {"morning": 1800, "afternoon": 1200, "evening": 1700, "night": 400},
    ("10", "11"):  {"morning": 2200, "afternoon": 1300, "evening": 2100, "night": 500},
    ("11", "F2"):  {"morning": 2100, "afternoon": 1200, "evening": 2000, "night": 450},
    ("12", "1"):   {"morning": 2600, "afternoon": 1400, "evening": 2400, "night": 550},
    ("13", "4"):   {"morning": 3800, "afternoon": 2000, "evening": 3500, "night": 800},
    ("14", "13"):  {"morning": 3600, "afternoon": 1900, "evening": 3300, "night": 750},
    ("15", "7"):   {"morning": 2800, "afternoon": 1500, "evening": 2600, "night": 600},
    ("F1", "5"):   {"morning": 3300, "afternoon": 2200, "evening": 3100, "night": 1200},
    ("F1", "2"):   {"morning": 3000, "afternoon": 2000, "evening": 2800, "night": 1100},
    ("F2", "3"):   {"morning": 1900, "afternoon": 1600, "evening": 1800, "night": 900},
    ("F7", "15"):  {"morning": 2600, "afternoon": 1500, "evening": 2400, "night": 550},
    ("F8", "4"):   {"morning": 2800, "afternoon": 1600, "evening": 2600, "night": 600},
}

# Time period labels for display
TIME_PERIODS = ["morning", "afternoon", "evening", "night"]
TIME_PERIOD_LABELS = {
    "morning":   "Morning Peak (7-10 AM)",
    "afternoon": "Afternoon (12-3 PM)",
    "evening":   "Evening Peak (5-8 PM)",
    "night":     "Night (10 PM-5 AM)",
}

# =============================================================================
# Public Transportation: Metro Lines
# =============================================================================
METRO_LINES = {
    "M1": {"name": "Line 1 (Helwan-New El-Marg)", "stations": ["12", "1", "3", "F2", "11"], "daily_passengers": 1500000},
    "M2": {"name": "Line 2 (Shubra-Giza)",        "stations": ["11", "F2", "3", "10", "8"], "daily_passengers": 1200000},
    "M3": {"name": "Line 3 (Airport-Imbaba)",      "stations": ["F1", "5", "2", "3", "9"],  "daily_passengers": 800000},
}

# =============================================================================
# Public Transportation: Bus Routes
# =============================================================================
BUS_ROUTES = {
    "B1":  {"stops": ["1", "3", "6", "9"],         "buses": 25, "daily_passengers": 35000},
    "B2":  {"stops": ["7", "15", "8", "10", "3"],   "buses": 30, "daily_passengers": 42000},
    "B3":  {"stops": ["2", "5", "F1"],              "buses": 20, "daily_passengers": 28000},
    "B4":  {"stops": ["4", "14", "2", "3"],         "buses": 22, "daily_passengers": 31000},
    "B5":  {"stops": ["8", "12", "1"],              "buses": 18, "daily_passengers": 25000},
    "B6":  {"stops": ["11", "5", "2"],              "buses": 24, "daily_passengers": 33000},
    "B7":  {"stops": ["13", "4", "14"],             "buses": 15, "daily_passengers": 21000},
    "B8":  {"stops": ["F7", "15", "7"],             "buses": 12, "daily_passengers": 17000},
    "B9":  {"stops": ["1", "8", "10", "9", "6"],    "buses": 28, "daily_passengers": 39000},
    "B10": {"stops": ["F8", "4", "2", "5"],         "buses": 20, "daily_passengers": 28000},
}

TOTAL_BUSES = sum(r["buses"] for r in BUS_ROUTES.values())

# =============================================================================
# Public Transportation Demand
# Format: list of {from, to, daily_passengers}
# =============================================================================
TRANSIT_DEMAND = [
    {"from": "3",  "to": "5",  "passengers": 15000},
    {"from": "1",  "to": "3",  "passengers": 12000},
    {"from": "2",  "to": "3",  "passengers": 18000},
    {"from": "F2", "to": "11", "passengers": 25000},
    {"from": "F1", "to": "3",  "passengers": 20000},
    {"from": "7",  "to": "3",  "passengers": 14000},
    {"from": "4",  "to": "3",  "passengers": 16000},
    {"from": "8",  "to": "3",  "passengers": 22000},
    {"from": "3",  "to": "9",  "passengers": 13000},
    {"from": "5",  "to": "2",  "passengers": 17000},
    {"from": "11", "to": "3",  "passengers": 24000},
    {"from": "12", "to": "3",  "passengers": 11000},
    {"from": "1",  "to": "8",  "passengers": 9000},
    {"from": "7",  "to": "F7", "passengers": 18000},
    {"from": "4",  "to": "F8", "passengers": 12000},
    {"from": "13", "to": "3",  "passengers": 8000},
    {"from": "14", "to": "4",  "passengers": 7000},
]

# =============================================================================
# Helper: Road capacity lookup for traffic analysis
# =============================================================================
def get_road_capacity(from_id, to_id):
    """Get road capacity for a given road segment."""
    for road in EXISTING_ROADS:
        if (road["from"] == from_id and road["to"] == to_id) or \
           (road["from"] == to_id and road["to"] == from_id):
            return road["capacity"]
    return None

def get_congestion_ratio(from_id, to_id, time_period="morning"):
    """Get congestion ratio (traffic_flow / capacity) for a road at a given time."""
    capacity = get_road_capacity(from_id, to_id)
    flow_key = (from_id, to_id)
    rev_key = (to_id, from_id)
    flow_data = TRAFFIC_FLOW.get(flow_key) or TRAFFIC_FLOW.get(rev_key)
    if capacity and flow_data:
        return flow_data[time_period] / capacity
    return 0.5  # Default moderate congestion
