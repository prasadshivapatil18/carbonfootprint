# 🌿 CarbonTrack — Personal Carbon Footprint Calculator

A clean, modern, realistic, and academic-grade **Personal Carbon Footprint Calculator** built with **Python (Flask)** and **SQLite**. 

Designed for Environmental Studies (EVS) and academic computing projects, CarbonTrack enables individuals and households to audit their greenhouse gas emissions across six essential lifestyle sectors: **Transportation**, **Electricity**, **LPG / Cooking Fuel**, **Food & Diet**, **Household Waste**, and **Water Usage**.

---

## 📸 Key Features

- **Multi-Sector Carbon Accounting**: Computes emissions in standardized **kg CO₂e** per month and projected **tonnes CO₂e** per year.
- **Configurable Emission Factors**: Emission factors are maintained in `data/emission_factors.json` rather than hardcoded in Python logic.
- **Regional & Indian Baselines**: Incorporates realistic parameters from India's Central Electricity Authority (CEA), MoEFCC, ARAI, and IPCC guidelines.
- **Interactive Visualizations**: Clean, responsive Chart.js Doughnut and Bar charts styled in an earthy, nature-inspired palette (Forest Green, Sage, Terracotta, Solar Gold).
- **Personalized Action Recommendations**: Dynamically evaluates the user's largest emission driver and generates practical reduction advice.
- **100% Local SQLite Persistence**: Stores calculation history on your computer. Zero cloud dependencies, zero accounts, and zero remote tracking.
- **Self-Healing Database**: Automatic schema initialization upon startup if the database file is removed or reset.
- **Print & PDF Export Support**: Direct browser-friendly printing for reports.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.10+ / Python 3.13, Flask
- **Database**: SQLite3 (Local file-based, zero configuration)
- **Frontend**: HTML5, CSS3 (Bespoke sustainable design system), JavaScript (ES6)
- **Data Visualization**: Chart.js v4
- **Typography**: Plus Jakarta Sans & Inter (Google Fonts)

---

## 📂 Project Architecture

```text
EVS/
│
├── app.py                      # Main Flask application & routing
├── requirements.txt            # Python dependencies (Flask)
├── README.md                   # Complete documentation & user guide
│
├── database/                   # Local database directory
│   └── carbon_footprint.db     # SQLite database (auto-created on startup)
│
├── data/
│   └── emission_factors.json   # Configurable regional emission factors
│
├── services/
│   ├── __init__.py
│   ├── calculator.py           # Core calculation engine & reduction logic
│   └── database.py             # SQLite helper & auto-initialization
│
├── static/
│   ├── css/
│   │   └── style.css           # Earthy, modern design system
│   └── js/
│       └── script.js           # Chart rendering, count-up animation & UI
│
└── templates/
    ├── base.html               # Base layout with navigation & footer
    ├── index.html              # Landing page (Understand, Measure, Reduce)
    ├── calculator.html         # Multi-section calculation questionnaire
    ├── results.html            # Results dashboard with charts & advice
    ├── history.html            # Stored calculation logs with deletion controls
    ├── about.html              # Educational methodology & factor table
    ├── 404.html                # Friendly 404 handler
    └── 500.html                # Friendly 500 handler
```

---

## 🚀 Installation & Running Locally (Windows / macOS / Linux)

### 1. Clone or Open the Project Folder
Open PowerShell or your command prompt in the project folder:
```powershell
cd "c:\Users\SHIVA PRASAD\Desktop\EVS"
```

### 2. (Optional) Create & Activate a Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Run the Application
```powershell
python app.py
```

### 5. Open in Your Web Browser
Navigate to:
```text
http://127.0.0.1:5000
```

---

## 🔄 Resetting Local Database

The application stores all calculation history locally inside `database/carbon_footprint.db`.

### Method A: From the Web UI
1. Navigate to the **History** tab in the top navigation bar.
2. Click the red **Delete All Local Data** button.
3. Confirm the dialog. All records will be wiped immediately.

### Method B: Manual File Deletion
1. Stop the Flask application in your terminal (`Ctrl + C`).
2. Navigate to the `database/` folder on your desktop.
3. Delete `carbon_footprint.db`.
4. Restart the application with `python app.py`.

> 💡 **Auto-Initialization**: When restarted, CarbonTrack detects the missing database, automatically creates a new database file, executes table schema creation, and boots cleanly without errors.

---

## 📊 Calculation Methodology & Formulas

The standard emission calculation follows the formula:
$$\text{Emissions (kg CO}_2\text{e)} = \text{Activity Data} \times \text{Emission Factor}$$

### Emission Factor Summary (Default `data/emission_factors.json`)

| Activity Sector | Category | Default Emission Factor | Source Reference |
| :--- | :--- | :--- | :--- |
| **Transportation** | Petrol Car | `0.192` kg CO₂e / km | IPCC / ARAI Baseline |
| | Diesel Car | `0.171` kg CO₂e / km | IPCC / ARAI Baseline |
| | Motorcycle / Scooter | `0.103` kg CO₂e / km | ARAI Two-Wheeler Average |
| | Electric Vehicle (EV) | `0.053` kg CO₂e / km | Grid Intensity + 0.15 kWh/km |
| | City Bus | `0.045` kg CO₂e / pass-km | Public Transit Efficiency |
| | Train / Metro | `0.032` kg CO₂e / pass-km | Urban Mass Transit Baseline |
| **Electricity** | Grid Electricity | `0.710` kg CO₂e / kWh | Central Electricity Authority (CEA) India |
| **LPG / Cooking** | Domestic LPG | `2.980` kg CO₂e / kg | Ministry of Petroleum / IPCC |
| **Waste** | Solid Waste | `0.580` kg CO₂e / kg | CPCB Municipal Solid Waste |
| **Water** | Municipal Supply | `0.00035` kg CO₂e / L | Pumping & Treatment Energy Factor |

---

## 🔒 Privacy & Local Security

- **No Remote Calls**: The calculation engine runs entirely offline on Python.
- **Zero Account Friction**: No passwords, emails, names, or phone numbers are ever requested.
- **Parameterized SQL**: All SQLite database queries use parameterized placeholders (`?`) to prevent SQL injection vulnerabilities.

---

## 🎓 Academic Presentation Tips

If presenting this project for an academic submission or college seminar:
1. Highlight how **separation of concerns** is achieved between `services/calculator.py` and the Flask routing layer.
2. Demonstrate modifying an emission factor in `data/emission_factors.json` without modifying any Python code.
3. Walk through the interactive **Chart.js** charts and the **History cleanup** lifecycle.
