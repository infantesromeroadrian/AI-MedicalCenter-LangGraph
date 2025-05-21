// Medical AI Assistants - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Show loading spinner on form submission
    const queryForm = document.getElementById('queryForm');
    const loadingSpinner = document.getElementById('loadingSpinner');
    
    if (queryForm && loadingSpinner) {
        queryForm.addEventListener('submit', function() {
            // Show loading spinner
            loadingSpinner.style.display = 'block';
            
            // Disable submit button to prevent multiple submissions
            const submitButton = queryForm.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.innerHTML = '<i class="fas fa-circle-notch fa-spin"></i> Processing...';
            }
        });
    }
    
    // Scroll to latest response if available
    const latestResponse = document.getElementById('latestResponse');
    if (latestResponse) {
        latestResponse.scrollIntoView({ behavior: 'smooth' });
    }
    
    // Automatically expand first item in the FAQ accordion
    const firstAccordionButton = document.querySelector('.accordion-button');
    if (firstAccordionButton && !firstAccordionButton.classList.contains('collapsed')) {
        const collapseElement = document.getElementById(firstAccordionButton.getAttribute('data-bs-target').substring(1));
        if (collapseElement) {
            const accordion = new bootstrap.Collapse(collapseElement, {
                toggle: true
            });
        }
    }
    
    // Add copy to clipboard functionality for medical responses
    const copyButtons = document.querySelectorAll('.copy-response');
    if (copyButtons.length > 0) {
        copyButtons.forEach(button => {
            button.addEventListener('click', function() {
                const responseId = this.getAttribute('data-response-id');
                const responseText = document.getElementById(responseId).innerText;
                
                navigator.clipboard.writeText(responseText).then(() => {
                    // Change button text temporarily
                    const originalText = this.innerHTML;
                    this.innerHTML = '<i class="fas fa-check"></i> Copied!';
                    
                    setTimeout(() => {
                        this.innerHTML = originalText;
                    }, 2000);
                });
            });
        });
    }
    
    // Add print functionality
    const printButtons = document.querySelectorAll('.print-response');
    if (printButtons.length > 0) {
        printButtons.forEach(button => {
            button.addEventListener('click', function() {
                window.print();
            });
        });
    }
    
    // Add emergency alert dismissal
    const emergencyAlerts = document.querySelectorAll('.emergency-alert');
    if (emergencyAlerts.length > 0) {
        emergencyAlerts.forEach(alert => {
            const dismissButton = alert.querySelector('.dismiss-alert');
            if (dismissButton) {
                dismissButton.addEventListener('click', function() {
                    alert.style.display = 'none';
                });
            }
        });
    }
    
    // Enable tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}); 