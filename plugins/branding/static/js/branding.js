/**
 * Triskele Labs - Dynamic Branding JavaScript
 * Handles runtime logo replacement and text branding
 * Version: 1.1 (Updated with correct logo paths)
 * Date: January 2025
 */

(function() {
    'use strict';

    // Configuration - Updated logo paths for branding plugin
    const CONFIG = {
        companyName: 'Triskele Labs',
        logoPath: '/branding/static/img/triskele_logo.svg',      // Standard SVG
        logoPng: '/branding/static/img/triskele_logo.png',       // PNG fallback
        logoLargePath: '/branding/static/img/triskele_logo_large.svg',  // Large SVG
        poweredBy: 'Powered by Triskele Labs Purple Team Automation',
        copyright: '© 2025 Triskele Labs. All rights reserved.',
        website: 'https://triskelelabs.com'
    };

    /**
     * Replace all MITRE/Caldera logos with Triskele logo
     */
    function replaceLogo() {
        const logoSelectors = [
            'img[src*="caldera"]',
            'img[src*="mitre"]',
            'img[alt*="Caldera"]',
            'img[alt*="MITRE"]',
            '.navbar-brand img',
            '.logo img',
            'header img'
        ];

        logoSelectors.forEach(selector => {
            document.querySelectorAll(selector).forEach(img => {
                if (!img.classList.contains('triskele-branded')) {
                    img.src = CONFIG.logoPath;
                    img.alt = CONFIG.companyName + ' Logo';
                    img.classList.add('triskele-branded');
                    img.style.maxHeight = '40px';
                    img.style.width = 'auto';
                    
                    // Add error handler for fallback
                    img.onerror = function() {
                        this.src = CONFIG.logoPng;
                        console.log('[Triskele Branding] Fell back to PNG logo');
                    };
                    
                    console.log('[Triskele Branding] Logo replaced:', selector);
                }
            });
        });
    }

    /**
     * Replace text mentions of MITRE/Caldera with Triskele Labs
     */
    function replaceText() {
        const replacements = [
            { find: /MITRE Caldera/gi, replace: CONFIG.companyName + ' Purple Team' },
            { find: /Caldera/gi, replace: CONFIG.companyName },
            { find: /MITRE/gi, replace: CONFIG.companyName }
        ];

        // Target common text containers
        const textContainers = document.querySelectorAll(
            'h1, h2, h3, h4, h5, h6, p, span.title, span.header, div.title, .page-title, .header-text'
        );

        textContainers.forEach(element => {
            if (!element.classList.contains('triskele-text-branded')) {
                let changed = false;
                let html = element.innerHTML;
                
                replacements.forEach(r => {
                    if (r.find.test(html)) {
                        html = html.replace(r.find, r.replace);
                        changed = true;
                    }
                });

                if (changed) {
                    element.innerHTML = html;
                    element.classList.add('triskele-text-branded');
                    console.log('[Triskele Branding] Text replaced in:', element.tagName);
                }
            }
        });
    }

    /**
     * Add Triskele Labs footer
     */
    function addFooter() {
        let footer = document.querySelector('footer');
        
        if (!footer) {
            footer = document.createElement('footer');
            footer.className = 'triskele-footer';
            document.body.appendChild(footer);
        }

        if (!footer.classList.contains('triskele-branded-footer')) {
            footer.innerHTML = `
                <div class="footer-content" style="
                    background-color: #000000;
                    color: white;
                    padding: 15px 20px;
                    text-align: center;
                    border-top: none;
                    font-size: 14px;
                ">
                    <p style="margin: 5px 0;">
                        ${CONFIG.copyright}
                    </p>
                </div>
            `;
            footer.classList.add('triskele-branded-footer');
            console.log('[Triskele Branding] Footer added');
        }
    }

    /**
     * Update page title
     */
    function updatePageTitle() {
        if (!document.title.includes(CONFIG.companyName)) {
            document.title = document.title
                .replace(/Caldera/gi, CONFIG.companyName)
                .replace(/MITRE/gi, CONFIG.companyName);
            
            if (!document.title.includes(CONFIG.companyName)) {
                document.title = CONFIG.companyName + ' | ' + document.title;
            }
            console.log('[Triskele Branding] Page title updated:', document.title);
        }
    }

    /**
     * Add favicon (optional - requires favicon file)
     */
    function updateFavicon() {
        let link = document.querySelector("link[rel*='icon']");
        if (!link) {
            link = document.createElement('link');
            link.rel = 'shortcut icon';
            document.head.appendChild(link);
        }
        // Use PNG for favicon compatibility
        link.href = CONFIG.logoPng;
        console.log('[Triskele Branding] Favicon updated');
    }

    /**
     * Main branding function
     */
    function applyBranding() {
        console.log('[Triskele Branding] Applying branding...');
        replaceLogo();
        replaceText();
        updatePageTitle();
        addFooter();
        updateFavicon();
        console.log('[Triskele Branding] Branding applied successfully');
    }

    /**
     * Initialize branding when DOM is ready
     */
    function init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', applyBranding);
        } else {
            applyBranding();
        }

        // Re-apply on dynamic content changes (for SPA/Vue)
        const observer = new MutationObserver((mutations) => {
            let shouldUpdate = false;
            mutations.forEach(mutation => {
                if (mutation.addedNodes.length > 0) {
                    shouldUpdate = true;
                }
            });
            if (shouldUpdate) {
                // Debounce to avoid excessive calls
                clearTimeout(window.triskeleBrandingTimeout);
                window.triskeleBrandingTimeout = setTimeout(() => {
                    replaceLogo();
                    replaceText();
                }, 100);
            }
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });

        console.log('[Triskele Branding] MutationObserver initialized for dynamic content');
    }

    // Start branding
    init();

})();
