// Car Rental System - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Date input validation
    const startDateInput = document.querySelector('input[name="start_date"]');
    const endDateInput = document.querySelector('input[name="end_date"]');

    if (startDateInput && endDateInput) {
        // Set min date to today
        const today = new Date().toISOString().split('T')[0];
        startDateInput.min = today;
        endDateInput.min = today;

        // Update end date min when start date changes
        startDateInput.addEventListener('change', function() {
            endDateInput.min = this.value;
            
            // Calculate and display duration if both dates are set
            if (endDateInput.value) {
                calculateDuration();
            }
        });

        endDateInput.addEventListener('change', function() {
            calculateDuration();
        });

        function calculateDuration() {
            if (startDateInput.value && endDateInput.value) {
                const start = new Date(startDateInput.value);
                const end = new Date(endDateInput.value);
                const diffTime = Math.abs(end - start);
                const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
                
                // You can display this somewhere on the page
                console.log('Rental Duration:', diffDays, 'days');
            }
        }
    }

    // Confirm delete actions
    const deleteForms = document.querySelectorAll('form[action*="delete"]');
    deleteForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!confirm('Are you sure you want to delete this item?')) {
                e.preventDefault();
            }
        });
    });

    // Image preview for file upload
    const imageInput = document.querySelector('input[type="file"][name="image"]');
    if (imageInput) {
        imageInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    // Create preview if preview container exists
                    const preview = document.getElementById('imagePreview');
                    if (preview) {
                        preview.src = e.target.result;
                        preview.style.display = 'block';
                    }
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // Smooth scroll to top button
    const scrollBtn = document.getElementById('scrollTopBtn');
    if (scrollBtn) {
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 300) {
                scrollBtn.style.display = 'block';
            } else {
                scrollBtn.style.display = 'none';
            }
        });

        scrollBtn.addEventListener('click', function() {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    // Search form validation
    const searchForm = document.querySelector('form[action*="cars"]');
    if (searchForm) {
        const minPrice = searchForm.querySelector('input[name="min_price"]');
        const maxPrice = searchForm.querySelector('input[name="max_price"]');

        if (minPrice && maxPrice) {
            searchForm.addEventListener('submit', function(e) {
                const min = parseFloat(minPrice.value) || 0;
                const max = parseFloat(maxPrice.value) || Infinity;

                if (min > max) {
                    e.preventDefault();
                    alert('Minimum price cannot be greater than maximum price');
                }
            });
        }
    }

    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
});

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('km-KH', {
        style: 'currency',
        currency: 'KHR',
        minimumFractionDigits: 0
    }).format(amount);
}

// Calculate booking total
function calculateBookingTotal(pricePerDay, days) {
    return pricePerDay * days;
}

// Validate email format
function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Validate phone number (Cambodian format)
function isValidPhoneNumber(phone) {
    // Cambodian phone: +855 12 345 678 or 012345678
    const re = /^(\+855|0)[1-9]\d{7,8}$/;
    return re.test(phone.replace(/\s/g, ''));
}
