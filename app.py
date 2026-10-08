"""
Carbon Footprint Calculator - Flask Web Application
---------------------------------------------------
A clean, student-friendly web application for personal carbon accounting.
Calculates emissions across Transportation, Electricity, LPG/Cooking,
Food, Waste, and Water with localized emission factors.
"""

import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from services.calculator import compute_carbon_footprint, load_emission_factors, generate_recommendations
from services.database import (
    init_db,
    save_calculation,
    get_calculation_by_id,
    get_all_calculations,
    delete_calculation,
    delete_all_calculations
)

app = Flask(__name__)
# Secret key for flash messaging and session handling
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'carbon-footprint-secret-key-nature-2026')

# Initialize SQLite database on startup
with app.app_context():
    init_db()


@app.route('/')
def index():
    """Landing page showcasing the value proposition and core calculator pillars."""
    return render_template('index.html')


@app.route('/calculator', methods=['GET', 'POST'])
def calculator():
    """
    Renders the multi-section calculator form on GET.
    Processes user input, calculates emissions, saves to local SQLite,
    and redirects to the result page on POST.
    """
    if request.method == 'POST':
        try:
            # Extract form values into a standard dictionary
            form_data = request.form.to_dict()
            
            # Compute emissions and breakdown
            result_data = compute_carbon_footprint(form_data)
            
            # Save into local SQLite database
            calc_id = save_calculation(result_data)
            
            flash('Your carbon footprint has been calculated and saved locally.', 'success')
            return redirect(url_for('results', calc_id=calc_id))
            
        except Exception as e:
            app.logger.error(f"Error computing carbon footprint: {e}")
            flash('There was an error processing your calculation. Please check your inputs.', 'danger')
            return redirect(url_for('calculator'))
            
    # GET request: load emission factors to display helper notes in the form
    factors = load_emission_factors()
    return render_template('calculator.html', factors=factors)


@app.route('/results/<int:calc_id>')
def results(calc_id):
    """
    Renders the detailed breakdown, Chart.js visualizations,
    and personalized reduction recommendations for a calculation record.
    """
    calc = get_calculation_by_id(calc_id)
    if not calc:
        flash('The requested calculation record was not found.', 'warning')
        return redirect(url_for('history'))
        
    # Generate dynamic contextual recommendations
    categories = {
        'transportation': calc['transportation'],
        'electricity': calc['electricity'],
        'lpg': calc['lpg'],
        'food': calc['food'],
        'waste': calc['waste'],
        'water': calc['water']
    }
    recommendations = generate_recommendations(categories, calc.get('largest_category', 'transportation'))
    
    return render_template('results.html', calc=calc, recommendations=recommendations)


@app.route('/history')
def history():
    """Displays previous personal calculation records in a clean tabular view."""
    calculations = get_all_calculations()
    
    # Calculate simple aggregate metrics if history exists
    total_entries = len(calculations)
    latest_monthly = calculations[0]['total_monthly'] if total_entries > 0 else 0
    avg_monthly = round(sum(c['total_monthly'] for c in calculations) / total_entries, 2) if total_entries > 0 else 0
    
    return render_template(
        'history.html',
        calculations=calculations,
        total_entries=total_entries,
        latest_monthly=latest_monthly,
        avg_monthly=avg_monthly
    )


@app.route('/history/delete/<int:calc_id>', methods=['POST'])
def delete_single_history(calc_id):
    """Deletes a specific calculation record."""
    success = delete_calculation(calc_id)
    if success:
        flash('Calculation record deleted successfully.', 'success')
    else:
        flash('Could not find or delete the specified record.', 'warning')
    return redirect(url_for('history'))


@app.route('/history/delete-all', methods=['POST'])
def delete_all_history():
    """Deletes all calculation history records while preserving the application."""
    count = delete_all_calculations()
    flash(f'All calculation history ({count} records) has been permanently deleted.', 'info')
    return redirect(url_for('history'))


@app.route('/about')
def about():
    """Educational page explaining CO2e, calculation methodology, assumptions, and limitations."""
    factors = load_emission_factors()
    return render_template('about.html', factors=factors)


@app.route('/api/factors')
def get_factors():
    """JSON API endpoint returning current active emission factors."""
    factors = load_emission_factors()
    return jsonify(factors)


# Friendly Error Handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    app.logger.error(f"Internal server error: {e}")
    return render_template('500.html'), 500


if __name__ == '__main__':
    # Running in local desktop environment
    print("=" * 60)
    print("🌿 CarbonTrack - Personal Carbon Footprint Calculator")
    print("Local Server Starting at: http://127.0.0.1:5000")
    print("Database Location: database/carbon_footprint.db")
    print("=" * 60)
    app.run(host='127.0.0.1', port=5000, debug=True)
