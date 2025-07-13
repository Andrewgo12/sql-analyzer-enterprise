/**
 * HEADER EVENTS MANAGER
 * Maneja todos los eventos del header de manera segura sin inline handlers
 */

class HeaderEventsManager {
    constructor() {
        this.init();
    }

    init() {
        try {
            this.setupEventListeners();
            if (window.Utils) Utils.log('✅ HeaderEventsManager initialized successfully');
        } catch (error) {
            if (window.Utils) Utils.error('❌ HeaderEventsManager initialization failed:', error);
        }
    }

    setupEventListeners() {
        try {
            // Sidebar toggle mobile
            const sidebarToggleMobile = document.getElementById('sidebar-toggle-mobile');
            if (sidebarToggleMobile) {
                sidebarToggleMobile.addEventListener('click', (e) => {
                    try {
                        e.preventDefault();
                        this.toggleSidebar();
                    } catch (error) {
                        if (window.Utils) Utils.error('❌ Sidebar toggle mobile error:', error);
                    }
                });
            }

            // Sidebar toggle desktop
            const sidebarToggleDesktop = document.getElementById('sidebar-toggle-desktop');
            if (sidebarToggleDesktop) {
                sidebarToggleDesktop.addEventListener('click', (e) => {
                    try {
                        e.preventDefault();
                        this.toggleSidebarCollapse();
                    } catch (error) {
                        if (window.Utils) Utils.error('❌ Sidebar toggle desktop error:', error);
                    }
                });
            }

            // Nav brand link
            const navBrandLink = document.getElementById('nav-brand-link');
            if (navBrandLink) {
                navBrandLink.addEventListener('click', (e) => {
                    try {
                        e.preventDefault();
                        this.navigateToView('dashboard');
                    } catch (error) {
                        if (window.Utils) Utils.error('❌ Nav brand link error:', error);
                    }
                });
            }

            // User avatar
            const userAvatar = document.getElementById('user-avatar');
            if (userAvatar) {
                userAvatar.addEventListener('click', (e) => {
                    try {
                        e.preventDefault();
                        this.toggleUserMenu();
                    } catch (error) {
                        if (window.Utils) Utils.error('❌ User avatar click error:', error);
                    }
                });
            }

            // Profile link
            const profileLink = document.getElementById('profile-link');
            if (profileLink) {
                profileLink.addEventListener('click', (e) => {
                    try {
                        e.preventDefault();
                        this.navigateToView('profile');
                    } catch (error) {
                        if (window.Utils) Utils.error('❌ Profile link error:', error);
                    }
                });
            }

            // Settings link
            const settingsLink = document.getElementById('settings-link');
            if (settingsLink) {
                settingsLink.addEventListener('click', (e) => {
                    try {
                        e.preventDefault();
                        this.navigateToView('settings');
                    } catch (error) {
                        if (window.Utils) Utils.error('❌ Settings link error:', error);
                    }
                });
            }

            // Sign out link
            const signoutLink = document.getElementById('signout-link');
            if (signoutLink) {
                signoutLink.addEventListener('click', (e) => {
                    try {
                        e.preventDefault();
                        this.signOut();
                    } catch (error) {
                        if (window.Utils) Utils.error('❌ Sign out link error:', error);
                    }
                });
            }

            // Sidebar backdrop
            const sidebarBackdrop = document.getElementById('sidebar-backdrop');
            if (sidebarBackdrop) {
                sidebarBackdrop.addEventListener('click', (e) => {
                    try {
                        e.preventDefault();
                        this.closeSidebar();
                    } catch (error) {
                        if (window.Utils) Utils.error('❌ Sidebar backdrop click error:', error);
                    }
                });
            }

            if (window.Utils) Utils.log('✅ Header event listeners setup successfully');
        } catch (error) {
            if (window.Utils) Utils.error('❌ setupEventListeners failed:', error);
        }
    }

    toggleSidebar() {
        try {
            if (typeof toggleSidebar === 'function') {
                toggleSidebar();
            } else if (window.navigationManager && window.navigationManager.toggleSidebar) {
                window.navigationManager.toggleSidebar();
            } else {
                if (window.Utils) Utils.warn('⚠️ toggleSidebar function not available');
            }
        } catch (error) {
            if (window.Utils) Utils.error('❌ toggleSidebar error:', error);
        }
    }

    toggleSidebarCollapse() {
        try {
            if (typeof toggleSidebarCollapse === 'function') {
                toggleSidebarCollapse();
            } else if (window.navigationManager && window.navigationManager.toggleSidebarCollapse) {
                window.navigationManager.toggleSidebarCollapse();
            } else {
                if (window.Utils) Utils.warn('⚠️ toggleSidebarCollapse function not available');
            }
        } catch (error) {
            if (window.Utils) Utils.error('❌ toggleSidebarCollapse error:', error);
        }
    }

    navigateToView(view) {
        try {
            if (window.navigationManager && window.navigationManager.navigateTo) {
                window.navigationManager.navigateTo(view);
            } else if (typeof navigateToView === 'function') {
                navigateToView(view);
            } else {
                if (window.Utils) Utils.warn('⚠️ Navigation function not available, using fallback');
                // Fallback navigation
                window.location.hash = view;
            }
        } catch (error) {
            if (window.Utils) Utils.error('❌ navigateToView error:', error);
        }
    }

    toggleUserMenu() {
        try {
            const userDropdown = document.getElementById('user-dropdown');
            if (userDropdown) {
                userDropdown.classList.toggle('show');
            }

            if (typeof toggleUserMenu === 'function') {
                toggleUserMenu();
            } else {
                if (window.Utils) Utils.warn('⚠️ toggleUserMenu function not available, using basic toggle');
            }
        } catch (error) {
            if (window.Utils) Utils.error('❌ toggleUserMenu error:', error);
        }
    }

    closeSidebar() {
        try {
            if (typeof closeSidebar === 'function') {
                closeSidebar();
            } else if (window.navigationManager && window.navigationManager.closeSidebar) {
                window.navigationManager.closeSidebar();
            } else {
                if (window.Utils) Utils.warn('⚠️ closeSidebar function not available, using basic close');
                // Fallback close sidebar
                const sidebar = document.querySelector('.app-sidebar');
                const backdrop = document.getElementById('sidebar-backdrop');
                if (sidebar) {
                    sidebar.classList.remove('show');
                }
                if (backdrop) {
                    backdrop.classList.remove('show');
                }
            }
        } catch (error) {
            if (window.Utils) Utils.error('❌ closeSidebar error:', error);
        }
    }

    signOut() {
        try {
            if (window.authManager && window.authManager.logout) {
                window.authManager.logout();
            } else if (typeof signOut === 'function') {
                signOut();
            } else {
                if (window.Utils) Utils.warn('⚠️ signOut function not available, using fallback');
                // Fallback sign out
                if (confirm('¿Está seguro de que desea cerrar sesión?')) {
                    window.location.href = '/auth';
                }
            }
        } catch (error) {
            if (window.Utils) Utils.error('❌ signOut error:', error);
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    try {
        window.headerEventsManager = new HeaderEventsManager();
    } catch (error) {
        if (window.Utils) Utils.error('❌ Failed to initialize HeaderEventsManager:', error);
    }
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = HeaderEventsManager;
}
