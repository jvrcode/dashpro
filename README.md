# Performance Dashboard

A web-based performance tracking dashboard.

## 🚀 Live Demo

The dashboard is deployed on Railway and displays sample data for demonstration purposes.

## ✨ Features

- **Real-time KPIs**: Plant-wide productivity, quality, and setup time averages
- **Top/Bottom Performers**: Identify high performers and operators needing support
- **Visual Charts**: Interactive productivity and performance score comparisons
- **Shift Filtering**: View performance by 1st, 2nd, or 3rd shift
- **Detailed Metrics**: Complete operator breakdown with color-coded indicators

## 📊 Performance Metrics

- **Productivity** (Target: 90%) - Time efficiency percentage
- **Quality Rate** (Target: 98%) - Defect-free production
- **Setup Time** (Target: 3 min) - Job changeover speed
- **Performance Score** (Max: 100) - Weighted composite metric

### Score Calculation
- Productivity: 40%
- Quality: 30%
- Setup Time: 20%
- Efficiency: 10%

## 🛠️ Technology Stack

- **Backend**: Flask (Python)
- **Data Processing**: Pandas
- **Visualization**: Plotly.js
- **Deployment**: Railway
- **Frontend**: HTML5, CSS3, JavaScript

## 🏃 Running Locally

### Prerequisites
- Python 3.12+
- pip

### Steps

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd atlanta-dashboard
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the application**
```bash
python app.py
```

4. **Open browser**
```
http://localhost:5000
```

## 📁 Project Structure

```
atlanta-dashboard/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── runtime.txt           # Python version for Railway
├── Procfile              # Railway deployment config
├── .gitignore            # Git ignore rules
├── templates/
│   └── index.html        # Dashboard UI
└── static/
    ├── css/
    │   └── style.css     # Styling
    ├── js/
    │   └── script.js     # Interactivity
    └── logo.png          # Supacolor logo
```

## 🔧 Configuration

### Change Date Range Filter
Edit `app.py` line ~36:
```python
df_clean = df_clean[df_clean['Date'] >= (recent_date - pd.Timedelta(days=7))]
```
Change `days=7` to desired number of days.

### Adjust Performance Targets
Edit thresholds in `static/js/script.js`:
- Productivity target (currently 90%)
- Quality target (currently 98%)
- Setup time target (currently 3 min)

### Modify Score Weights
Edit `calculate_performance_score()` in `app.py`:
```python
productivity_score = (row['productivity'] / 100) * 40  # 40%
quality_score = (row['quality_rate'] / 100) * 30       # 30%
setup_score = (3.0 / row['avg_setup_time']) * 20       # 20%
efficiency_score = (1 - (row['downtime_minutes'] / 480)) * 10  # 10%
```

## 🚢 Deployment on Railway

### Automatic Deployment
1. Connect your GitHub repository to Railway
2. Railway auto-detects Python and uses:
   - `runtime.txt` for Python version
   - `requirements.txt` for dependencies
   - `Procfile` for startup command
3. Push to main branch to trigger deployment

### Environment Variables (Optional)
For future SharePoint integration, add:
- `AZURE_CLIENT_ID`
- `AZURE_CLIENT_SECRET`
- `AZURE_TENANT_ID`

## 📝 Color Coding

### Green (Good Performance)
- Productivity ≥ 90%
- Quality ≥ 98%
- Setup ≤ 3 min

### Orange (Warning)
- Productivity 85-89%
- Quality 95-97%
- Setup 3-3.5 min

### Red (Needs Attention)
- Productivity < 85%
- Quality < 95%
- Setup > 3.5 min

## 🤝 Contributing

For questions or improvements:
- **Plant Manager**: Javier Archila
- **Director of Manufacturing**: Carrie

## 📄 License

© 2025 Supacolor - The World's #1 Heat Transfer Brand

**Mission**: Supafast. Supaeasy. Supacolor.
