// static/js/masters/vendor-form.js

document.addEventListener('DOMContentLoaded', function() {
    
    // Get form elements
    const vendorForm = document.getElementById('vendorForm');
    const pincodeSelect = document.getElementById('pincode');
    const areaNameInput = document.getElementById('areaName');

    // ===== Pincode Selection - Auto-fill Area Name =====
    if (pincodeSelect && areaNameInput) {
        pincodeSelect.addEventListener('change', function() {
            const selectedOption = this.options[this.selectedIndex];
            const placeName = selectedOption.getAttribute('data-place');
            
            if (placeName) {
                areaNameInput.value = placeName;
            } else {
                areaNameInput.value = '';
            }
        });

        // Trigger change on page load if pincode is pre-selected (for edit mode)
        if (pincodeSelect.value) {
            pincodeSelect.dispatchEvent(new Event('change'));
        }
    }

    // ===== Phone number validation =====
    const phoneInput = document.getElementById('phoneNo');
    if (phoneInput) {
        phoneInput.addEventListener('input', function() {
            this.value = this.value.replace(/[^0-9]/g, '').slice(0, 10);
        });
    }

    // ===== Preview Functionality =====
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
                    vendorForm.reset();
                    areaNameInput.value = '';
                }
            });
        });
    }

    // ===== Form Submission =====
    if (vendorForm) {
        vendorForm.addEventListener('submit', function(e) {
            if (!validateForm()) {
                e.preventDefault();
            }
        });
    }

    // ===== Helper Functions =====

    function validateForm() {
        const vendorName = document.getElementById('vendorName')?.value.trim();
        const phoneNo = document.getElementById('phoneNo')?.value.trim();
        const pincode = document.getElementById('pincode')?.value;

        let isValid = true;
        let errorMessage = '';

        if (!vendorName) {
            errorMessage = 'Vendor name is required';
            isValid = false;
        } else if (!phoneNo || phoneNo.length !== 10) {
            errorMessage = 'Valid 10-digit phone number is required';
            isValid = false;
        } else if (!pincode) {
            errorMessage = 'Please select a pincode';
            isValid = false;
        }

        if (!isValid) {
            Swal.fire({
                icon: 'error',
                title: 'Validation Error',
                text: errorMessage,
                confirmButtonColor: '#8c0d4f'
            });
        }

        return isValid;
    }

    function updatePreview() {
        const vendorName = document.getElementById('vendorName')?.value || '-';
        const phone = document.getElementById('phoneNo')?.value || '-';
        const email = document.getElementById('email')?.value || '-';
        const area = document.getElementById('areaName')?.value || '-';
        const pincode = document.getElementById('pincode')?.value || '-';
        const address = document.getElementById('vendorAddress')?.value || '-';
        const isActive = document.getElementById('isActive')?.checked || false;
        
        // Get place name from selected option
        const pincodeSelect = document.getElementById('pincode');
        let placeName = area;
        if (pincodeSelect && pincodeSelect.selectedIndex > 0) {
            const selectedOption = pincodeSelect.options[pincodeSelect.selectedIndex];
            placeName = selectedOption.getAttribute('data-place') || area;
        }
        
        // Build full address
        let fullAddress = address;
        if (placeName !== '-') {
            fullAddress = placeName + (address !== '-' ? ', ' + address : '');
        }
        
        document.getElementById('previewVendorName').textContent = vendorName;
        document.getElementById('previewPhone').textContent = phone;
        document.getElementById('previewEmail').textContent = email;
        document.getElementById('previewAddress').textContent = fullAddress;
        document.getElementById('previewPincode').textContent = pincode + (placeName !== '-' ? ' - ' + placeName : '');
        
        const previewStatus = document.getElementById('previewStatus');
        if (previewStatus) {
            previewStatus.textContent = isActive ? 'Active' : 'Inactive';
            previewStatus.style.color = isActive ? '#28a745' : '#dc3545';
        }
    }
});