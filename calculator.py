import numpy as np
import logging

class RealEstateCalculator:
    def __init__(self, property_price, notary_rate, renovation_budget, monthly_rent, 
                 vacancy_months, annual_charges, taxe_fonciere, annual_capex, 
                 resale_value, discount_rate, use_loan=False, loan_amount=0, 
                 interest_rate=0, loan_duration=0, annual_rent_increase=0, 
                 annual_charges_increase=0):
        
        self.property_price = property_price
        self.notary_rate = notary_rate
        self.renovation_budget = renovation_budget
        self.monthly_rent = monthly_rent
        self.vacancy_months = vacancy_months
        self.annual_charges = annual_charges
        self.taxe_fonciere = taxe_fonciere
        self.annual_capex = annual_capex
        self.resale_value = resale_value
        self.discount_rate = discount_rate
        
        self.use_loan = use_loan
        self.loan_amount = loan_amount
        self.interest_rate = interest_rate
        self.loan_duration = loan_duration
        self.annual_rent_increase = annual_rent_increase
        self.annual_charges_increase = annual_charges_increase
        
    def calculate_notary_fees(self):
        """Calculate notary fees"""
        return self.property_price * self.notary_rate
    
    def calculate_total_investment(self):
        """Calculate total initial investment"""
        notary_fees = self.calculate_notary_fees()
        if self.use_loan:
            # Only count the down payment as investment
            down_payment = self.property_price - self.loan_amount
            return down_payment + notary_fees + self.renovation_budget
        else:
            return self.property_price + notary_fees + self.renovation_budget
    
    def calculate_annual_gross_income(self, year=1):
        """Calculate annual gross rental income for a specific year"""
        # Apply rent increase for each year after year 1
        adjusted_rent = self.monthly_rent * ((1 + self.annual_rent_increase) ** (year - 1))
        return adjusted_rent * (12 - self.vacancy_months)
    
    def calculate_annual_net_income(self, year=1):
        """Calculate annual net income after expenses for a specific year"""
        gross_income = self.calculate_annual_gross_income(year)
        
        # Apply charges increase for each year after year 1
        adjusted_charges = self.annual_charges * ((1 + self.annual_charges_increase) ** (year - 1))
        adjusted_taxe_fonciere = self.taxe_fonciere * ((1 + self.annual_charges_increase) ** (year - 1))
        adjusted_capex = self.annual_capex * ((1 + self.annual_charges_increase) ** (year - 1))
        
        total_expenses = adjusted_charges + adjusted_taxe_fonciere + adjusted_capex
        
        # If using loan, subtract annual loan payments (these don't increase)
        if self.use_loan:
            monthly_payment = self.calculate_monthly_loan_payment()
            annual_loan_payment = monthly_payment * 12
            total_expenses += annual_loan_payment
            
        return gross_income - total_expenses
    
    def calculate_monthly_loan_payment(self):
        """Calculate monthly loan payment using PMT formula"""
        if not self.use_loan or self.loan_amount == 0:
            return 0
        
        monthly_rate = self.interest_rate / 12
        num_payments = self.loan_duration * 12
        
        if monthly_rate == 0:
            return self.loan_amount / num_payments
        
        payment = self.loan_amount * (monthly_rate * (1 + monthly_rate) ** num_payments) / \
                 ((1 + monthly_rate) ** num_payments - 1)
        return payment
    
    def calculate_net_yield(self):
        """Calculate net rental yield (based on year 1)"""
        net_income = self.calculate_annual_net_income(1)
        total_investment = self.calculate_total_investment()
        if total_investment == 0:
            return 0
        return (net_income / total_investment) * 100
    
    def calculate_cap_rate(self):
        """Calculate capitalization rate (gross yield, based on year 1)"""
        gross_income = self.calculate_annual_gross_income(1)
        property_value = self.property_price + self.renovation_budget
        if property_value == 0:
            return 0
        return (gross_income / property_value) * 100
    
    def calculate_monthly_cash_flow(self):
        """Calculate monthly cash flow (based on year 1)"""
        annual_net_income = self.calculate_annual_net_income(1)
        return annual_net_income / 12
    
    def calculate_npv(self, years):
        """Calculate Net Present Value for given years"""
        try:
            cash_flows = []
            
            # Initial investment (negative)
            initial_investment = self.calculate_total_investment()
            cash_flows.append(-initial_investment)
            
            # Annual cash flows with escalation
            for year in range(1, years + 1):
                annual_cash_flow = self.calculate_annual_net_income(year)
                
                if year == years:
                    # Add net resale value in final year (resale minus remaining loan)
                    net_resale_value = self.resale_value
                    
                    # If using loan, subtract remaining principal from resale value
                    if self.use_loan:
                        remaining_principal = self.calculate_remaining_principal(year)
                        net_resale_value -= remaining_principal
                        logging.debug(f"Year {year}: Resale {self.resale_value:,.0f} - Remaining loan {remaining_principal:,.0f} = Net {net_resale_value:,.0f}")
                    
                    final_cash_flow = annual_cash_flow + net_resale_value
                    cash_flows.append(final_cash_flow)
                else:
                    cash_flows.append(annual_cash_flow)
            
            # Calculate NPV
            npv = 0
            for i, cash_flow in enumerate(cash_flows):
                npv += cash_flow / ((1 + self.discount_rate) ** i)
            
            return npv
            
        except Exception as e:
            logging.error(f"NPV calculation error: {e}")
            return 0
    
    def calculate_remaining_principal(self, year):
        """Calculate remaining loan principal after given years"""
        if not self.use_loan:
            return 0
        
        monthly_payment = self.calculate_monthly_loan_payment()
        monthly_rate = self.interest_rate / 12
        payments_made = year * 12
        
        if monthly_rate == 0:
            return self.loan_amount - (monthly_payment * payments_made)
        
        remaining = self.loan_amount * ((1 + monthly_rate) ** (self.loan_duration * 12) - 
                                      (1 + monthly_rate) ** payments_made) / \
                   ((1 + monthly_rate) ** (self.loan_duration * 12) - 1)
        
        return max(0, remaining)
    
    def calculate_irr(self):
        """Calculate Internal Rate of Return for 10 years"""
        try:
            cash_flows = []
            
            # Initial investment (negative)
            initial_investment = self.calculate_total_investment()
            cash_flows.append(-initial_investment)
            
            # Annual cash flows for 10 years with escalation
            for year in range(1, 11):
                annual_cash_flow = self.calculate_annual_net_income(year)
                
                if year == 10:
                    # Add net resale value in final year (resale minus remaining loan)
                    net_resale_value = self.resale_value
                    
                    # If using loan, subtract remaining principal from resale value
                    if self.use_loan:
                        remaining_principal = self.calculate_remaining_principal(year)
                        net_resale_value -= remaining_principal
                    
                    final_cash_flow = annual_cash_flow + net_resale_value
                    cash_flows.append(final_cash_flow)
                else:
                    cash_flows.append(annual_cash_flow)
            
            # Calculate IRR using numpy
            irr = np.irr(cash_flows) if hasattr(np, 'irr') else self._calculate_irr_manual(cash_flows)
            return irr * 100 if irr and not np.isnan(irr) else 0
            
        except Exception as e:
            logging.error(f"IRR calculation error: {e}")
            return 0
    
    def _calculate_irr_manual(self, cash_flows):
        """Manual IRR calculation using Newton-Raphson method"""
        try:
            # Initial guess
            rate = 0.1
            
            for _ in range(100):  # Maximum iterations
                npv = sum(cf / (1 + rate) ** i for i, cf in enumerate(cash_flows))
                dnpv = sum(-i * cf / (1 + rate) ** (i + 1) for i, cf in enumerate(cash_flows))
                
                if abs(npv) < 1e-6:
                    return rate
                
                if dnpv == 0:
                    break
                    
                rate = rate - npv / dnpv
                
                if rate < -0.99:  # Prevent negative rates below -99%
                    rate = -0.99
                    
            return rate
            
        except Exception as e:
            logging.error(f"Manual IRR calculation error: {e}")
            return 0
    
    def calculate_dscr(self):
        """Calculate Debt Service Coverage Ratio (based on year 1)"""
        if not self.use_loan:
            return 0
        
        # Use gross income minus operating expenses (not net income which includes debt service)
        gross_income = self.calculate_annual_gross_income(1)
        adjusted_charges = self.annual_charges
        adjusted_taxe_fonciere = self.taxe_fonciere
        adjusted_capex = self.annual_capex
        operating_expenses = adjusted_charges + adjusted_taxe_fonciere + adjusted_capex
        net_operating_income = gross_income - operating_expenses
        
        monthly_payment = self.calculate_monthly_loan_payment()
        annual_debt_payment = monthly_payment * 12
        
        if annual_debt_payment == 0:
            return 0
        
        return net_operating_income / annual_debt_payment
    
    def calculate_breakeven_rent(self):
        """Calculate minimum monthly rent required to reach 0% NPV (10 years)"""
        # Binary search to find the rent that makes NPV = 0
        low_rent = 0
        high_rent = 10000
        tolerance = 1.0  # €1 tolerance
        
        for _ in range(50):  # Maximum iterations
            mid_rent = (low_rent + high_rent) / 2
            
            # Create temporary calculator with new rent
            temp_calc = RealEstateCalculator(
                property_price=self.property_price,
                notary_rate=self.notary_rate,
                renovation_budget=self.renovation_budget,
                monthly_rent=mid_rent,
                vacancy_months=self.vacancy_months,
                annual_charges=self.annual_charges,
                taxe_fonciere=self.taxe_fonciere,
                annual_capex=self.annual_capex,
                resale_value=self.resale_value,
                discount_rate=self.discount_rate,
                use_loan=self.use_loan,
                loan_amount=self.loan_amount,
                interest_rate=self.interest_rate,
                loan_duration=self.loan_duration,
                annual_rent_increase=self.annual_rent_increase,
                annual_charges_increase=self.annual_charges_increase
            )
            
            npv_10 = temp_calc.calculate_npv(10)
            
            if abs(npv_10) < tolerance:
                return mid_rent
            elif npv_10 < 0:
                low_rent = mid_rent
            else:
                high_rent = mid_rent
        
        return (low_rent + high_rent) / 2
    
    def calculate_npv_over_time(self):
        """Calculate NPV for each year from 1 to 10"""
        npv_data = []
        for year in range(1, 11):
            npv = self.calculate_npv(year)
            npv_data.append({'year': year, 'npv': npv})
        return npv_data
    
    def calculate_scenario(self, scenario_type='base'):
        """Calculate metrics for different scenarios"""
        if scenario_type == 'worst':
            # Worst case: +2% tax rate, +1 vacancy month, -10% resale
            temp_calc = RealEstateCalculator(
                property_price=self.property_price,
                notary_rate=self.notary_rate,
                renovation_budget=self.renovation_budget,
                monthly_rent=self.monthly_rent,
                vacancy_months=self.vacancy_months + 1,
                annual_charges=self.annual_charges,
                taxe_fonciere=self.taxe_fonciere * 1.02,
                annual_capex=self.annual_capex,
                resale_value=self.resale_value * 0.9,
                discount_rate=self.discount_rate,
                use_loan=self.use_loan,
                loan_amount=self.loan_amount,
                interest_rate=self.interest_rate,
                loan_duration=self.loan_duration,
                annual_rent_increase=self.annual_rent_increase,
                annual_charges_increase=self.annual_charges_increase
            )
        elif scenario_type == 'best':
            # Best case: -1% tax, -1 vacancy, +10% resale
            temp_calc = RealEstateCalculator(
                property_price=self.property_price,
                notary_rate=self.notary_rate,
                renovation_budget=self.renovation_budget,
                monthly_rent=self.monthly_rent,
                vacancy_months=max(0, self.vacancy_months - 1),
                annual_charges=self.annual_charges,
                taxe_fonciere=self.taxe_fonciere * 0.99,
                annual_capex=self.annual_capex,
                resale_value=self.resale_value * 1.1,
                discount_rate=self.discount_rate,
                use_loan=self.use_loan,
                loan_amount=self.loan_amount,
                interest_rate=self.interest_rate,
                loan_duration=self.loan_duration,
                annual_rent_increase=self.annual_rent_increase,
                annual_charges_increase=self.annual_charges_increase
            )
        else:
            temp_calc = self
        
        return temp_calc.calculate_all_metrics()

    def calculate_all_metrics(self):
        """Calculate all financial metrics"""
        return {
            'notary_fees': self.calculate_notary_fees(),
            'total_investment': self.calculate_total_investment(),
            'annual_gross_income': self.calculate_annual_gross_income(),
            'annual_net_income': self.calculate_annual_net_income(),
            'net_yield': self.calculate_net_yield(),
            'cap_rate': self.calculate_cap_rate(),
            'monthly_cash_flow': self.calculate_monthly_cash_flow(),
            'monthly_loan_payment': self.calculate_monthly_loan_payment() if self.use_loan else 0,
            'npv_3': self.calculate_npv(3),
            'npv_5': self.calculate_npv(5),
            'npv_10': self.calculate_npv(10),
            'irr': self.calculate_irr(),
            'dscr': self.calculate_dscr(),
            'breakeven_rent': self.calculate_breakeven_rent(),
            'npv_over_time': self.calculate_npv_over_time()
        }
    
    def get_interpretations(self, language='fr'):
        """Get CFA-style financial interpretations"""
        results = self.calculate_all_metrics()
        interpretations = []
        
        # Translation dictionaries
        translations = {
            'fr': {
                'good': 'Bon',
                'poor': 'Faible',
                'risky': 'Risqué',
                'excellent': 'Excellent',
                'irr_good': 'TRI supérieur au taux d\'actualisation - Bon rendement',
                'irr_poor': 'TRI inférieur au taux d\'actualisation - Rendement faible',
                'npv_positive': 'VAN positive - Investissement rentable',
                'npv_negative': 'VAN négative - Investissement risqué',
                'yield_good': 'Rendement net > 3% - Bon investissement locatif',
                'yield_poor': 'Rendement net < 3% - Investissement locatif faible',
                'cash_flow_positive': 'Cash-flow positif - Investissement autofinancé',
                'cash_flow_negative': 'Cash-flow négatif - Effort financier mensuel requis',
                'dscr_safe': 'DSCR > 1.2 - Couverture de prêt sécurisée',
                'dscr_risky': 'DSCR < 1.0 - Couverture de prêt risquée'
            },
            'ar': {
                'good': 'جيد',
                'poor': 'ضعيف',
                'risky': 'محفوف بالمخاطر',
                'excellent': 'ممتاز',
                'irr_good': 'معدل العائد الداخلي أعلى من معدل الخصم - عائد جيد',
                'irr_poor': 'معدل العائد الداخلي أقل من معدل الخصم - عائد ضعيف',
                'npv_positive': 'القيمة الحالية الصافية إيجابية - استثمار مربح',
                'npv_negative': 'القيمة الحالية الصافية سالبة - استثمار محفوف بالمخاطر',
                'yield_good': 'العائد الصافي > 3% - استثمار إيجاري جيد',
                'yield_poor': 'العائد الصافي < 3% - استثمار إيجاري ضعيف',
                'cash_flow_positive': 'التدفق النقدي إيجابي - استثمار ممول ذاتياً',
                'cash_flow_negative': 'التدفق النقدي سالب - مطلوب جهد مالي شهري',
                'dscr_safe': 'نسبة تغطية خدمة الدين > 1.2 - تغطية قرض آمنة',
                'dscr_risky': 'نسبة تغطية خدمة الدين < 1.0 - تغطية قرض محفوفة بالمخاطر'
            }
        }
        
        t = translations[language]
        
        # IRR vs Discount Rate
        if results['irr'] > (self.discount_rate * 100):
            interpretations.append(('✅', t['irr_good']))
        else:
            interpretations.append(('❌', t['irr_poor']))
        
        # NPV Analysis
        if results['npv_10'] > 0:
            interpretations.append(('✅', t['npv_positive']))
        else:
            interpretations.append(('❌', t['npv_negative']))
        
        # Net Yield Analysis
        if results['net_yield'] >= 3:
            interpretations.append(('✅', t['yield_good']))
        else:
            interpretations.append(('❌', t['yield_poor']))
        
        # Cash Flow Analysis
        if results['monthly_cash_flow'] >= 0:
            interpretations.append(('✅', t['cash_flow_positive']))
        else:
            interpretations.append(('❌', t['cash_flow_negative']))
        
        # DSCR Analysis (only if using loan)
        if self.use_loan and results['dscr'] > 0:
            if results['dscr'] >= 1.2:
                interpretations.append(('✅', t['dscr_safe']))
            elif results['dscr'] < 1.0:
                interpretations.append(('❌', t['dscr_risky']))
        
        return interpretations
