// Link Extractor JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap components
    const toastElList = [].slice.call(document.querySelectorAll('.toast'));
    const toastList = toastElList.map(function(toastEl) {
        return new bootstrap.Toast(toastEl);
    });

    // Form submission handling
    const extractForm = document.getElementById('extractForm');
    const extractBtn = document.getElementById('extractBtn');
    const loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));

    if (extractForm) {
        extractForm.addEventListener('submit', function(e) {
            // Show loading state
            extractBtn.classList.add('loading');
            extractBtn.disabled = true;
            loadingModal.show();
        });
    }

    // Example URL buttons
    const exampleButtons = document.querySelectorAll('.example-url');
    exampleButtons.forEach(button => {
        button.addEventListener('click', function() {
            const url = this.dataset.url;
            const urlInput = document.getElementById('url');
            if (urlInput) {
                urlInput.value = url;
                urlInput.focus();
            }
        });
    });

    // Copy functionality
    function copyToClipboard(text, successCallback) {
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(text).then(function() {
                if (successCallback) successCallback();
            }).catch(function(err) {
                console.error('Failed to copy: ', err);
                fallbackCopyTextToClipboard(text, successCallback);
            });
        } else {
            fallbackCopyTextToClipboard(text, successCallback);
        }
    }

    function fallbackCopyTextToClipboard(text, successCallback) {
        const textArea = document.createElement("textarea");
        textArea.value = text;
        textArea.style.top = "0";
        textArea.style.left = "0";
        textArea.style.position = "fixed";
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();

        try {
            const successful = document.execCommand('copy');
            if (successful && successCallback) {
                successCallback();
            }
        } catch (err) {
            console.error('Fallback: Oops, unable to copy', err);
        }

        document.body.removeChild(textArea);
    }

    function showCopyToast(message = "Copied to clipboard!") {
        const copyToast = document.getElementById('copyToast');
        if (copyToast) {
            const toastBody = copyToast.querySelector('.toast-body');
            toastBody.textContent = message;
            const toast = new bootstrap.Toast(copyToast);
            toast.show();
        }
    }

    // Individual link copy buttons
    const copyLinkButtons = document.querySelectorAll('.copy-link');
    copyLinkButtons.forEach(button => {
        button.addEventListener('click', function() {
            const url = this.dataset.url;
            const originalText = this.innerHTML;
            
            copyToClipboard(url, () => {
                // Visual feedback
                this.innerHTML = '<i class="fas fa-check"></i>';
                this.classList.remove('btn-outline-secondary');
                this.classList.add('btn-success');
                
                setTimeout(() => {
                    this.innerHTML = originalText;
                    this.classList.remove('btn-success');
                    this.classList.add('btn-outline-secondary');
                }, 1000);
                
                showCopyToast('Link copied!');
            });
        });
    });

    // Category copy buttons
    const copyCategoryButtons = document.querySelectorAll('.copy-category');
    copyCategoryButtons.forEach(button => {
        button.addEventListener('click', function() {
            const category = this.dataset.category;
            const categoryLinks = categoriesData[category];
            
            if (categoryLinks && categoryLinks.length > 0) {
                const urls = categoryLinks.map(link => link.url).join('\n');
                const originalText = this.innerHTML;
                
                copyToClipboard(urls, () => {
                    // Visual feedback
                    this.innerHTML = '<i class="fas fa-check me-1"></i>Copied!';
                    this.classList.remove('btn-outline-primary');
                    this.classList.add('btn-success');
                    
                    setTimeout(() => {
                        this.innerHTML = originalText;
                        this.classList.remove('btn-success');
                        this.classList.add('btn-outline-primary');
                    }, 2000);
                    
                    showCopyToast(`${categoryLinks.length} links copied!`);
                });
            }
        });
    });

    // Copy all URLs button
    const copyAllBtn = document.getElementById('copyAllUrls');
    if (copyAllBtn && typeof linksData !== 'undefined') {
        copyAllBtn.addEventListener('click', function() {
            const allUrls = linksData.map(link => link.url).join('\n');
            const originalText = this.innerHTML;
            
            copyToClipboard(allUrls, () => {
                // Visual feedback
                this.innerHTML = '<i class="fas fa-check me-2"></i>Copied!';
                this.classList.remove('btn-secondary');
                this.classList.add('btn-success');
                
                setTimeout(() => {
                    this.innerHTML = originalText;
                    this.classList.remove('btn-success');
                    this.classList.add('btn-secondary');
                }, 2000);
                
                showCopyToast(`All ${linksData.length} links copied!`);
            });
        });
    }

    // Export functionality
    const exportJsonBtn = document.getElementById('exportJson');
    if (exportJsonBtn && typeof linksData !== 'undefined') {
        exportJsonBtn.addEventListener('click', function() {
            const dataStr = JSON.stringify({
                url: window.location.href,
                timestamp: new Date().toISOString(),
                total_count: linksData.length,
                categories: categoriesData,
                links: linksData
            }, null, 2);
            
            const dataBlob = new Blob([dataStr], {type: 'application/json'});
            const url = URL.createObjectURL(dataBlob);
            const link = document.createElement('a');
            link.href = url;
            link.download = 'extracted_links.json';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
            
            showCopyToast('JSON file downloaded!');
        });
    }

    // Export CSV functionality
    const exportCsvBtn = document.getElementById('exportCsv');
    if (exportCsvBtn && typeof linksData !== 'undefined') {
        exportCsvBtn.addEventListener('click', function() {
            const csvHeaders = 'Category,Text,URL,Original Href,Title,Target\n';
            const csvRows = [];
            
            for (const [category, links] of Object.entries(categoriesData)) {
                links.forEach(link => {
                    const row = [
                        `"${category}"`,
                        `"${(link.text || '').replace(/"/g, '""')}"`,
                        `"${link.url}"`,
                        `"${link.original_href}"`,
                        `"${(link.title || '').replace(/"/g, '""')}"`,
                        `"${link.target || ''}"`
                    ].join(',');
                    csvRows.push(row);
                });
            }
            
            const csvContent = csvHeaders + csvRows.join('\n');
            const dataBlob = new Blob([csvContent], {type: 'text/csv'});
            const url = URL.createObjectURL(dataBlob);
            const link = document.createElement('a');
            link.href = url;
            link.download = 'extracted_links.csv';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
            
            showCopyToast('CSV file downloaded!');
        });
    }

    // URL validation
    const urlInput = document.getElementById('url');
    if (urlInput) {
        urlInput.addEventListener('input', function() {
            const value = this.value.trim();
            
            if (value === '') {
                this.classList.remove('is-valid', 'is-invalid');
                return;
            }

            // Basic URL validation
            try {
                // Add protocol if missing
                const urlToTest = value.startsWith('http://') || value.startsWith('https://') 
                    ? value 
                    : 'https://' + value;
                
                const url = new URL(urlToTest);
                this.classList.remove('is-invalid');
                this.classList.add('is-valid');
            } catch {
                this.classList.remove('is-valid');
                this.classList.add('is-invalid');
            }
        });
    }

    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + Enter to submit form
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            if (extractForm && !extractBtn.disabled) {
                extractForm.submit();
            }
        }
        
        // Escape to close modals
        if (e.key === 'Escape') {
            const openModals = document.querySelectorAll('.modal.show');
            openModals.forEach(modal => {
                const modalInstance = bootstrap.Modal.getInstance(modal);
                if (modalInstance) {
                    modalInstance.hide();
                }
            });
        }
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 5000);
    });

    console.log('Link Extractor initialized successfully!');
});
