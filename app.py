from flask import Flask, render_template, request, jsonify
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json
import random
import os

app = Flask(__name__)

def generate_sample_data():
    """Load performance data from Excel file or use fallback sample data"""
    
    # For Railway: Excel file won't exist, so use sample data
    # For local: Try to load Excel file first
    excel_path = "performance_data.xlsx"
    
    if not os.path.exists(excel_path):
        print(f"ℹ️  Excel file not found. Using sample data for demonstration.")
        return generate_fallback_sample_data()
    
    try:
        # Read the "at machine reporting" worksheet (Atlanta data)
        df = pd.read_excel(excel_path, sheet_name='at machine reporting')
        
        print(f"✓ Loaded {len(df)} rows from at machine reporting sheet")
        
        # Clean and transform the data
        df_clean = df.dropna(how='all')
        
        # FILTER: Show only last 7 days of data
        if len(df_clean) > 0 and 'Date' in df_clean.columns:
            recent_date = df_clean['Date'].max()
            df_clean = df_clean[df_clean['Date'] >= (recent_date - pd.Timedelta(days=30))]
            print(f"   Filtered to last 7 days (from {recent_date - pd.Timedelta(days=7)} to {recent_date})")
        
        processed_data = []
        
        for idx, row in df_clean.iterrows():
            # Skip rows with missing critical data
            if pd.isna(row['Date']) or pd.isna(row['Line']):
                continue
            
            # Extract operator from Column1
            operator = str(row['Column1']) if pd.notna(row['Column1']) else "Unknown Operator"
            if operator == "nan" or operator == "Unknown Operator":
                continue
            
            operator = operator.strip()
            
            # Get shift (note: column name has trailing space)
            shift = str(row['Shift ']) if pd.notna(row['Shift ']) else "Unknown"
            
            # Get line
            line = f"Line {row['Line']}" if pd.notna(row['Line']) else "Unknown"
            
            # PRODUCTIVITY: Use Time_Percentage
            time_percentage = row['Time_Percentage'] if pd.notna(row['Time_Percentage']) else 0
            if time_percentage > 0 and time_percentage < 2:
                productivity = float(time_percentage * 100)
            else:
                productivity = float(time_percentage)
            productivity = max(0, min(productivity, 120))
            
            # QUALITY: Use Pass_Percentage
            pass_percentage = row['Pass_Percentage'] if pd.notna(row['Pass_Percentage']) else 100
            if pass_percentage > 0 and pass_percentage < 2:
                quality_rate = float(pass_percentage * 100)
            else:
                quality_rate = float(pass_percentage)
            quality_rate = max(0, min(quality_rate, 100))
            
            # SETUP TIME: Use Actual_Setup_Time
            actual_setup = row['Actual_Setup_Time'] if pd.notna(row['Actual_Setup_Time']) else 0
            avg_setup_time = float(actual_setup) if actual_setup > 0 else 3.0
            avg_setup_time = max(0.5, min(avg_setup_time, 30))
            
            # JOBS COMPLETED: Use Screenprint Passes
            passes = row['Screenprint Passes'] if pd.notna(row['Screenprint Passes']) else 0
            jobs_completed = int(passes) if passes > 0 else 1
            
            # DOWNTIME: Calculate from Shift_Minutes - Total_Time
            shift_minutes = row['Shift_Minutes'] if pd.notna(row['Shift_Minutes']) else 480
            total_time = row['Total_Time'] if pd.notna(row['Total_Time']) else 0
            downtime_minutes = max(0, shift_minutes - total_time)
            downtime_minutes = min(downtime_minutes, shift_minutes)
            
            processed_data.append({
                'operator': operator,
                'shift': shift,
                'line': line,
                'productivity': round(productivity, 1),
                'quality_rate': round(quality_rate, 1),
                'avg_setup_time': round(avg_setup_time, 2),
                'jobs_completed': int(jobs_completed),
                'downtime_minutes': int(downtime_minutes),
                'date': pd.to_datetime(row['Date']).strftime('%Y-%m-%d') if pd.notna(row['Date']) else datetime.now().strftime('%Y-%m-%d')
            })
        
        if not processed_data:
            print("ℹ️  No valid operator data found. Using sample data.")
            return generate_fallback_sample_data()
        
        result_df = pd.DataFrame(processed_data)
        
        # Aggregate by operator and shift
        aggregated = result_df.groupby(['operator', 'shift', 'line']).agg({
            'productivity': 'mean',
            'quality_rate': 'mean',
            'avg_setup_time': 'mean',
            'jobs_completed': 'sum',
            'downtime_minutes': 'sum',
            'date': 'first'
        }).reset_index()
        
        # Round to prevent floating point issues
        aggregated['productivity'] = aggregated['productivity'].round(1)
        aggregated['quality_rate'] = aggregated['quality_rate'].round(1)
        aggregated['avg_setup_time'] = aggregated['avg_setup_time'].round(2)
        
        print(f"✓ Processed {len(aggregated)} operator/shift combinations")
        
        return aggregated
        
    except Exception as e:
        print(f"❌ Error reading Excel file: {e}")
        return generate_fallback_sample_data()

