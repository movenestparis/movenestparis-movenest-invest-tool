import os
import logging
from flask import Flask, render_template, request, session, redirect, url_for, Response
from calculator import RealEstateCalculator
from translations import get_translations
from pdf_generator import generate_pdf_report

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Flask app setup
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

# Credentials from environment variables
USERNAME = os.environ.get('ADMIN_USERNAME', 'movenest')
PASSWORD = os.environ.get('ADMIN_PASSWORD', 'paris2025')

# -------------------------
# ROUTES
# -------------------------

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == USERNAME and password == PASSWORD:
            session['authenticated'] = True
            return redirect(url_for('index'))
        else:
            error = 'Invalid credentials. Please try again.'
    return render_template('login.html', error=error)

@app.before_request
def require_login():
    allowed_routes = ['login', 'static']
    if request.endpoint not in allowed_routes and not session.get('authenticated'):
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
def index():
    language = session.get('language', 'fr')
    translations = get_translations(language)
    form_data = session.get('form_data', {})
    return render_template('index.html',
                           translations=translations,
                           language=language,
                           form_data=form_data)


@app.route('/calculate', methods=['POST'])
def calculate():
    form_data = request.form.to_dict()
    session['form_data'] = form_data

    language = session.get('language', 'fr')
    translations = get_translations(language)
    scenario_type = form_data.get('scenario', 'base')

    try:
        calculator = RealEstateCalculator(
            property_price=float(form_data.get('property_price', 0)),
            notary_rate=float(form_data.get('notary_rate', 0)) / 100,
            renovation_budget=float(form_data.get('renovation_budget', 0)),
            monthly_rent=float(form_data.get('monthly_rent', 0)),
            vacancy_months=float(form_data.get('vacancy_months', 0)),
            annual_charges=float(form_data.get('annual_charges', 0)),
            taxe_fonciere=float(form_data.get('taxe_fonciere', 0)),
            annual_capex=float(form_data.get('annual_capex', 0)),
            resale_value=float(form_data.get('resale_value', 0)),
            discount_rate=float(form_data.get('discount_rate', 0)) / 100,
            use_loan=form_data.get('use_loan') == 'yes',
            loan_amount=float(form_data.get('loan_amount', 0)),
            interest_rate=float(form_data.get('interest_rate', 0)) / 100,
            loan_duration=int(form_data.get('loan_duration', 0)),
            annual_rent_increase=float(form_data.get('annual_rent_increase', 0)) / 100,
            annual_charges_increase=float(form_data.get('annual_charges_increase', 0)) / 100
        )

        if scenario_type in ['best', 'worst']:
            results = calculator.calculate_scenario(scenario_type)
            base_results = calculator.calculate_all_metrics()
        else:
            results = calculator.calculate_all_metrics()
            base_results = results

        interpretations = calculator.get_interpretations(language)

        return render_template('index.html',
                               translations=translations,
                               language=language,
                               form_data=form_data,
                               results=results,
                               base_results=base_results,
                               interpretations=interpretations,
                               show_results=True,
                               scenario_type=scenario_type,
                               calculator=calculator)

    except ValueError as e:
        logging.error(f"Calculation error: {e}")
        return render_template('index.html',
                               translations=translations,
                               language=language,
                               form_data=form_data,
                               error=translations['error_invalid_input'])


@app.route('/toggle_language')
def toggle_language():
    current_language = session.get('language', 'fr')
    session['language'] = 'ar' if current_language == 'fr' else 'fr'
    return redirect(url_for('index'))


@app.route('/export_pdf')
def export_pdf():
    form_data = session.get('form_data', {})
    language = session.get('language', 'fr')

    if not form_data:
        return redirect(url_for('index'))

    try:
        calculator = RealEstateCalculator(
            property_price=float(form_data.get('property_price', 0)),
            notary_rate=float(form_data.get('notary_rate', 0)) / 100,
            renovation_budget=float(form_data.get('renovation_budget', 0)),
            monthly_rent=float(form_data.get('monthly_rent', 0)),
            vacancy_months=float(form_data.get('vacancy_months', 0)),
            annual_charges=float(form_data.get('annual_charges', 0)),
            taxe_fonciere=float(form_data.get('taxe_fonciere', 0)),
            annual_capex=float(form_data.get('annual_capex', 0)),
            resale_value=float(form_data.get('resale_value', 0)),
            discount_rate=float(form_data.get('discount_rate', 0)) / 100,
            use_loan=form_data.get('use_loan') == 'yes',
            loan_amount=float(form_data.get('loan_amount', 0)),
            interest_rate=float(form_data.get('interest_rate', 0)) / 100,
            loan_duration=int(form_data.get('loan_duration', 0)),
            annual_rent_increase=float(form_data.get('annual_rent_increase', 0)) / 100,
            annual_charges_increase=float(form_data.get('annual_charges_increase', 0)) / 100
        )

        results = calculator.calculate_all_metrics()
        interpretations = calculator.get_interpretations(language)
        pdf_data = generate_pdf_report(results, interpretations, form_data, calculator, language)

        return Response(pdf_data,
                        mimetype='application/pdf',
                        headers={'Content-Disposition': 'attachment; filename=movenest_analysis.pdf'})

    except Exception as e:
        logging.error(f"PDF generation error: {e}")
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
