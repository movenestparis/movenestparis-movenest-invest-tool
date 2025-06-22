# app.py
import os
import logging
from flask import Flask, render_template, request, session, redirect, url_for, Response
from calculator import RealEstateCalculator
from translations import get_translations
from pdf_generator import generate_pdf_report

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

@app.route('/')
def index():
    # Get current language from session, default to French
    language = session.get('language', 'fr')
    translations = get_translations(language)

    # Get form data from session if available (for language switching)
    form_data = session.get('form_data', {})

    return render_template('index.html', 
                         translations=translations, 
                         language=language,
                         form_data=form_data)

@app.route('/calculate', methods=['POST'])
def calculate():
    # Store form data in session for language switching
    form_data = request.form.to_dict()
    session['form_data'] = form_data

    language = session.get('language', 'fr')
    translations = get_translations(language)
    scenario_type = form_data.get('scenario', 'base')

    try:
        # Parse form data
        property_price = float(form_data.get('property_price', 0))
        notary_rate = float(form_data.get('notary_rate', 0)) / 100
        renovation_budget = float(form_data.get('renovation_budget', 0))
        monthly_rent = float(form_data.get('monthly_rent', 0))
        vacancy_months = float(form_data.get('vacancy_months', 0))
        annual_charges = float(form_data.get('annual_charges', 0))
        taxe_fonciere = float(form_data.get('taxe_fonciere', 0))
        annual_capex = float(form_data.get('annual_capex', 0))
        resale_value = float(form_data.get('resale_value', 0))
        discount_rate = float(form_data.get('discount_rate', 0)) / 100

        annual_rent_increase = float(form_data.get('annual_rent_increase', 0)) / 100
        annual_charges_increase = float(form_data.get('annual_charges_increase', 0)) / 100

        use_loan = form_data.get('use_loan') == 'yes'
        loan_amount = float(form_data.get('loan_amount', 0)) if use_loan else 0
        interest_rate = float(form_data.get('interest_rate', 0)) / 100 if use_loan else 0
        loan_duration = int(form_data.get('loan_duration', 0)) if use_loan else 0

        # Create calculator instance
        calculator = RealEstateCalculator(
            property_price=property_price,
            notary_rate=notary_rate,
            renovation_budget=renovation_budget,
            monthly_rent=monthly_rent,
            vacancy_months=vacancy_months,
            annual_charges=annual_charges,
            taxe_fonciere=taxe_fonciere,
            annual_capex=annual_capex,
            resale_value=resale_value,
            discount_rate=discount_rate,
            use_loan=use_loan,
            loan_amount=loan_amount,
            interest_rate=interest_rate,
            loan_duration=loan_duration,
            annual_rent_increase=annual_rent_increase,
            annual_charges_increase=annual_charges_increase
        )

        # Calculate metrics for selected scenario
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
        error_message = translations['error_invalid_input']
        return render_template('index.html', 
                             translations=translations, 
                             language=language,
                             form_data=form_data,
                             error=error_message)

@app.route('/toggle_language')
def toggle_language():
    current_language = session.get('language', 'fr')
    new_language = 'ar' if current_language == 'fr' else 'fr'
    session['language'] = new_language
    return redirect(url_for('index'))

@app.route('/export_pdf')
def export_pdf():
    form_data = session.get('form_data', {})
    language = session.get('language', 'fr')

    if not form_data:
        return redirect(url_for('index'))

    try:
        # Recreate calculator from form data
        property_price = float(form_data.get('property_price', 0))
        notary_rate = float(form_data.get('notary_rate', 0)) / 100
        renovation_budget = float(form_data.get('renovation_budget', 0))
        monthly_rent = float(form_data.get('monthly_rent', 0))
        vacancy_months = float(form_data.get('vacancy_months', 0))
        annual_charges = float(form_data.get('annual_charges', 0))
        taxe_fonciere = float(form_data.get('taxe_fonciere', 0))
        annual_capex = float(form_data.get('annual_capex', 0))
        resale_value = float(form_data.get('resale_value', 0))
        discount_rate = float(form_data.get('discount_rate', 0)) / 100

        annual_rent_increase = float(form_data.get('annual_rent_increase', 0)) / 100
        annual_charges_increase = float(form_data.get('annual_charges_increase', 0)) / 100

        use_loan = form_data.get('use_loan') == 'yes'
        loan_amount = float(form_data.get('loan_amount', 0)) if use_loan else 0
        interest_rate = float(form_data.get('interest_rate', 0)) / 100 if use_loan else 0
        loan_duration = int(form_data.get('loan_duration', 0)) if use_loan else 0

        calculator = RealEstateCalculator(
            property_price=property_price,
            notary_rate=notary_rate,
            renovation_budget=renovation_budget,
            monthly_rent=monthly_rent,
            vacancy_months=vacancy_months,
            annual_charges=annual_charges,
            taxe_fonciere=taxe_fonciere,
            annual_capex=annual_capex,
            resale_value=resale_value,
            discount_rate=discount_rate,
            use_loan=use_loan,
            loan_amount=loan_amount,
            interest_rate=interest_rate,
            loan_duration=loan_duration,
            annual_rent_increase=annual_rent_increase,
            annual_charges_increase=annual_charges_increase
        )

        results = calculator.calculate_all_metrics()
        interpretations = calculator.get_interpretations(language)

        pdf_data = generate_pdf_report(results, interpretations, form_data, calculator, language)

        response = Response(
            pdf_data,
            mimetype='application/pdf',
            headers={
                'Content-Disposition': 'attachment; filename=movenest_analysis.pdf'
            }
        )
        return response

    except Exception as e:
        logging.error(f"PDF generation error: {e}")
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)