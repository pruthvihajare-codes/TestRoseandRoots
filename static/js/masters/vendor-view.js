// static/js/masters/vendor-view.js

document.addEventListener('DOMContentLoaded', function() {
    
    // ===== Delete Vendor Functionality =====
    const deleteButton = document.querySelector('.btn-delete');
    const deleteModal = document.getElementById('deleteVendorModal');
    const deleteVendorName = document.getElementById('deleteVendorName');
    const deleteVendorId = document.getElementById('deleteVendorId');
    
    if (deleteButton && deleteModal) {
        const modal = new bootstrap.Modal(deleteModal);
        
        deleteButton.addEventListener('click', function() {
            const vendorId = this.dataset.vendorId;
            const vendorName = this.dataset.vendorName;
            
            if (deleteVendorName) deleteVendorName.textContent = vendorName;
            if (deleteVendorId) deleteVendorId.value = vendorId;
            
            modal.show();
        });
    }
});