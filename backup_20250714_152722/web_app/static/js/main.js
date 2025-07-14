/**
 * Main JavaScript - Analizador SQL Empresarial
 * Funcionalidad para la página principal y componentes globales
 */

class SQLAnalyzerMain {
    constructor() {
        this.init();
    }
    
    init() {
        if (window.Utils) Utils.log('🚀 Inicializando Analizador SQL Empresarial');
        
        // Configurar animaciones
        this.setupAnimations();
        
        // Configurar smooth scrolling
        this.setupSmoothScrolling();
        
        // Configurar lazy loading
        this.setupLazyLoading();
        
        // Configurar tema
        this.setupTheme();
        
        // Configurar efectos visuales
        this.setupVisualEffects();
        
        // Configurar analytics (si está disponible)
        this.setupAnalytics();
        
        if (window.Utils) Utils.log('✅ Inicialización completada');
    }
    
    /**
     * Configurar animaciones de entrada
     */
    setupAnimations() {
        // Intersection Observer para animaciones al hacer scroll
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        }, observerOptions);
        
        // Observar elementos que necesitan animación
        document.querySelectorAll('.feature-card, .hero-visual, .stat-item').forEach(el => {
            observer.observe(el);
        });
        
        // Animación de typing para el título principal
        this.setupTypingAnimation();
        
        // Animación de contadores
        this.setupCounterAnimations();
    }
    
    /**
     * Configurar animación de typing
     */
    setupTypingAnimation() {
        const titleElement = document.querySelector('.hero-content h1');
        if (!titleElement) return;
        
        const originalText = titleElement.textContent;
        titleElement.textContent = '';
        
        let i = 0;
        const typeWriter = () => {
            if (i < originalText.length) {
                titleElement.textContent += originalText.charAt(i);
                i++;
                setTimeout(typeWriter, 100);
            } else {
                // Agregar cursor parpadeante
                titleElement.innerHTML += '<span class="typing-cursor">|</span>';
                
                // Remover cursor después de 3 segundos
                setTimeout(() => {
                    const cursor = titleElement.querySelector('.typing-cursor');
                    if (cursor) cursor.remove();
                }, 3000);
            }
        };
        
        // Iniciar animación después de un breve delay
        setTimeout(typeWriter, 1000);
    }
    
    /**
     * Configurar animaciones de contadores
     */
    setupCounterAnimations() {
        const counters = document.querySelectorAll('.stat-number');
        
        const animateCounter = (element) => {
            const target = parseInt(element.textContent.replace(/[^\d]/g, ''));
            const duration = 2000; // 2 segundos
            const step = target / (duration / 16); // 60 FPS
            let current = 0;
            
            const timer = setInterval(() => {
                current += step;
                if (current >= target) {
                    current = target;
                    clearInterval(timer);
                }
                
                // Formatear número con comas
                element.textContent = Math.floor(current).toLocaleString();
            }, 16);
        };
        
        // Observer para iniciar animación cuando sea visible
        const counterObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    animateCounter(entry.target);
                    counterObserver.unobserve(entry.target);
                }
            });
        });
        
        counters.forEach(counter => {
            counterObserver.observe(counter);
        });
    }
    
    /**
     * Configurar smooth scrolling
     */
    setupSmoothScrolling() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    const headerOffset = 80; // Altura del navbar fijo
                    const elementPosition = target.getBoundingClientRect().top;
                    const offsetPosition = elementPosition + window.pageYOffset - headerOffset;
                    
                    window.scrollTo({
                        top: offsetPosition,
                        behavior: 'smooth'
                    });
                }
            });
        });
    }
    
    /**
     * Configurar lazy loading para imágenes
     */
    setupLazyLoading() {
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.classList.remove('lazy');
                        imageObserver.unobserve(img);
                    }
                });
            });
            
            document.querySelectorAll('img[data-src]').forEach(img => {
                imageObserver.observe(img);
            });
        }
    }
    
    /**
     * Configurar sistema de temas
     */
    setupTheme() {
        // Detectar preferencia del sistema
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)');
        
        // Aplicar tema inicial
        this.applyTheme(this.getStoredTheme() || (prefersDark.matches ? 'dark' : 'light'));
        
        // Escuchar cambios en preferencia del sistema
        prefersDark.addEventListener('change', (e) => {
            if (!this.getStoredTheme()) {
                this.applyTheme(e.matches ? 'dark' : 'light');
            }
        });
        
        // Configurar toggle de tema si existe
        const themeToggle = document.getElementById('theme-toggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => {
                const currentTheme = document.documentElement.getAttribute('data-theme');
                const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
                this.applyTheme(newTheme);
                this.storeTheme(newTheme);
            });
        }
    }
    
    /**
     * Aplicar tema
     */
    applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        
        // Actualizar meta theme-color
        const metaThemeColor = document.querySelector('meta[name="theme-color"]');
        if (metaThemeColor) {
            metaThemeColor.setAttribute('content', theme === 'dark' ? '#1e293b' : '#2563eb');
        }
    }
    
    /**
     * Obtener tema almacenado
     */
    getStoredTheme() {
        return localStorage.getItem('sql-analyzer-theme');
    }
    
    /**
     * Almacenar tema
     */
    storeTheme(theme) {
        localStorage.setItem('sql-analyzer-theme', theme);
    }
    
    /**
     * Configurar efectos visuales
     */
    setupVisualEffects() {
        // Efecto parallax para el hero
        this.setupParallax();
        
        // Efecto de partículas en el fondo
        this.setupParticles();
        
        // Efecto hover para tarjetas
        this.setupCardHoverEffects();
        
        // Efecto de ondas en botones
        this.setupRippleEffect();
    }
    
    /**
     * Configurar efecto parallax
     */
    setupParallax() {
        const heroSection = document.querySelector('.hero-section');
        if (!heroSection) return;
        
        window.addEventListener('scroll', () => {
            const scrolled = window.pageYOffset;
            const rate = scrolled * -0.5;
            
            heroSection.style.transform = `translateY(${rate}px)`;
        });
    }
    
    /**
     * Configurar partículas de fondo
     */
    setupParticles() {
        const heroSection = document.querySelector('.hero-section');
        if (!heroSection) return;
        
        // Crear canvas para partículas
        const canvas = document.createElement('canvas');
        canvas.style.position = 'absolute';
        canvas.style.top = '0';
        canvas.style.left = '0';
        canvas.style.width = '100%';
        canvas.style.height = '100%';
        canvas.style.pointerEvents = 'none';
        canvas.style.opacity = '0.3';
        
        heroSection.appendChild(canvas);
        
        const ctx = canvas.getContext('2d');
        let particles = [];
        
        // Redimensionar canvas
        const resizeCanvas = () => {
            canvas.width = heroSection.offsetWidth;
            canvas.height = heroSection.offsetHeight;
        };
        
        resizeCanvas();
        window.addEventListener('resize', resizeCanvas);
        
        // Crear partículas
        for (let i = 0; i < 50; i++) {
            particles.push({
                x: Math.random() * canvas.width,
                y: Math.random() * canvas.height,
                vx: (Math.random() - 0.5) * 0.5,
                vy: (Math.random() - 0.5) * 0.5,
                size: Math.random() * 2 + 1
            });
        }
        
        // Animar partículas
        const animateParticles = () => {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            particles.forEach(particle => {
                // Actualizar posición
                particle.x += particle.vx;
                particle.y += particle.vy;
                
                // Rebotar en bordes
                if (particle.x < 0 || particle.x > canvas.width) particle.vx *= -1;
                if (particle.y < 0 || particle.y > canvas.height) particle.vy *= -1;
                
                // Dibujar partícula
                ctx.beginPath();
                ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(255, 255, 255, 0.5)';
                ctx.fill();
            });
            
            requestAnimationFrame(animateParticles);
        };
        
        animateParticles();
    }
    
    /**
     * Configurar efectos hover para tarjetas
     */
    setupCardHoverEffects() {
        document.querySelectorAll('.feature-card').forEach(card => {
            card.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-8px) scale(1.02)';
            });
            
            card.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0) scale(1)';
            });
        });
    }
    
    /**
     * Configurar efecto ripple en botones
     */
    setupRippleEffect() {
        document.querySelectorAll('.btn').forEach(button => {
            button.addEventListener('click', function(e) {
                const ripple = document.createElement('span');
                const rect = this.getBoundingClientRect();
                const size = Math.max(rect.width, rect.height);
                const x = e.clientX - rect.left - size / 2;
                const y = e.clientY - rect.top - size / 2;
                
                ripple.style.cssText = `
                    position: absolute;
                    width: ${size}px;
                    height: ${size}px;
                    left: ${x}px;
                    top: ${y}px;
                    background: rgba(255, 255, 255, 0.3);
                    border-radius: 50%;
                    transform: scale(0);
                    animation: ripple 0.6s linear;
                    pointer-events: none;
                `;
                
                this.style.position = 'relative';
                this.style.overflow = 'hidden';
                this.appendChild(ripple);
                
                setTimeout(() => {
                    ripple.remove();
                }, 600);
            });
        });
        
        // Agregar CSS para animación ripple
        if (!document.getElementById('ripple-styles')) {
            const style = document.createElement('style');
            style.id = 'ripple-styles';
            style.textContent = `
                @keyframes ripple {
                    to {
                        transform: scale(4);
                        opacity: 0;
                    }
                }
            `;
            document.head.appendChild(style);
        }
    }
    
    /**
     * Configurar analytics
     */
    setupAnalytics() {
        // Implementar tracking de eventos si es necesario
        this.trackPageView();
        this.setupEventTracking();
    }
    
    /**
     * Track page view
     */
    trackPageView() {
        if (window.Utils) Utils.log('📊 Page view tracked:', window.location.pathname);
    }
    
    /**
     * Configurar tracking de eventos
     */
    setupEventTracking() {
        // Track clicks en botones principales
        document.querySelectorAll('.btn-primary, .btn-warning').forEach(button => {
            button.addEventListener('click', (e) => {
                const action = e.target.textContent.trim();
                if (window.Utils) Utils.log('📊 Button click tracked:', action);
            });
        });
        
        // Track scroll depth
        let maxScroll = 0;
        window.addEventListener('scroll', () => {
            const scrollPercent = Math.round(
                (window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100
            );
            
            if (scrollPercent > maxScroll) {
                maxScroll = scrollPercent;
                
                // Track milestones
                if ([25, 50, 75, 100].includes(scrollPercent)) {
                    if (window.Utils) Utils.log('📊 Scroll depth tracked:', scrollPercent + '%');
                }
            }
        });
    }
    
    /**
     * Utilidades públicas
     */
    showNotification(message, type = 'info') {
        // Crear notificación toast
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 9999;';
        
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        document.body.appendChild(toast);
        
        // Mostrar toast
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        // Remover elemento después de que se oculte
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }
    
    /**
     * Formatear números
     */
    formatNumber(num) {
        return new Intl.NumberFormat().format(num);
    }
    
    /**
     * Formatear bytes
     */
    formatBytes(bytes, decimals = 2) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    }
}

// Funciones globales
function goToDashboard() {
    window.location.href = '/dashboard';
}

function scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.scrollIntoView({ behavior: 'smooth' });
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    window.sqlAnalyzer = new SQLAnalyzerMain();
    
    // Agregar estilos CSS adicionales
    const additionalStyles = document.createElement('style');
    additionalStyles.textContent = `
        .animate-in {
            animation: fadeInUp 0.8s ease-out forwards;
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .typing-cursor {
            animation: blink 1s infinite;
        }
        
        @keyframes blink {
            0%, 50% { opacity: 1; }
            51%, 100% { opacity: 0; }
        }
        
        .lazy {
            opacity: 0;
            transition: opacity 0.3s;
        }
        
        .lazy.loaded {
            opacity: 1;
        }
    `;
    document.head.appendChild(additionalStyles);
});
