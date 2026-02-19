// static/js/masters/vendor-list.js

document.addEventListener('DOMContentLoaded', function() {
    
    // ===== Delete Vendor Functionality =====
    const deleteButtons = document.querySelectorAll('.delete-btn');
    const deleteModal = document.getElementById('deleteVendorModal');
    const deleteVendorName = document.getElementById('deleteVendorName');
    const deleteVendorId = document.getElementById('deleteVendorId');
    
    if (deleteButtons.length > 0 && deleteModal) {
        const modal = new bootstrap.Modal(deleteModal);
        
        deleteButtons.forEach(button => {
            button.addEventListener('click', function() {
                // Get the data attributes from the button
                const vendorId = this.dataset.vendorId;
                const vendorName = this.dataset.vendorName;
                
                console.log("Delete clicked - Vendor ID:", vendorId); // For debugging
                console.log("Delete clicked - Vendor Name:", vendorName); // For debugging
                
                // Set the values in the modal
                if (deleteVendorName) {
                    deleteVendorName.textContent = vendorName;
                }
                
                if (deleteVendorId) {
                    deleteVendorId.value = vendorId;
                    console.log("Hidden input set to:", deleteVendorId.value); // For debugging
                }
                
                // Show the modal
                modal.show();
            });
        });
    }

    // ===== Search and Filter Functionality =====
    const searchInput = document.getElementById('searchVendor');
    const filterArea = document.getElementById('filterArea');
    const filterStatus = document.getElementById('filterStatus');
    const resetBtn = document.getElementById('resetFilters');
    const tableBody = document.getElementById('vendorsTableBody');
    const rows = tableBody ? tableBody.getElementsByTagName('tr') : [];

    if (searchInput && filterArea && filterStatus) {
        
        function filterTable() {
            const searchTerm = searchInput.value.toLowerCase().trim();
            const areaFilter = filterArea.value;
            const statusFilter = filterStatus.value;
            
            let visibleCount = 0;
            
            Array.from(rows).forEach(row => {
                // Skip empty state row
                if (row.querySelector('.empty-state')) return;
                
                const vendorName = row.cells[1]?.textContent.toLowerCase() || '';
                const phone = row.cells[2]?.textContent.toLowerCase() || '';
                const area = row.cells[3]?.textContent || '';
                const pincode = row.cells[4]?.textContent || '';
                const statusCell = row.cells[5]?.querySelector('.status-badge');
                const status = statusCell ? (statusCell.classList.contains('status-active') ? '1' : '0') : '';
                
                let matchesSearch = true;
                let matchesArea = true;
                let matchesStatus = true;
                
                // Search filter
                if (searchTerm) {
                    matchesSearch = vendorName.includes(searchTerm) || 
                                   phone.includes(searchTerm) ||
                                   area.toLowerCase().includes(searchTerm) || 
                                   pincode.includes(searchTerm);
                }
                
                // Area filter
                if (areaFilter) {
                    matchesArea = area === areaFilter;
                }
                
                // Status filter
                if (statusFilter !== '') {
                    matchesStatus = status === statusFilter;
                }
                
                // Show/hide row
                if (matchesSearch && matchesArea && matchesStatus) {
                    row.style.display = '';
                    visibleCount++;
                } else {
                    row.style.display = 'none';
                }
            });
            
            // Update search stats if you have a stats element
            const searchStats = document.getElementById('searchStats');
            const visibleCountSpan = document.getElementById('visibleCount');
            if (searchStats && visibleCountSpan) {
                if (searchTerm || areaFilter || statusFilter) {
                    visibleCountSpan.textContent = visibleCount;
                    searchStats.style.display = 'block';
                } else {
                    searchStats.style.display = 'none';
                }
            }
        }
        
        // Event listeners
        searchInput.addEventListener('keyup', filterTable);
        filterArea.addEventListener('change', filterTable);
        filterStatus.addEventListener('change', filterTable);
        
        // Reset filters
        if (resetBtn) {
            resetBtn.addEventListener('click', function() {
                searchInput.value = '';
                filterArea.value = '';
                filterStatus.value = '';
                filterTable();
            });
        }
    }
});