def generate_fallback_sample_data():
    """Fallback sample data for demonstration"""
    operators = [
        "Maria Rodriguez", "John Smith", "Carlos Martinez", "Sarah Johnson",
        "David Lee", "Amanda Brown", "Miguel Santos", "Lisa Chen",
        "Robert Taylor", "Jennifer Garcia", "Kevin Wilson", "Diana Lopez"
    ]
    
    shifts = ["1st Shift", "2nd Shift", "3rd Shift"]
    lines = ["Line 1", "Line 2", "Line 3", "Line 4", "Line 5", "Line 6"]
    
    data = []
    for operator in operators:
        shift = random.choice(shifts)
        line = random.choice(lines)
        productivity = random.randint(75, 105)
        quality_rate = random.uniform(92, 100)
        setup_time = random.uniform(2.5, 4.5)
        jobs_completed = random.randint(15, 45)
        downtime_minutes = random.randint(0, 60)
        
        data.append({
            'operator': operator,
            'shift': shift,
            'line': line,
            'productivity': productivity,
            'quality_rate': quality_rate,
            'avg_setup_time': setup_time,
            'jobs_completed': jobs_completed,
            'downtime_minutes': downtime_minutes,
            'date': datetime.now().strftime('%Y-%m-%d')
        })
    
    return pd.DataFrame(data)

def calculate_performance_score(row):
    """Calculate overall performance score based on key metrics"""
    productivity_score = (row['productivity'] / 100) * 40
    quality_score = (row['quality_rate'] / 100) * 30
    setup_score = (3.0 / row['avg_setup_time']) * 20 if row['avg_setup_time'] > 0 else 0
    efficiency_score = (1 - (row['downtime_minutes'] / 480)) * 10
    
    total_score = productivity_score + quality_score + setup_score + efficiency_score
    return round(total_score, 1)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/performance-data')
def get_performance_data():
    """API endpoint to fetch performance data"""
    shift_filter = request.args.get('shift', 'all')
    
    df = generate_sample_data()
    
    # Filter by shift if specified
    if shift_filter != 'all':
        df = df[df['shift'] == shift_filter]
    
    # Calculate performance scores
    df['performance_score'] = df.apply(calculate_performance_score, axis=1)
    
    # Sort by performance score
    df_sorted = df.sort_values('performance_score', ascending=False)
    
    # Identify top and bottom performers
    top_performers = df_sorted.head(5).to_dict('records')
    bottom_performers = df_sorted.tail(5).to_dict('records')
    
    # Calculate shift averages
    shift_avg = df.groupby('shift').agg({
        'productivity': 'mean',
        'quality_rate': 'mean',
        'avg_setup_time': 'mean',
        'performance_score': 'mean'
    }).round(2).to_dict('index')
    
    return jsonify({
        'top_performers': top_performers,
        'bottom_performers': bottom_performers,
        'all_operators': df_sorted.to_dict('records'),
        'shift_averages': shift_avg,
        'plant_average': {
            'productivity': round(df['productivity'].mean(), 1),
            'quality_rate': round(df['quality_rate'].mean(), 1),
            'avg_setup_time': round(df['avg_setup_time'].mean(), 2),
            'performance_score': round(df['performance_score'].mean(), 1)
        }
    })

@app.route('/api/charts')
def get_charts():
    """Generate chart data for visualization"""
    df = generate_sample_data()
    df['performance_score'] = df.apply(calculate_performance_score, axis=1)
    
    # Productivity by operator chart
    fig_productivity = go.Figure(data=[
        go.Bar(
            x=df.sort_values('productivity', ascending=False)['operator'],
            y=df.sort_values('productivity', ascending=False)['productivity'],
            marker_color=['#00C853' if x >= 90 else '#FF6B35' if x < 85 else '#FFA726' 
                          for x in df.sort_values('productivity', ascending=False)['productivity']],
            text=df.sort_values('productivity', ascending=False)['productivity'],
            textposition='auto',
        )
    ])
    fig_productivity.update_layout(
        title='Productivity by Operator (%)',
        xaxis_title='Operator',
        yaxis_title='Productivity %',
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#333333')
    )
    
    # Performance score comparison
    df_sorted = df.sort_values('performance_score', ascending=False)
    fig_performance = go.Figure(data=[
        go.Bar(
            x=df_sorted['operator'],
            y=df_sorted['performance_score'],
            marker_color=['#00C853' if i < 5 else '#FF6B35' if i >= len(df_sorted) - 5 
                          else '#2196F3' for i in range(len(df_sorted))],
            text=df_sorted['performance_score'],
            textposition='auto',
        )
    ])
    fig_performance.update_layout(
        title='Overall Performance Score by Operator',
        xaxis_title='Operator',
        yaxis_title='Performance Score',
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#333333')
    )
    
    return jsonify({
        'productivity_chart': json.loads(fig_productivity.to_json()),
        'performance_chart': json.loads(fig_performance.to_json())
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
