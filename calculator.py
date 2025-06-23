import numpy as np
import logging

try:
    import numpy_financial as npf
    has_npf = True
except ImportError:
    has_npf = False

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
        
    # ... (all your methods unchanged) ...
    
    def calculate_irr(self):
        """Calculate Internal Rate of Return for 10 years"""
        try:
            cash_flows = []
            
            initial_investment = self.calculate_total_investment()
            cash_flows.append(-initial_investment)
            
            for year in range(1, 11):
                annual_cash_flow = self.calculate_annual_net_income(year)
                
                if year == 10:
                    net_resale_value = self.resale_value
                    if self.use_loan:
                        remaining_principal = self.calculate_remaining_principal(year)
                        net_resale_value -= remaining_principal
                    
                    final_cash_flow = annual_cash_flow + net_resale_value
                    cash_flows.append(final_cash_flow)
                else:
                    cash_flows.append(annual_cash_flow)
            
            if has_npf:
                irr = npf.irr(cash_flows)
            else:
                # fallback manual calculation or numpy.irr if exists
                irr = np.irr(cash_flows) if hasattr(np, 'irr') else self._calculate_irr_manual(cash_flows)
            
            return irr * 100 if irr and not np.isnan(irr) else 0
            
        except Exception as e:
            logging.error(f"IRR calculation error: {e}")
            return 0

    # rest of your methods unchanged...
