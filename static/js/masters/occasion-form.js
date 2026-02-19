// static/js/masters/occasion-form.js

document.addEventListener('DOMContentLoaded', function() {
    
    // Get form elements
    const occasionForm = document.getElementById('occasionForm');
    const nameInput = document.getElementById('name');
    const iconInput = document.getElementById('icon');
    const iconPreviewSection = document.getElementById('iconPreviewSection');
    const iconPreview = document.getElementById('iconPreview');
    const iconPreviewText = document.getElementById('iconPreviewText');

    // ===== Real-time Validation =====
    if (nameInput) {
        nameInput.addEventListener('blur', function() {
            validateName(this);
        });
    }

    // ===== Icon Preview =====
    if (iconInput && iconPreviewSection && iconPreview && iconPreviewText) {
        // Show preview if icon exists on page load
        if (iconInput.value.trim()) {
            updateIconPreview(iconInput.value.trim());
        }
        
        iconInput.addEventListener('input', function() {
            const iconClass = this.value.trim();
            if (iconClass) {
                updateIconPreview(iconClass);
            } else {
                iconPreviewSection.style.display = 'none';
            }
        });
    }

    // ===== Preview Modal =====
    const previewBtn = document.getElementById('previewBtn');
    if (previewBtn) {
        previewBtn.addEventListener('click', function() {
            updatePreview();
            const previewModal = new bootstrap.Modal(document.getElementById('previewModal'));
            previewModal.show();
        });
    }

    // ===== Reset Button =====
    const resetBtn = document.getElementById('resetBtn');
    if (resetBtn) {
        resetBtn.addEventListener('click', function(e) {
            e.preventDefault();
            
            Swal.fire({
                icon: 'question',
                title: 'Reset Form',
                text: 'Are you sure you want to reset all fields?',
                showCancelButton: true,
                confirmButtonText: 'Yes, reset',
                cancelButtonText: 'Cancel',
                confirmButtonColor: '#8c0d4f',
                cancelButtonColor: '#6c757d'
            }).then((result) => {
                if (result.isConfirmed) {
                    occasionForm.reset();
                    if (iconPreviewSection) {
                        iconPreviewSection.style.display = 'none';
                    }
                    // Clear validation states
                    document.querySelectorAll('.form-control').forEach(input => {
                        input.classList.remove('is-invalid');
                    });
                }
            });
        });
    }

    // ===== Form Submission =====
    if (occasionForm) {
        occasionForm.addEventListener('submit', function(e) {
            if (!validateForm()) {
                e.preventDefault();
            }
        });
    }

    // ===== Helper Functions =====

    function validateName(field) {
        const value = field.value.trim();
        let isValid = true;
        let errorMessage = '';

        if (!value) {
            errorMessage = 'Occasion name is required';
            isValid = false;
        } else if (value.length < 3) {
            errorMessage = 'Occasion name must be at least 3 characters';
            isValid = false;
        }

        if (!isValid) {
            showFieldError(field, errorMessage);
        } else {
            clearFieldError(field);
        }

        return isValid;
    }

    function showFieldError(field, message) {
        field.classList.add('is-invalid');
        const errorDiv = document.getElementById(field.id + 'Error');
        if (errorDiv) {
            errorDiv.textContent = message;
        }
    }

    function clearFieldError(field) {
        field.classList.remove('is-invalid');
        const errorDiv = document.getElementById(field.id + 'Error');
        if (errorDiv) {
            errorDiv.textContent = '';
        }
    }

    function updateIconPreview(iconClass) {
        if (iconClass.startsWith('bi-')) {
            iconPreview.className = `bi ${iconClass}`;
        } else {
            iconPreview.className = `bi bi-${iconClass}`;
        }
        iconPreviewText.textContent = iconClass;
        iconPreviewSection.style.display = 'block';
    }

    function validateForm() {
        const name = nameInput ? nameInput.value.trim() : '';
        
        let isValid = true;
        let errorMessage = '';

        if (!name) {
            errorMessage = 'Occasion name is required';
            isValid = false;
        } else if (name.length < 3) {
            errorMessage = 'Occasion name must be at least 3 characters';
            isValid = false;
        }

        if (!isValid) {
            Swal.fire({
                icon: 'error',
                title: 'Validation Error',
                text: errorMessage,
                confirmButtonColor: '#8c0d4f'
            });
            
            if (nameInput) {
                showFieldError(nameInput, errorMessage);
            }
        }

        return isValid;
    }

    function updatePreview() {
        const name = nameInput ? nameInput.value.trim() : '-';
        const icon = iconInput ? iconInput.value.trim() : '';
        
        // Generate slug from name
        let slug = name.toLowerCase()
            .replace(/[^\w\s-]/g, '')
            .replace(/\s+/g, '-')
            .replace(/--+/g, '-')
            .replace(/^-+|-+$/g, '');
        
        document.getElementById('previewOccasionName').textContent = name;
        document.getElementById('previewSlug').textContent = slug || '-';
        
        // Update icon in preview
        const previewIcon = document.getElementById('previewIconDisplay').querySelector('i');
        if (icon) {
            if (icon.startsWith('bi-')) {
                previewIcon.className = `bi ${icon}`;
            } else {
                previewIcon.className = `bi bi-${icon}`;
            }
        } else {
            previewIcon.className = 'bi bi-calendar-event';
        }
        
        // Update status
        const isActive = document.getElementById('isActive')?.checked || false;
        document.getElementById('previewStatus').textContent = isActive ? 'Active' : 'Inactive';
    }
});