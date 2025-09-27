// JavaScript for WAHYUDINFLIX2 - Netflix-like experience
document.addEventListener('DOMContentLoaded', function() {
    // Add scroll effect to navbar
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        window.onscroll = function() {
            if (document.body.scrollTop > 50 || document.documentElement.scrollTop > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        };
    }
    
    // Auto-scroll for content rows
    const rowPosters = document.querySelectorAll('.row-posters');
    rowPosters.forEach(row => {
        let isDown = false;
        let startX;
        let scrollLeft;

        row.addEventListener('mousedown', (e) => {
            isDown = true;
            startX = e.pageX - row.offsetLeft;
            scrollLeft = row.scrollLeft;
        });

        row.addEventListener('mouseleave', () => {
            isDown = false;
        });

        row.addEventListener('mouseup', () => {
            isDown = false;
        });

        row.addEventListener('mousemove', (e) => {
            if (!isDown) return;
            e.preventDefault();
            const x = e.pageX - row.offsetLeft;
            const walk = (x - startX) * 2;
            row.scrollLeft = scrollLeft - walk;
        });
    });
    
    // Add loading indicators for player links
    const playerLinks = document.querySelectorAll('[target="_blank"]');
    playerLinks.forEach(link => {
        link.addEventListener('click', function() {
            // Add visual feedback
            const originalHTML = this.innerHTML;
            this.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Loading...';
            this.disabled = true;
            
            // Reset after a short time
            setTimeout(() => {
                this.innerHTML = originalHTML;
                this.disabled = false;
            }, 2000);
        });
    });
    
    // Search functionality
    const searchInput = document.querySelector('input[name="q"]');
    if (searchInput) {
        searchInput.addEventListener('keyup', function(e) {
            if (e.key === 'Enter') {
                const form = this.closest('form');
                if (form) {
                    form.submit();
                }
            }
        });
    }
});

// Function to handle AJAX search (if needed)
function performSearch(query, type = 'all') {
    if (!query.trim()) return;
    
    fetch(`/api/search?q=${encodeURIComponent(query)}&type=${type}`)
        .then(response => response.json())
        .then(data => {
            console.log('Search results:', data);
        })
        .catch(error => {
            console.error('Search error:', error);
        });
}