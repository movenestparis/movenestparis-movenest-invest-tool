// Real Estate Calculator JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize loan fields visibility
    toggleLoanFields();
    
    // Add event listeners for loan radio buttons
    const loanRadios = document.querySelectorAll('input[name="use_loan"]');
    loanRadios.forEach(radio => {
        radio.addEventListener('change', toggleLoanFields);
    });
    
    // Add form validation
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', validateForm);
    }
    
    // Add number formatting to inputs
    const numberInputs = document.querySelectorAll('input[type="number"]');
    numberInputs.forEach(input => {
        input.addEventListener('blur', formatNumber);
    });
    
    // Add smooth scrolling to results when calculated
    if (document.querySelector('.results-card')) {
        scrollToResults();
    }
});

function toggleLoanFields() {
    const useLoanYes = document.getElementById('loan_yes');
    const loanFields = document.getElementById('loan-fields');
    
    if (useLoanYes && loanFields) {
        if (useLoanYes.checked) {
            loanFields.style.display = 'block';
            // Make loan fields required
            const loanInputs = loanFields.querySelectorAll('input');
            loanInputs.forEach(input => {
                input.required = true;
            });
        } else {
            loanFields.style.display = 'none';
            // Remove required attribute from loan fields
            const loanInputs = loanFields.querySelectorAll('input');
            loanInputs.forEach(input => {
                input.required = false;
            });
        }
    }
}

function validateForm(event) {
    const form = event.target;
    const propertyPrice = parseFloat(form.property_price.value);
    const monthlyRent = parseFloat(form.monthly_rent.value);
    const resaleValue = parseFloat(form.resale_value.value);
    
    // Basic validation
    if (propertyPrice <= 0) {
        showError('Le prix de la propriété doit être supérieur à 0');
        event.preventDefault();
        return false;
    }
    
    if (monthlyRent <= 0) {
        showError('Le loyer mensuel doit être supérieur à 0');
        event.preventDefault();
        return false;
    }
    
    if (resaleValue <= 0) {
        showError('La valeur de revente doit être supérieure à 0');
        event.preventDefault();
        return false;
    }
    
    // Loan validation
    const useLoan = form.use_loan.value === 'yes';
    if (useLoan) {
        const loanAmount = parseFloat(form.loan_amount.value);
        const interestRate = parseFloat(form.interest_rate.value);
        const loanDuration = parseInt(form.loan_duration.value);
        
        if (loanAmount <= 0) {
            showError('Le montant du prêt doit être supérieur à 0');
            event.preventDefault();
            return false;
        }
        
        if (loanAmount >= propertyPrice) {
            showError('Le montant du prêt ne peut pas être supérieur ou égal au prix de la propriété');
            event.preventDefault();
            return false;
        }
        
        if (interestRate < 0 || interestRate > 20) {
            showError('Le taux d\'intérêt doit être entre 0% et 20%');
            event.preventDefault();
            return false;
        }
        
        if (loanDuration <= 0 || loanDuration > 50) {
            showError('La durée du prêt doit être entre 1 et 50 ans');
            event.preventDefault();
            return false;
        }
    }
    
    // Show loading state
    const submitButton = form.querySelector('button[type="submit"]');
    if (submitButton) {
        submitButton.disabled = true;
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Calcul en cours...';
    }
    
    return true;
}

function showError(message) {
    // Remove existing error alerts
    const existingAlerts = document.querySelectorAll('.alert-danger');
    existingAlerts.forEach(alert => alert.remove());
    
    // Create new error alert
    const alert = document.createElement('div');
    alert.className = 'alert alert-danger';
    alert.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${message}`;
    
    // Insert at the top of the form
    const form = document.querySelector('form');
    if (form) {
        form.insertBefore(alert, form.firstChild);
    }
    
    // Scroll to error
    alert.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function formatNumber(event) {
    const input = event.target;
    const value = parseFloat(input.value);
    
    if (!isNaN(value) && value !== 0) {
        // Add thousand separators for display (optional)
        // input.value = value.toLocaleString('fr-FR');
    }
}

function scrollToResults() {
    const resultsCard = document.querySelector('.results-card');
    if (resultsCard) {
        setTimeout(() => {
            resultsCard.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'start' 
            });
        }, 100);
    }
}

// Add animation to metric cards
function animateMetrics() {
    const metricItems = document.querySelectorAll('.metric-item');
    metricItems.forEach((item, index) => {
        setTimeout(() => {
            item.style.opacity = '0';
            item.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                item.style.transition = 'all 0.5s ease';
                item.style.opacity = '1';
                item.style.transform = 'translateY(0)';
            }, 50);
        }, index * 100);
    });
}

// Call animation if results are present
if (document.querySelector('.results-card')) {
    setTimeout(animateMetrics, 200);
}

// Add keyboard shortcuts
document.addEventListener('keydown', function(event) {
    // Ctrl/Cmd + Enter to submit form
    if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
        const form = document.querySelector('form');
        if (form) {
            form.submit();
        }
    }
    
    // Escape to clear form
    if (event.key === 'Escape') {
        const form = document.querySelector('form');
        if (form && confirm('Voulez-vous vraiment effacer le formulaire?')) {
            form.reset();
            toggleLoanFields();
        }
    }
});

// Add copy to clipboard functionality for results
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        // Show success message
        const toast = document.createElement('div');
        toast.className = 'alert alert-success position-fixed';
        toast.style.top = '20px';
        toast.style.right = '20px';
        toast.style.zIndex = '9999';
        toast.innerHTML = '<i class="fas fa-check"></i> Copié dans le presse-papiers!';
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.remove();
        }, 3000);
    });
}

// Add click handlers to metric values for copying
document.querySelectorAll('.metric-value').forEach(element => {
    element.style.cursor = 'pointer';
    element.title = 'Cliquer pour copier';
    element.addEventListener('click', function() {
        copyToClipboard(this.textContent);
    });
});

// Auto-submit form when scenario changes
document.querySelectorAll('input[name="scenario"]').forEach(radio => {
    radio.addEventListener('change', function() {
        if (document.querySelector('.results-card')) {
            // Only auto-submit if we already have results
            setTimeout(() => {
                document.querySelector('form').submit();
            }, 100);
        }
    });
});
