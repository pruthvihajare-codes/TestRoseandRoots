// static/js/masters/occasion-view.js

document.addEventListener('DOMContentLoaded', function() {
    
    // ===== Delete Occasion Functionality =====
    const deleteButton = document.querySelector('.btn-delete');
    const deleteModal = document.getElementById('deleteOccasionModal');
    const deleteOccasionName = document.getElementById('deleteOccasionName');
    const deleteOccasionId = document.getElementById('deleteOccasionId');
    
    if (deleteButton && deleteModal) {
        const modal = new bootstrap.Modal(deleteModal);
        
        deleteButton.addEventListener('click', function() {
            const occasionId = this.dataset.occasionId;
            const occasionName = this.dataset.occasionName;
            
            if (deleteOccasionName) {
                deleteOccasionName.textContent = occasionName;
            }
            
            if (deleteOccasionId) {
                deleteOccasionId.value = occasionId;
            }
            
            modal.show();
        });
    }
});