// static/js/masters/occasion-list.js

document.addEventListener('DOMContentLoaded', function() {
    
    // ===== Delete Occasion Functionality =====
    const deleteButtons = document.querySelectorAll('.delete-btn');
    const deleteModal = document.getElementById('deleteOccasionModal');
    const deleteOccasionName = document.getElementById('deleteOccasionName');
    const deleteOccasionId = document.getElementById('deleteOccasionId');
    
    if (deleteButtons.length > 0 && deleteModal) {
        const modal = new bootstrap.Modal(deleteModal);
        
        deleteButtons.forEach(button => {
            button.addEventListener('click', function() {
                const occasionId = this.dataset.occasionId;
                const occasionName = this.dataset.occasionName;
                
                console.log("Delete clicked - Occasion ID:", occasionId);
                console.log("Delete clicked - Occasion Name:", occasionName);
                
                if (deleteOccasionName) {
                    deleteOccasionName.textContent = occasionName;
                }
                
                if (deleteOccasionId) {
                    deleteOccasionId.value = occasionId;
                    console.log("Hidden input set to:", deleteOccasionId.value);
                }
                
                modal.show();
            });
        });
    }

    // ===== Search and Filter Functionality =====
    const searchInput = document.getElementById('searchOccasion');
    const filterStatus = document.getElementById('filterStatus');
    const resetBtn = document.getElementById('resetFilters');
    const tableBody = document.getElementById('occasionsTableBody');
    const rows = tableBody ? tableBody.getElementsByTagName('tr') : [];

    if (searchInput && filterStatus) {
        
        function filterTable() {
            const searchTerm = searchInput.value.toLowerCase().trim();
            const statusFilter = filterStatus.value;
            
            Array.from(rows).forEach(row => {
                // Skip empty state row
                if (row.querySelector('.empty-state')) return;
                
                const occasionName = row.cells[1]?.textContent.toLowerCase() || '';
                const statusCell = row.cells[4]?.querySelector('.status-badge');
                const status = statusCell ? (statusCell.classList.contains('status-active') ? '1' : '0') : '';
                
                let matchesSearch = true;
                let matchesStatus = true;
                
                // Search filter
                if (searchTerm) {
                    matchesSearch = occasionName.includes(searchTerm);
                }
                
                // Status filter
                if (statusFilter !== '') {
                    matchesStatus = status === statusFilter;
                }
                
                // Show/hide row
                if (matchesSearch && matchesStatus) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        }
        
        // Event listeners
        searchInput.addEventListener('keyup', filterTable);
        filterStatus.addEventListener('change', filterTable);
        
        // Reset filters
        if (resetBtn) {
            resetBtn.addEventListener('click', function() {
                searchInput.value = '';
                filterStatus.value = '';
                filterTable();
            });
        }
    }
});