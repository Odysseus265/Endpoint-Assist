/**
 * Endpoint Assist - IT Help Desk Dashboard
 * Professional JavaScript functionality
 */

// ==================== GLOBAL STATE ====================
let autoRefreshInterval = null;
let currentSection = 'dashboard';
let allSoftware = [];

// ==================== INITIALIZATION ====================
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

function initializeApp() {
    // Update time
    updateTime();
    setInterval(updateTime, 1000);
    
    // Initialize navigation
    initializeNavigation();
    
    // Load initial data
    loadDashboardData();
    
    // Initialize sidebar toggle
    initializeSidebar();
    
    // Initialize ticket filters
    initializeTicketFilters();
    
    // Check for dark mode preference
    if (localStorage.getItem('darkMode') === 'false') {
        document.body.classList.add('light-mode');
        document.getElementById('darkModeToggle').checked = false;
    } else {
        document.getElementById('darkModeToggle').checked = true;
    }
    
    // Check for auto-refresh preference
    if (localStorage.getItem('autoRefresh') === 'true') {
        document.getElementById('autoRefreshToggle').checked = true;
        startAutoRefresh();
    }
    
    console.log('✅ Endpoint Assist initialized successfully');
}

// ==================== TIME & DATE ====================
function updateTime() {
    const now = new Date();
    const options = { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: true 
    };
    document.getElementById('currentTime').textContent = now.toLocaleTimeString('en-US', options);
}

// ==================== NAVIGATION ====================
function initializeNavigation() {
    document.querySelectorAll('.nav-item[data-section]').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const section = item.dataset.section;
            showSection(section);
        });
    });
}

function showSection(sectionId) {
    // Update current section
    currentSection = sectionId;
    
    // Update nav items
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
        if (item.dataset.section === sectionId) {
            item.classList.add('active');
        }
    });
    
    // Update sections
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.remove('active');
    });
    
    const targetSection = document.getElementById(`${sectionId}Section`);
    if (targetSection) {
        targetSection.classList.add('active');
    }
    
    // Update header title
    const titles = {
        dashboard: 'Dashboard',
        system: 'System Health',
        macos: 'macOS Support',
        mobile: 'Mobile Devices',
        security: 'Security Status',
        network: 'Network Diagnostics',
        performance: 'Performance Tools',
        peripherals: 'Peripheral Devices',
        iot: 'IoT & AV Devices',
        inventory: 'Device Inventory',
        procurement: 'IT Procurement',
        tickets: 'Support Tickets',
        knowledge: 'Knowledge Base',
        tools: 'Quick Tools',
        adusers: 'AD User Lookup',
        onboarding: 'New Employee Setup',
        services: 'Windows Services',
        compliance: 'Compliance Check',
        remotetools: 'Remote Tools',
        logs: 'Audit Logs',
        reports: 'Reports',
        experimental: 'Experimental Tools'
    };
    
    document.getElementById('pageTitle').textContent = titles[sectionId] || 'Dashboard';
    
    // Load section-specific data
    loadSectionData(sectionId);
}

function loadSectionData(sectionId) {
    switch (sectionId) {
        case 'dashboard':
            loadDashboardData();
            break;
        case 'system':
            loadSystemHealth();
            loadProcesses();
            break;
        case 'security':
            loadSecurityStatus();
            break;
        case 'network':
            loadNetworkInfo();
            loadWifiStatus();
            break;
        case 'performance':
            loadStartupPrograms();
            break;
        case 'peripherals':
            loadPrinters();
            loadAudioDevices();
            loadCameras();
            loadBluetooth();
            loadUsbDevices();
            break;
        case 'inventory':
            loadInventory();
            break;
        case 'tickets':
            loadTickets();
            break;
        case 'knowledge':
            loadKnowledgeBase();
            break;
        case 'adusers':
            // Ready for user search
            break;
        case 'onboarding':
            loadOnboardingChecklist();
            break;
        case 'services':
            loadServices();
            loadCriticalServices();
            break;
        case 'compliance':
            // Ready for compliance check
            break;
        case 'remotetools':
            // Ready for remote tools
            break;
        case 'logs':
            loadAuditLogs();
            break;
    }
}

// ==================== SIDEBAR ====================
function initializeSidebar() {
    const toggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    
    toggle.addEventListener('click', () => {
        sidebar.classList.toggle('collapsed');
        localStorage.setItem('sidebarCollapsed', sidebar.classList.contains('collapsed'));
    });
    
    // Restore state
    if (localStorage.getItem('sidebarCollapsed') === 'true') {
        sidebar.classList.add('collapsed');
    }
}

// ==================== DASHBOARD ====================
function loadDashboardData() {
    loadSystemHealth();
    loadSecurityStatus();
    loadNetworkInfo();
    loadTickets();
    loadAuditLogs();
}

function refreshAll() {
    showToast('Refreshing', 'Updating dashboard data...', 'info');
    loadSectionData(currentSection);
    setTimeout(() => {
        showToast('Updated', 'Dashboard data refreshed', 'success');
    }, 1000);
}

// ==================== SYSTEM HEALTH ====================
async function loadSystemHealth() {
    try {
        const response = await fetch('/api/system/health');
        const data = await response.json();
        
        if (data.status === 'success') {
            updateSystemStats(data.data);
            updateSystemInfo(data.data);
            updateOsInfo(data.data);
            updateGauges(data.data);
            updateDisksInfo(data.data.disks);
            updateBatteryInfo(data.data.battery);
        }
    } catch (error) {
        console.error('Error loading system health:', error);
    }
}

function updateSystemStats(data) {
    // CPU
    const cpuUsage = data.cpu.usage_percent;
    document.getElementById('cpuUsage').textContent = `${cpuUsage}%`;
    
    // Memory
    const memoryUsage = data.memory.percent;
    document.getElementById('memoryUsage').textContent = `${memoryUsage}%`;
    
    // Disk
    if (data.disks.length > 0) {
        document.getElementById('diskUsage').textContent = `${data.disks[0].percent}%`;
    }
    
    // Update alert count
    let alerts = 0;
    if (cpuUsage > 80) alerts++;
    if (memoryUsage > 80) alerts++;
    if (data.disks.some(d => d.percent > 90)) alerts++;
    
    const alertBadge = document.getElementById('alertCount');
    alertBadge.textContent = alerts;
    if (alerts > 0) {
        alertBadge.classList.add('visible');
    } else {
        alertBadge.classList.remove('visible');
    }
}

function updateSystemInfo(data) {
    const container = document.getElementById('systemInfo');
    container.innerHTML = `
        <div class="info-item">
            <span class="info-label">Hostname</span>
            <span class="info-value">${data.os.hostname}</span>
        </div>
        <div class="info-item">
            <span class="info-label">OS</span>
            <span class="info-value">${data.os.system} ${data.os.release}</span>
        </div>
        <div class="info-item">
            <span class="info-label">CPU Cores</span>
            <span class="info-value">${data.cpu.physical_cores} Physical / ${data.cpu.logical_cores} Logical</span>
        </div>
        <div class="info-item">
            <span class="info-label">Total RAM</span>
            <span class="info-value">${data.memory.total_gb} GB</span>
        </div>
        <div class="info-item">
            <span class="info-label">Boot Time</span>
            <span class="info-value">${new Date(data.os.boot_time).toLocaleString()}</span>
        </div>
    `;
}

function updateOsInfo(data) {
    const container = document.getElementById('osInfo');
    if (!container) return;
    
    container.innerHTML = `
        <div class="os-info-item">
            <i class="fab fa-windows"></i>
            <div>
                <div class="label">Operating System</div>
                <div class="value">${data.os.system} ${data.os.release}</div>
            </div>
        </div>
        <div class="os-info-item">
            <i class="fas fa-code-branch"></i>
            <div>
                <div class="label">Version</div>
                <div class="value">${data.os.version}</div>
            </div>
        </div>
        <div class="os-info-item">
            <i class="fas fa-server"></i>
            <div>
                <div class="label">Hostname</div>
                <div class="value">${data.os.hostname}</div>
            </div>
        </div>
        <div class="os-info-item">
            <i class="fas fa-microchip"></i>
            <div>
                <div class="label">Architecture</div>
                <div class="value">${data.os.machine}</div>
            </div>
        </div>
        <div class="os-info-item">
            <i class="fas fa-clock"></i>
            <div>
                <div class="label">Boot Time</div>
                <div class="value">${new Date(data.os.boot_time).toLocaleString()}</div>
            </div>
        </div>
        <div class="os-info-item">
            <i class="fas fa-bolt"></i>
            <div>
                <div class="label">Processor</div>
                <div class="value">${data.os.processor || 'N/A'}</div>
            </div>
        </div>
    `;
}

function updateGauges(data) {
    // CPU Gauge
    const cpuGauge = document.getElementById('cpuGauge');
    if (cpuGauge) {
        const cpuPercent = data.cpu.usage_percent;
        cpuGauge.style.background = `conic-gradient(var(--primary) ${cpuPercent * 3.6}deg, var(--bg-secondary) 0deg)`;
        cpuGauge.querySelector('.gauge-value').textContent = `${cpuPercent}%`;
    }
    
    // Memory Gauge
    const memoryGauge = document.getElementById('memoryGauge');
    if (memoryGauge) {
        const memPercent = data.memory.percent;
        memoryGauge.style.background = `conic-gradient(var(--success) ${memPercent * 3.6}deg, var(--bg-secondary) 0deg)`;
        memoryGauge.querySelector('.gauge-value').textContent = `${memPercent}%`;
    }
    
    // CPU Details
    const cpuDetails = document.getElementById('cpuDetails');
    if (cpuDetails) {
        cpuDetails.innerHTML = `
            <div class="info-item">
                <span class="info-label">Physical Cores</span>
                <span class="info-value">${data.cpu.physical_cores}</span>
            </div>
            <div class="info-item">
                <span class="info-label">Logical Cores</span>
                <span class="info-value">${data.cpu.logical_cores}</span>
            </div>
            ${data.cpu.frequency ? `
            <div class="info-item">
                <span class="info-label">Frequency</span>
                <span class="info-value">${Math.round(data.cpu.frequency.current)} MHz</span>
            </div>
            ` : ''}
        `;
    }
    
    // Memory Details
    const memoryDetails = document.getElementById('memoryDetails');
    if (memoryDetails) {
        memoryDetails.innerHTML = `
            <div class="info-item">
                <span class="info-label">Total</span>
                <span class="info-value">${data.memory.total_gb} GB</span>
            </div>
            <div class="info-item">
                <span class="info-label">Used</span>
                <span class="info-value">${data.memory.used_gb} GB</span>
            </div>
            <div class="info-item">
                <span class="info-label">Available</span>
                <span class="info-value">${data.memory.available_gb} GB</span>
            </div>
        `;
    }
}

function updateDisksInfo(disks) {
    const container = document.getElementById('disksInfo');
    if (!container) return;
    
    container.innerHTML = disks.map(disk => {
        let barClass = '';
        if (disk.percent > 90) barClass = 'danger';
        else if (disk.percent > 75) barClass = 'warning';
        
        return `
            <div class="disk-item">
                <div class="disk-header">
                    <span class="disk-name"><i class="fas fa-hard-drive"></i> ${disk.device}</span>
                    <span class="disk-space">${disk.free_gb} GB free of ${disk.total_gb} GB</span>
                </div>
                <div class="disk-bar">
                    <div class="disk-bar-fill ${barClass}" style="width: ${disk.percent}%"></div>
                </div>
            </div>
        `;
    }).join('');
}

function updateBatteryInfo(battery) {
    const container = document.getElementById('batteryInfo');
    const card = document.getElementById('batteryCard');
    
    if (!battery) {
        if (card) card.style.display = 'none';
        return;
    }
    
    if (card) card.style.display = 'block';
    if (!container) return;
    
    let iconClass = 'fa-battery-full';
    let colorClass = '';
    
    if (battery.percent < 20) {
        iconClass = 'fa-battery-empty low';
        colorClass = 'low';
    } else if (battery.percent < 50) {
        iconClass = 'fa-battery-half';
    } else if (battery.percent < 80) {
        iconClass = 'fa-battery-three-quarters';
    }
    
    if (battery.power_plugged) {
        colorClass = 'charging';
    }
    
    container.innerHTML = `
        <i class="fas ${iconClass} battery-icon ${colorClass}"></i>
        <span class="battery-percent">${battery.percent}%</span>
        <span class="battery-status">
            ${battery.power_plugged ? '⚡ Plugged In' : `🔋 ${battery.time_left}`}
        </span>
    `;
}

// ==================== PROCESSES ====================
async function loadProcesses() {
    const container = document.getElementById('processesTable');
    if (!container) return;
    
    try {
        const response = await fetch('/api/system/processes');
        const data = await response.json();
        
        if (data.status === 'success') {
            container.innerHTML = `
                <div class="process-header">
                    <span>Name</span>
                    <span>CPU %</span>
                    <span>Memory %</span>
                    <span>Status</span>
                </div>
                ${data.data.slice(0, 15).map(proc => `
                    <div class="process-row">
                        <span class="process-name">${proc.name}</span>
                        <span>${proc.cpu_percent}%</span>
                        <span>${proc.memory_percent}%</span>
                        <span>${proc.status}</span>
                    </div>
                `).join('')}
            `;
        }
    } catch (error) {
        container.innerHTML = '<div class="empty-state"><i class="fas fa-exclamation-circle"></i><span>Failed to load processes</span></div>';
    }
}

// ==================== SECURITY ====================
async function loadSecurityStatus() {
    try {
        const response = await fetch('/api/security/status');
        const data = await response.json();
        
        if (data.status === 'success') {
            updateSecurityOverview(data.data);
            updateSecurityDetails(data.data);
            calculateSecurityScore(data.data);
        }
    } catch (error) {
        console.error('Error loading security status:', error);
    }
}

function updateSecurityOverview(data) {
    const container = document.getElementById('securityOverview');
    if (!container) return;
    
    const defenderOk = data.defender.status === 'Enabled';
    const firewallOk = data.firewall.enabled;
    
    container.innerHTML = `
        <div class="security-item ${defenderOk ? 'good' : 'bad'}">
            <i class="fas ${defenderOk ? 'fa-check-circle' : 'fa-times-circle'}"></i>
            <div class="security-item-info">
                <span class="security-item-title">Windows Defender</span>
                <span class="security-item-status">${data.defender.status}</span>
            </div>
        </div>
        <div class="security-item ${firewallOk ? 'good' : 'bad'}">
            <i class="fas ${firewallOk ? 'fa-check-circle' : 'fa-times-circle'}"></i>
            <div class="security-item-info">
                <span class="security-item-title">Firewall</span>
                <span class="security-item-status">${data.firewall.status}</span>
            </div>
        </div>
        <div class="security-item ${data.defender.real_time ? 'good' : 'warning'}">
            <i class="fas ${data.defender.real_time ? 'fa-shield-halved' : 'fa-exclamation-triangle'}"></i>
            <div class="security-item-info">
                <span class="security-item-title">Real-time Protection</span>
                <span class="security-item-status">${data.defender.real_time ? 'Active' : 'Inactive'}</span>
            </div>
        </div>
    `;
}

function updateSecurityDetails(data) {
    // Defender Status
    const defenderContainer = document.getElementById('defenderStatus');
    if (defenderContainer) {
        const defenderOk = data.defender.status === 'Enabled';
        defenderContainer.innerHTML = `
            <div class="security-item ${defenderOk ? 'good' : 'bad'}">
                <i class="fas ${defenderOk ? 'fa-check-circle' : 'fa-times-circle'}"></i>
                <div class="security-item-info">
                    <span class="security-item-title">Antivirus</span>
                    <span class="security-item-status">${data.defender.status}</span>
                </div>
            </div>
            <div class="security-item ${data.defender.real_time ? 'good' : 'warning'}">
                <i class="fas ${data.defender.real_time ? 'fa-shield-halved' : 'fa-exclamation-triangle'}"></i>
                <div class="security-item-info">
                    <span class="security-item-title">Real-time Protection</span>
                    <span class="security-item-status">${data.defender.real_time ? 'Enabled' : 'Disabled'}</span>
                </div>
            </div>
        `;
    }
    
    // Firewall Status
    const firewallContainer = document.getElementById('firewallStatus');
    if (firewallContainer) {
        const firewallOk = data.firewall.enabled;
        firewallContainer.innerHTML = `
            <div class="security-item ${firewallOk ? 'good' : 'bad'}">
                <i class="fas ${firewallOk ? 'fa-check-circle' : 'fa-times-circle'}"></i>
                <div class="security-item-info">
                    <span class="security-item-title">Firewall Status</span>
                    <span class="security-item-status">${data.firewall.status}</span>
                </div>
            </div>
        `;
    }
    
    // Update Status
    const updateContainer = document.getElementById('updateStatus');
    if (updateContainer) {
        updateContainer.innerHTML = `
            <div class="security-item good">
                <i class="fas fa-download"></i>
                <div class="security-item-info">
                    <span class="security-item-title">Last Update</span>
                    <span class="security-item-status">${data.updates.last_update || 'Unknown'}</span>
                </div>
            </div>
        `;
    }
}

function calculateSecurityScore(data) {
    const container = document.getElementById('securityScore');
    if (!container) return;
    
    let score = 0;
    let maxScore = 100;
    
    // Defender enabled: 30 points
    if (data.defender.status === 'Enabled') score += 30;
    
    // Real-time protection: 25 points
    if (data.defender.real_time) score += 25;
    
    // Firewall enabled: 30 points
    if (data.firewall.enabled) score += 30;
    
    // Recent updates: 15 points
    if (data.updates.last_update && data.updates.last_update !== 'Unknown') score += 15;
    
    let label = 'Poor';
    let color = 'var(--danger)';
    
    if (score >= 80) {
        label = 'Excellent';
        color = 'var(--success)';
    } else if (score >= 60) {
        label = 'Good';
        color = 'var(--info)';
    } else if (score >= 40) {
        label = 'Fair';
        color = 'var(--warning)';
    }
    
    const scoreCircle = container.querySelector('.score-circle');
    if (scoreCircle) {
        scoreCircle.style.background = `conic-gradient(${color} ${score * 3.6}deg, var(--bg-secondary) 0deg)`;
    }
    
    container.querySelector('.score-value').textContent = score;
    container.querySelector('.score-label').textContent = label;
}

// ==================== NETWORK ====================
async function loadNetworkInfo() {
    try {
        const response = await fetch('/api/network/info');
        const data = await response.json();
        
        if (data.status === 'success') {
            updateNetworkInfo(data.data);
            updateNetworkDetails(data.data);
            
            // Update dashboard network status
            const networkStatus = document.getElementById('networkStatus');
            if (networkStatus) {
                networkStatus.textContent = 'Connected';
            }
            const networkIndicator = document.getElementById('networkIndicator');
            if (networkIndicator) {
                networkIndicator.style.background = 'var(--success)';
                networkIndicator.style.boxShadow = '0 0 10px var(--success)';
            }
        }
    } catch (error) {
        console.error('Error loading network info:', error);
        const networkStatus = document.getElementById('networkStatus');
        if (networkStatus) {
            networkStatus.textContent = 'Error';
        }
    }
}

function updateNetworkInfo(data) {
    const container = document.getElementById('networkInfo');
    if (!container) return;
    
    container.innerHTML = `
        <div class="info-item">
            <span class="info-label">Local IP</span>
            <span class="info-value">${data.local_ip}</span>
        </div>
        <div class="info-item">
            <span class="info-label">Public IP</span>
            <span class="info-value">${data.public_ip}</span>
        </div>
        <div class="info-item">
            <span class="info-label">Hostname</span>
            <span class="info-value">${data.hostname}</span>
        </div>
    `;
}

function updateNetworkDetails(data) {
    const container = document.getElementById('networkDetails');
    if (!container) return;
    
    container.innerHTML = `
        <div class="network-item">
            <span class="label"><i class="fas fa-home"></i> Local IP</span>
            <span class="value">${data.local_ip}</span>
        </div>
        <div class="network-item">
            <span class="label"><i class="fas fa-globe"></i> Public IP</span>
            <span class="value">${data.public_ip}</span>
        </div>
        <div class="network-item">
            <span class="label"><i class="fas fa-server"></i> Hostname</span>
            <span class="value">${data.hostname}</span>
        </div>
        <div class="network-item">
            <span class="label"><i class="fas fa-arrow-up"></i> Bytes Sent</span>
            <span class="value">${formatBytes(data.stats.bytes_sent)}</span>
        </div>
        <div class="network-item">
            <span class="label"><i class="fas fa-arrow-down"></i> Bytes Received</span>
            <span class="value">${formatBytes(data.stats.bytes_recv)}</span>
        </div>
    `;
}

async function loadWifiStatus() {
    const container = document.getElementById('wifiStatus');
    if (!container) return;
    
    try {
        const response = await fetch('/api/network/wifi');
        const data = await response.json();
        
        if (data.status === 'success') {
            const wifi = data.data;
            container.innerHTML = `
                <i class="fas fa-wifi wifi-icon ${wifi.connected ? 'connected' : 'disconnected'}"></i>
                <span class="wifi-ssid">${wifi.ssid || 'Not Connected'}</span>
                ${wifi.signal ? `<span class="wifi-signal">Signal: ${wifi.signal}</span>` : ''}
                ${wifi.speed ? `<span class="wifi-signal">Speed: ${wifi.speed}</span>` : ''}
            `;
        }
    } catch (error) {
        container.innerHTML = '<div class="empty-state"><i class="fas fa-wifi"></i><span>Unable to detect WiFi</span></div>';
    }
}

async function runPingTest() {
    const target = document.getElementById('pingTarget').value;
    const container = document.getElementById('pingResults');
    
    container.innerHTML = '<div class="loading-spinner"></div>';
    
    try {
        const response = await fetch(`/api/network/ping?target=${encodeURIComponent(target)}`);
        const data = await response.json();
        
        if (data.status === 'success') {
            const result = data.data;
            container.innerHTML = `
                <div class="${result.reachable ? 'success' : 'error'}">
                    <strong>${result.reachable ? '✓ Host is reachable' : '✗ Host is unreachable'}</strong>
                </div>
                <pre style="margin-top: 0.5rem; font-size: 0.8rem; white-space: pre-wrap;">${result.output}</pre>
            `;
        }
    } catch (error) {
        container.innerHTML = '<div class="error">Error running ping test</div>';
    }
}

async function runDnsTest() {
    const domain = document.getElementById('dnsTarget').value;
    const container = document.getElementById('dnsResults');
    
    container.innerHTML = '<div class="loading-spinner"></div>';
    
    try {
        const response = await fetch(`/api/network/dns?domain=${encodeURIComponent(domain)}`);
        const data = await response.json();
        
        if (data.status === 'success') {
            const result = data.data;
            container.innerHTML = `
                <div class="${result.success ? 'success' : 'error'}">
                    <strong>${result.success ? '✓ DNS Resolution Successful' : '✗ DNS Resolution Failed'}</strong>
                </div>
                ${result.success ? `
                    <div style="margin-top: 0.5rem;">
                        <strong>Domain:</strong> ${result.domain}<br>
                        <strong>IP Address:</strong> ${result.resolved_ip}
                    </div>
                ` : `<div>${result.error || 'Unable to resolve'}</div>`}
            `;
        }
    } catch (error) {
        container.innerHTML = '<div class="error">Error running DNS test</div>';
    }
}

async function runPortCheck() {
    const host = document.getElementById('portHost').value;
    const port = document.getElementById('portNumber').value;
    const container = document.getElementById('portResults');
    
    container.innerHTML = '<div class="loading-spinner"></div>';
    
    try {
        const response = await fetch(`/api/network/port-check?host=${encodeURIComponent(host)}&port=${port}`);
        const data = await response.json();
        
        if (data.status === 'success') {
            const result = data.data;
            container.innerHTML = `
                <div class="${result.open ? 'success' : 'error'}">
                    <strong>${result.open ? '✓ Port is OPEN' : '✗ Port is CLOSED'}</strong>
                </div>
                <div style="margin-top: 0.5rem;">
                    <strong>Host:</strong> ${result.host}<br>
                    <strong>Port:</strong> ${result.port}
                </div>
            `;
        }
    } catch (error) {
        container.innerHTML = '<div class="error">Error checking port</div>';
    }
}

async function runTraceroute() {
    const target = document.getElementById('tracerouteTarget').value;
    const container = document.getElementById('tracerouteResults');
    
    container.innerHTML = '<div class="loading-spinner"></div><p style="text-align: center; margin-top: 1rem;">Running traceroute... This may take a moment.</p>';
    
    try {
        const response = await fetch(`/api/network/traceroute?target=${encodeURIComponent(target)}`);
        const data = await response.json();
        
        if (data.status === 'success') {
            container.innerHTML = `<pre>${data.data.output}</pre>`;
        }
    } catch (error) {
        container.innerHTML = '<div class="error">Error running traceroute</div>';
    }
}

// ==================== PERFORMANCE ====================
async function loadStartupPrograms() {
    const container = document.getElementById('startupList');
    if (!container) return;
    
    try {
        const response = await fetch('/api/system/startup');
        const data = await response.json();
        
        if (data.status === 'success' && data.data.length > 0) {
            container.innerHTML = data.data.map(prog => `
                <div class="startup-item">
                    <div class="startup-icon">
                        <i class="fas fa-play"></i>
                    </div>
                    <div class="startup-info">
                        <span class="startup-name">${prog.name}</span>
                        <span class="startup-path">${prog.path}</span>
                    </div>
                </div>
            `).join('');
        } else {
            container.innerHTML = '<div class="empty-state"><i class="fas fa-rocket"></i><span>No startup programs found</span></div>';
        }
    } catch (error) {
        container.innerHTML = '<div class="empty-state"><i class="fas fa-exclamation-circle"></i><span>Failed to load startup programs</span></div>';
    }
}

async function cleanTempFiles() {
    showToast('Cleaning...', 'Removing temporary files', 'info');
    
    try {
        const response = await fetch('/api/system/clean-temp', { method: 'POST' });
        const data = await response.json();
        
        if (data.status === 'success') {
            showToast('Success!', `Cleaned ${data.data.files_deleted} files, freed ${data.data.space_freed_mb} MB`, 'success');
            
            const resultsContainer = document.getElementById('cleanerResults');
            if (resultsContainer) {
                resultsContainer.classList.add('show');
                resultsContainer.innerHTML = `
                    <div class="success">
                        <strong>✓ Cleanup Complete!</strong><br>
                        Files deleted: ${data.data.files_deleted}<br>
                        Space freed: ${data.data.space_freed_mb} MB
                    </div>
                `;
            }
        }
    } catch (error) {
        showToast('Error', 'Failed to clean temp files', 'error');
    }
}

async function runSpeedTest() {
    const container = document.getElementById('speedResults');
    if (container) {
        container.classList.add('show');
        container.innerHTML = '<div class="loading-spinner"></div><p style="text-align: center;">Testing download speed...</p>';
    }
    
    showToast('Speed Test', 'Running speed test...', 'info');
    
    try {
        const response = await fetch('/api/experimental/speed-test');
        const data = await response.json();
        
        if (data.status === 'success') {
            if (container) {
                container.innerHTML = `
                    <div class="speed-value">${data.data.download_speed_mbps}</div>
                    <div class="speed-unit">Mbps Download</div>
                `;
            }
            showToast('Speed Test Complete', `Download: ${data.data.download_speed_mbps} Mbps`, 'success');
        }
    } catch (error) {
        if (container) {
            container.innerHTML = '<div class="error">Speed test failed</div>';
        }
        showToast('Error', 'Speed test failed', 'error');
    }
}

// ==================== PERIPHERALS ====================
async function loadPrinters() {
    const container = document.getElementById('printersList');
    if (!container) return;
    
    try {
        const response = await fetch('/api/devices/printers');
        const data = await response.json();
        
        if (data.status === 'success' && data.data.length > 0) {
            container.innerHTML = data.data.map(printer => `
                <div class="device-item">
                    <div class="device-icon">
                        <i class="fas fa-print"></i>
                    </div>
                    <div class="device-info">
                        <span class="device-name">${printer.name}</span>
                        <span class="device-status">${printer.driver}</span>
                    </div>
                    <span class="device-badge ${printer.status === 'Online' ? 'online' : 'offline'}">
                        ${printer.status}
                    </span>
                </div>
            `).join('');
        } else {
            container.innerHTML = '<div class="empty-state"><i class="fas fa-print"></i><span>No printers found</span></div>';
        }
    } catch (error) {
        container.innerHTML = '<div class="empty-state"><i class="fas fa-exclamation-circle"></i><span>Failed to load printers</span></div>';
    }
}

async function loadAudioDevices() {
    const container = document.getElementById('audioList');
    if (!container) return;
    
    try {
        const response = await fetch('/api/devices/audio');
        const data = await response.json();
        
        if (data.status === 'success' && data.data.length > 0) {
            container.innerHTML = data.data.map(device => `
                <div class="device-item">
                    <div class="device-icon">
                        <i class="fas fa-volume-high"></i>
                    </div>
                    <div class="device-info">
                        <span class="device-name">${device.name}</span>
                        <span class="device-status">${device.status}</span>
                    </div>
                </div>
            `).join('');
        } else {
            container.innerHTML = '<div class="empty-state"><i class="fas fa-volume-high"></i><span>No audio devices found</span></div>';
        }
    } catch (error) {
        container.innerHTML = '<div class="empty-state"><i class="fas fa-exclamation-circle"></i><span>Failed to load audio devices</span></div>';
    }
}

async function loadCameras() {
    const container = document.getElementById('camerasList');
    if (!container) return;
    
    try {
        const response = await fetch('/api/devices/cameras');
        const data = await response.json();
        
        if (data.status === 'success' && data.data.length > 0) {
            container.innerHTML = data.data.map(device => `
                <div class="device-item">
                    <div class="device-icon">
                        <i class="fas fa-camera"></i>
                    </div>
                    <div class="device-info">
                        <span class="device-name">${device.name}</span>
                        <span class="device-status">${device.status}</span>
                    </div>
                </div>
            `).join('');
        } else {
            container.innerHTML = '<div class="empty-state"><i class="fas fa-camera"></i><span>No cameras found</span></div>';
        }
    } catch (error) {
        container.innerHTML = '<div class="empty-state"><i class="fas fa-exclamation-circle"></i><span>Failed to load cameras</span></div>';
    }
}

async function loadBluetooth() {
    const container = document.getElementById('bluetoothList');
    if (!container) return;
    
    try {
        const response = await fetch('/api/devices/bluetooth');
        const data = await response.json();
        
        if (data.status === 'success' && data.data.devices.length > 0) {
            container.innerHTML = data.data.devices.map(device => `
                <div class="device-item">
                    <div class="device-icon">
                        <i class="fab fa-bluetooth-b"></i>
                    </div>
                    <div class="device-info">
                        <span class="device-name">${device.name}</span>
                        <span class="device-status">${device.status}</span>
                    </div>
                </div>
            `).join('');
        } else {
            container.innerHTML = '<div class="empty-state"><i class="fab fa-bluetooth-b"></i><span>No Bluetooth devices found</span></div>';
        }
    } catch (error) {
        container.innerHTML = '<div class="empty-state"><i class="fas fa-exclamation-circle"></i><span>Failed to load Bluetooth</span></div>';
    }
}

async function loadUsbDevices() {
    const container = document.getElementById('usbList');
    if (!container) return;
    
    try {
        const response = await fetch('/api/devices/usb');
        const data = await response.json();
        
        if (data.status === 'success' && data.data.length > 0) {
            container.innerHTML = data.data.map(device => `
                <div class="device-item">
                    <div class="device-icon">
                        <i class="fas fa-usb"></i>
                    </div>
                    <div class="device-info">
                        <span class="device-name">${device.name}</span>
                        <span class="device-status">${device.status}</span>
                    </div>
                </div>
            `).join('');
        } else {
            container.innerHTML = '<div class="empty-state"><i class="fas fa-usb"></i><span>No USB devices found</span></div>';
        }
    } catch (error) {
        container.innerHTML = '<div class="empty-state"><i class="fas fa-exclamation-circle"></i><span>Failed to load USB devices</span></div>';
    }
}

// ==================== INVENTORY ====================
async function loadInventory() {
    try {
        const response = await fetch('/api/inventory/device');
        const data = await response.json();
        
        if (data.status === 'success') {
            updateHardwareInventory(data.data.hardware);
            updateBrowsersInventory(data.data.browsers);
            updateSoftwareList(data.data.software);
            allSoftware = data.data.software;
        }
    } catch (error) {
        console.error('Error loading inventory:', error);
    }
}

function updateHardwareInventory(hardware) {
    const container = document.getElementById('hardwareInventory');
    if (!container) return;
    
    container.innerHTML = `
        <div class="inventory-item">
            <span class="info-label">Device Name</span>
            <span class="info-value">${hardware.device_name}</span>
        </div>
        <div class="inventory-item">
            <span class="info-label">Operating System</span>
            <span class="info-value">${hardware.os}</span>
        </div>
        <div class="inventory-item">
            <span class="info-label">OS Version</span>
            <span class="info-value">${hardware.os_version}</span>
        </div>
        <div class="inventory-item">
            <span class="info-label">Processor</span>
            <span class="info-value">${hardware.processor}</span>
        </div>
        <div class="inventory-item">
            <span class="info-label">RAM</span>
            <span class="info-value">${hardware.ram_gb} GB</span>
        </div>
        <div class="inventory-item">
            <span class="info-label">Architecture</span>
            <span class="info-value">${hardware.architecture}</span>
        </div>
    `;
}

function updateBrowsersInventory(browsers) {
    const container = document.getElementById('browsersInventory');
    if (!container) return;
    
    if (browsers.length > 0) {
        container.innerHTML = browsers.map(browser => `
            <div class="inventory-item">
                <span class="info-label">${browser.name}</span>
                <span class="info-value" style="color: var(--success);">Installed</span>
            </div>
        `).join('');
    } else {
        container.innerHTML = '<div class="empty-state"><i class="fas fa-globe"></i><span>No browsers detected</span></div>';
    }
}

function updateSoftwareList(software) {
    const container = document.getElementById('softwareList');
    if (!container) return;
    
    if (software.length > 0) {
        container.innerHTML = software.map(sw => `
            <div class="software-item">
                <div>
                    <span class="software-name">${sw.name}</span>
                    ${sw.publisher ? `<span class="software-version">${sw.publisher}</span>` : ''}
                </div>
                <span class="software-version">${sw.version || 'N/A'}</span>
            </div>
        `).join('');
    } else {
        container.innerHTML = '<div class="empty-state"><i class="fas fa-cube"></i><span>No software detected</span></div>';
    }
}

function filterSoftware() {
    const search = document.getElementById('softwareSearch').value.toLowerCase();
    const filtered = allSoftware.filter(sw => 
        sw.name.toLowerCase().includes(search) || 
        (sw.publisher && sw.publisher.toLowerCase().includes(search))
    );
    updateSoftwareList(filtered);
}

// ==================== TICKETS ====================
function initializeTicketFilters() {
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            filterTickets(btn.dataset.filter);
        });
    });
}

async function loadTickets() {
    try {
        const response = await fetch('/api/tickets');
        const data = await response.json();
        
        if (data.status === 'success') {
            updateTicketsDisplay(data.data);
            updateRecentTickets(data.data);
        }
    } catch (error) {
        console.error('Error loading tickets:', error);
    }
}

function updateTicketsDisplay(tickets) {
    const container = document.getElementById('ticketsTable');
    if (!container) return;
    
    if (tickets.length > 0) {
        container.innerHTML = tickets.map(ticket => `
            <div class="ticket-row" onclick="showTicketDetails('${ticket.id}')">
                <span class="ticket-id">#${ticket.id}</span>
                <div class="ticket-info">
                    <span class="ticket-title">${ticket.title}</span>
                    <span class="ticket-meta">${ticket.user} • ${new Date(ticket.created).toLocaleDateString()}</span>
                </div>
                <span class="ticket-status ${ticket.status}">${ticket.status}</span>
                <span class="badge" style="background: var(--${getPriorityColor(ticket.priority)}-bg); color: var(--${getPriorityColor(ticket.priority)});">${ticket.priority}</span>
                <select onchange="updateTicketStatus('${ticket.id}', this.value)" onclick="event.stopPropagation()">
                    <option value="open" ${ticket.status === 'open' ? 'selected' : ''}>Open</option>
                    <option value="in-progress" ${ticket.status === 'in-progress' ? 'selected' : ''}>In Progress</option>
                    <option value="resolved" ${ticket.status === 'resolved' ? 'selected' : ''}>Resolved</option>
                </select>
            </div>
        `).join('');
    } else {
        container.innerHTML = '<div class="empty-state"><i class="fas fa-inbox"></i><span>No tickets found</span></div>';
    }
}

function updateRecentTickets(tickets) {
    const container = document.getElementById('recentTickets');
    if (!container) return;
    
    const recent = tickets.slice(0, 5);
    
    if (recent.length > 0) {
        container.innerHTML = recent.map(ticket => `
            <div class="ticket-item" onclick="showSection('tickets')">
                <div class="ticket-priority ${ticket.priority}"></div>
                <div class="ticket-info">
                    <span class="ticket-title">${ticket.title}</span>
                    <span class="ticket-meta">#${ticket.id} • ${ticket.user}</span>
                </div>
                <span class="ticket-status ${ticket.status}">${ticket.status}</span>
            </div>
        `).join('');
    } else {
        container.innerHTML = '<div class="empty-state"><i class="fas fa-inbox"></i><span>No tickets yet</span></div>';
    }
}

function getPriorityColor(priority) {
    const colors = {
        low: 'info',
        medium: 'warning',
        high: 'danger',
        critical: 'danger'
    };
    return colors[priority] || 'info';
}

async function createTicket(event) {
    event.preventDefault();
    
    const ticket = {
        title: document.getElementById('ticketTitle').value,
        description: document.getElementById('ticketDescription').value,
        category: document.getElementById('ticketCategory').value,
        priority: document.getElementById('ticketPriority').value,
        user: document.getElementById('ticketUser').value
    };
    
    try {
        const response = await fetch('/api/tickets', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(ticket)
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            showToast('Success!', `Ticket #${data.data.id} created`, 'success');
            document.getElementById('ticketForm').reset();
            loadTickets();
        }
    } catch (error) {
        showToast('Error', 'Failed to create ticket', 'error');
    }
}

async function updateTicketStatus(ticketId, status) {
    try {
        const response = await fetch(`/api/tickets/${ticketId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status })
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            showToast('Updated', `Ticket #${ticketId} status changed to ${status}`, 'success');
            loadTickets();
        }
    } catch (error) {
        showToast('Error', 'Failed to update ticket', 'error');
    }
}

function filterTickets(filter) {
    // Re-fetch and filter tickets
    fetch('/api/tickets')
        .then(res => res.json())
        .then(data => {
            if (data.status === 'success') {
                let filtered = data.data;
                if (filter !== 'all') {
                    filtered = data.data.filter(t => t.status === filter);
                }
                updateTicketsDisplay(filtered);
            }
        });
}

// ==================== TOOLS ====================
async function clearBrowserCache() {
    showToast('Cleaning...', 'Clearing browser cache', 'info');
    
    try {
        const response = await fetch('/api/tools/browser-cache', { method: 'POST' });
        const data = await response.json();
        
        if (data.status === 'success') {
            showToast('Success!', `Cleared cache for: ${data.data.browsers_cleaned.join(', ') || 'No browsers'}`, 'success');
        }
    } catch (error) {
        showToast('Error', 'Failed to clear browser cache', 'error');
    }
}

async function networkReset() {
    showToast('Resetting...', 'Resetting network configuration', 'info');
    
    try {
        const response = await fetch('/api/tools/network-reset', { method: 'POST' });
        const data = await response.json();
        
        if (data.status === 'success') {
            showToast('Network Reset', 'Network configuration has been reset', 'success');
        }
    } catch (error) {
        showToast('Error', 'Failed to reset network', 'error');
    }
}

async function flushDNS() {
    showToast('Flushing...', 'Clearing DNS resolver cache', 'info');
    
    try {
        const response = await fetch('/api/tools/flush-dns', { method: 'POST' });
        const data = await response.json();
        
        if (data.status === 'success') {
            showToast('DNS Flushed', 'DNS resolver cache has been cleared', 'success');
        }
    } catch (error) {
        showToast('Error', 'Failed to flush DNS cache', 'error');
    }
}

async function loadErrorLogs() {
    const card = document.getElementById('errorLogsCard');
    const container = document.getElementById('errorLogsList');
    
    if (card) card.style.display = 'block';
    if (container) container.innerHTML = '<div class="loading-spinner"></div>';
    
    try {
        const response = await fetch('/api/tools/error-logs');
        const data = await response.json();
        
        if (data.status === 'success' && data.data.length > 0) {
            container.innerHTML = data.data.map(log => `
                <div class="error-log-item">
                    <div class="error-log-header">
                        <span class="error-log-source">${log.source}</span>
                        <span class="error-log-time">${log.time}</span>
                    </div>
                    <div class="error-log-message">${log.message}</div>
                </div>
            `).join('');
        } else {
            container.innerHTML = '<div class="empty-state"><i class="fas fa-check-circle"></i><span>No recent errors</span></div>';
        }
    } catch (error) {
        container.innerHTML = '<div class="empty-state"><i class="fas fa-exclamation-circle"></i><span>Failed to load error logs</span></div>';
    }
}

// ==================== AUDIT LOGS ====================
async function loadAuditLogs() {
    const dashboardContainer = document.getElementById('recentLogs');
    const fullContainer = document.getElementById('auditLogsTable');
    
    try {
        const response = await fetch('/api/audit-logs');
        const data = await response.json();
        
        if (data.status === 'success') {
            // Dashboard preview
            if (dashboardContainer) {
                const recent = data.data.slice(0, 5);
                if (recent.length > 0) {
                    dashboardContainer.innerHTML = recent.map(log => `
                        <div class="log-item">
                            <span class="log-time">${new Date(log.timestamp).toLocaleTimeString()}</span>
                            <span class="log-action">${log.action}</span>
                            <span class="log-details">${log.details}</span>
                        </div>
                    `).join('');
                } else {
                    dashboardContainer.innerHTML = '<div class="empty-state"><i class="fas fa-clock-rotate-left"></i><span>No recent activity</span></div>';
                }
            }
            
            // Full logs
            if (fullContainer) {
                if (data.data.length > 0) {
                    fullContainer.innerHTML = data.data.map(log => `
                        <div class="audit-log-row">
                            <span class="audit-log-time">${new Date(log.timestamp).toLocaleString()}</span>
                            <span class="audit-log-action">${log.action}</span>
                            <span>${log.details}</span>
                            <span>${log.user}</span>
                        </div>
                    `).join('');
                } else {
                    fullContainer.innerHTML = '<div class="empty-state"><i class="fas fa-scroll"></i><span>No audit logs</span></div>';
                }
            }
        }
    } catch (error) {
        console.error('Error loading audit logs:', error);
    }
}

// ==================== REPORTS ====================
async function generateReport(type) {
    const container = document.getElementById('reportDisplay');
    const content = document.getElementById('reportContent');
    
    if (container) container.style.display = 'block';
    if (content) content.innerHTML = '<div class="loading-spinner"></div><p style="text-align: center;">Generating report...</p>';
    
    showToast('Generating Report', 'Please wait...', 'info');
    
    try {
        const response = await fetch(`/api/reports/generate?type=${type}`);
        const data = await response.json();
        
        if (data.status === 'success') {
            const report = data.data;
            content.innerHTML = `
                <div class="report-section">
                    <h4>📋 Report Information</h4>
                    <div class="info-grid">
                        <div class="info-item">
                            <span class="info-label">Generated</span>
                            <span class="info-value">${new Date(report.generated).toLocaleString()}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Device</span>
                            <span class="info-value">${report.device_name}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Report Type</span>
                            <span class="info-value">${report.type.toUpperCase()}</span>
                        </div>
                    </div>
                </div>
                
                <div class="report-section">
                    <h4>🖥️ System Health</h4>
                    <div class="info-grid">
                        <div class="info-item">
                            <span class="info-label">Operating System</span>
                            <span class="info-value">${report.sections.system.os}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">CPU Usage</span>
                            <span class="info-value">${report.sections.system.cpu_usage}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Memory Usage</span>
                            <span class="info-value">${report.sections.system.memory_usage}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Available Memory</span>
                            <span class="info-value">${report.sections.system.memory_available}</span>
                        </div>
                    </div>
                </div>
                
                <div class="report-section">
                    <h4>💾 Disk Storage</h4>
                    <div class="info-grid">
                        ${report.sections.disks.map(disk => `
                            <div class="info-item">
                                <span class="info-label">${disk.drive}</span>
                                <span class="info-value">${disk.usage} used, ${disk.free} free</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
                
                <div class="report-section">
                    <h4>🌐 Network</h4>
                    <div class="info-grid">
                        <div class="info-item">
                            <span class="info-label">Local IP</span>
                            <span class="info-value">${report.sections.network.local_ip}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Hostname</span>
                            <span class="info-value">${report.sections.network.hostname}</span>
                        </div>
                    </div>
                </div>
            `;
            
            showToast('Report Generated', 'Report is ready', 'success');
        }
    } catch (error) {
        content.innerHTML = '<div class="error">Failed to generate report. Please try again.</div>';
        showToast('Error', 'Failed to generate report', 'error');
    }
}

function exportReport() {
    const reportContent = document.getElementById('reportContent');
    const reportText = reportContent.innerText;
    
    // Create a nicely formatted text report
    const header = `
════════════════════════════════════════════════════════════════
                    ENDPOINT ASSIST REPORT
════════════════════════════════════════════════════════════════
Generated: ${new Date().toLocaleString()}
────────────────────────────────────────────────────────────────

`;
    const footer = `
────────────────────────────────────────────────────────────────
                   End of Report
════════════════════════════════════════════════════════════════
`;
    
    const fullReport = header + reportText + footer;
    const blob = new Blob([fullReport], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Endpoint_Assist_Report_${new Date().toISOString().split('T')[0]}.txt`;
    a.click();
    URL.revokeObjectURL(url);
    showToast('Report Exported', 'Report saved to Downloads folder', 'success');
}

function printReport() {
    window.print();
    showToast('Printing', 'Print dialog opened', 'info');
}

// ==================== EXPERIMENTAL ====================
async function runNetworkScan() {
    const container = document.getElementById('networkScanResults');
    container.innerHTML = '<div class="loading-spinner"></div><p>Scanning network...</p>';
    
    try {
        const response = await fetch('/api/experimental/network-scan');
        const data = await response.json();
        
        if (data.status === 'success') {
            container.innerHTML = `
                <p><strong>Your IP:</strong> ${data.data.local_ip}</p>
                <p><strong>Devices found:</strong></p>
                <div class="devices-list">
                    ${data.data.devices.map(device => `
                        <div class="device-item">
                            <div class="device-icon">
                                <i class="fas fa-desktop"></i>
                            </div>
                            <div class="device-info">
                                <span class="device-name">${device.ip}</span>
                                <span class="device-status">${device.mac}</span>
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
        }
    } catch (error) {
        container.innerHTML = '<div class="error">Scan failed</div>';
    }
}

function toggleDarkMode() {
    const enabled = document.getElementById('darkModeToggle').checked;
    if (enabled) {
        document.body.classList.remove('light-mode');
    } else {
        document.body.classList.add('light-mode');
    }
    localStorage.setItem('darkMode', enabled);
}

function toggleAutoRefresh() {
    const enabled = document.getElementById('autoRefreshToggle').checked;
    localStorage.setItem('autoRefresh', enabled);
    
    if (enabled) {
        startAutoRefresh();
        showToast('Auto-refresh', 'Enabled (30s)', 'info');
    } else {
        stopAutoRefresh();
        showToast('Auto-refresh', 'Disabled', 'info');
    }
}

function startAutoRefresh() {
    if (autoRefreshInterval) return;
    autoRefreshInterval = setInterval(() => {
        loadSectionData(currentSection);
    }, 30000);
}

function stopAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
        autoRefreshInterval = null;
    }
}

function toggleCompactMode() {
    const enabled = document.getElementById('compactModeToggle').checked;
    document.body.classList.toggle('compact-mode', enabled);
    localStorage.setItem('compactMode', enabled);
}

// ==================== TOAST NOTIFICATIONS ====================
function showToast(title, message, type = 'info') {
    const container = document.getElementById('toastContainer');
    
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-times-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    };
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <i class="fas ${icons[type]}"></i>
        <div class="toast-content">
            <span class="toast-title">${title}</span>
            <span class="toast-message">${message}</span>
        </div>
        <span class="toast-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </span>
    `;
    
    container.appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (toast.parentElement) {
            toast.remove();
        }
    }, 5000);
}

// ==================== MODAL ====================
function showModal(title, content, footer = '') {
    document.getElementById('modalTitle').textContent = title;
    document.getElementById('modalContent').innerHTML = content;
    document.getElementById('modalFooter').innerHTML = footer;
    document.getElementById('modalOverlay').classList.add('active');
}

function closeModal() {
    document.getElementById('modalOverlay').classList.remove('active');
}

// Close modal on overlay click
document.getElementById('modalOverlay')?.addEventListener('click', (e) => {
    if (e.target.id === 'modalOverlay') {
        closeModal();
    }
});

// ==================== UTILITIES ====================
function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function showTicketDetails(ticketId) {
    // This could open a modal with full ticket details
    showToast('Ticket Details', `Viewing ticket #${ticketId}`, 'info');
}

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl+R to refresh
    if (e.ctrlKey && e.key === 'r') {
        e.preventDefault();
        refreshAll();
    }
    
    // Escape to close modal
    if (e.key === 'Escape') {
        closeModal();
    }
});

// ==================== KNOWLEDGE BASE ====================
let allKBArticles = [];

async function loadKnowledgeBase() {
    try {
        const response = await fetch('/api/knowledge-base');
        const data = await response.json();
        allKBArticles = data.articles || [];
        renderKBArticles(allKBArticles);
    } catch (error) {
        console.error('Error loading knowledge base:', error);
        showToast('Error', 'Failed to load knowledge base', 'error');
    }
}

function renderKBArticles(articles) {
    const grid = document.getElementById('kbArticlesGrid');
    if (!grid) return;
    
    if (articles.length === 0) {
        grid.innerHTML = `
            <div class="card">
                <div class="card-content empty-state">
                    <i class="fas fa-search"></i>
                    <p>No articles found</p>
                </div>
            </div>
        `;
        return;
    }
    
    grid.innerHTML = articles.map(article => `
        <div class="card kb-article-card" onclick="viewKBArticle(${article.id})">
            <div class="card-header">
                <span class="kb-category-badge ${article.category.toLowerCase()}">${article.category}</span>
            </div>
            <div class="card-content">
                <h4>${article.title}</h4>
                <p class="kb-preview">${article.content.substring(0, 100)}...</p>
                <div class="kb-tags">
                    ${article.tags.map(tag => `<span class="kb-tag">${tag}</span>`).join('')}
                </div>
            </div>
        </div>
    `).join('');
}

async function searchKnowledgeBase() {
    const query = document.getElementById('kbSearchInput').value.trim();
    
    if (query.length === 0) {
        renderKBArticles(allKBArticles);
        return;
    }
    
    if (query.length < 2) return;
    
    try {
        const response = await fetch(`/api/knowledge-base/search?q=${encodeURIComponent(query)}`);
        const data = await response.json();
        renderKBArticles(data.articles || []);
    } catch (error) {
        console.error('Error searching knowledge base:', error);
    }
}

async function viewKBArticle(articleId) {
    try {
        const response = await fetch(`/api/knowledge-base/${articleId}`);
        const article = await response.json();
        
        document.getElementById('kbArticlesGrid').style.display = 'none';
        document.querySelector('#knowledgeSection .card:first-of-type').style.display = 'none';
        document.getElementById('kbArticleDetail').style.display = 'block';
        
        document.getElementById('kbArticleTitle').textContent = article.title;
        
        // Format the content with proper step numbers and styling
        let formattedContent = article.content
            .split('\n')
            .map(line => {
                // Format numbered steps with styled numbers
                if (/^\d+\.\s/.test(line.trim())) {
                    const match = line.match(/^(\d+)\.\s(.+)/);
                    if (match) {
                        return `<div class="kb-step"><span class="kb-step-number">${match[1]}</span><span class="kb-step-text">${match[2]}</span></div>`;
                    }
                }
                // Format paths/commands in code style
                line = line.replace(/`([^`]+)`/g, '<code>$1</code>');
                // Format file paths
                line = line.replace(/(C:\\[^\s,]+)/g, '<code>$1</code>');
                line = line.replace(/(%[^%]+%)/g, '<code>$1</code>');
                return line;
            })
            .join('<br>');
        
        document.getElementById('kbArticleContent').innerHTML = `
            <div class="kb-article-meta">
                <span class="kb-category-badge ${article.category.toLowerCase()}">${article.category}</span>
                <span class="kb-article-id">Article #${article.id}</span>
            </div>
            <div class="kb-article-text">${formattedContent}</div>
            <div class="kb-tags">
                <span class="kb-tags-label"><i class="fas fa-tags"></i> Related:</span>
                ${article.tags.map(tag => `<span class="kb-tag">${tag}</span>`).join('')}
            </div>
        `;
    } catch (error) {
        showToast('Error', 'Failed to load article', 'error');
    }
}

function backToKBList() {
    document.getElementById('kbArticlesGrid').style.display = 'grid';
    document.querySelector('#knowledgeSection .card:first-of-type').style.display = 'block';
    document.getElementById('kbArticleDetail').style.display = 'none';
}

// ==================== AD USER LOOKUP ====================
let selectedADUser = null;

async function searchADUsers() {
    const query = document.getElementById('adSearchInput').value.trim();
    
    if (query.length < 2) {
        document.getElementById('adUsersBody').innerHTML = `
            <tr>
                <td colspan="7" class="empty-state">
                    <i class="fas fa-users"></i>
                    <p>Enter at least 2 characters to search</p>
                </td>
            </tr>
        `;
        document.getElementById('adUserCount').textContent = '0 users';
        document.getElementById('adUserActions').style.display = 'none';
        return;
    }
    
    try {
        const response = await fetch(`/api/ad/search?q=${encodeURIComponent(query)}`);
        const data = await response.json();
        renderADUsers(data.users || []);
    } catch (error) {
        console.error('Error searching AD users:', error);
        showToast('Error', 'Failed to search users', 'error');
    }
}

function renderADUsers(users) {
    const tbody = document.getElementById('adUsersBody');
    document.getElementById('adUserCount').textContent = `${users.length} user${users.length !== 1 ? 's' : ''}`;
    
    if (users.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="empty-state">
                    <i class="fas fa-user-slash"></i>
                    <p>No users found</p>
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = users.map(user => `
        <tr onclick="selectADUser('${user.username}')" class="clickable-row">
            <td><strong>${user.username}</strong></td>
            <td>${user.full_name}</td>
            <td>${user.email}</td>
            <td>${user.department}</td>
            <td>
                <span class="status-badge ${user.status === 'Active' ? 'success' : 'danger'}">
                    ${user.status}
                </span>
            </td>
            <td>${user.last_login}</td>
            <td>
                <button class="btn-icon" onclick="event.stopPropagation(); selectADUser('${user.username}')" title="Select User">
                    <i class="fas fa-arrow-right"></i>
                </button>
            </td>
        </tr>
    `).join('');
}

function selectADUser(username) {
    selectedADUser = username;
    document.getElementById('selectedUserName').textContent = username;
    document.getElementById('adUserActions').style.display = 'block';
    
    // Highlight selected row
    document.querySelectorAll('#adUsersBody tr').forEach(row => {
        row.classList.remove('selected');
        if (row.textContent.includes(username)) {
            row.classList.add('selected');
        }
    });
    
    showToast('User Selected', `Selected user: ${username}`, 'info');
}

async function resetUserPassword() {
    if (!selectedADUser) {
        showToast('Error', 'No user selected', 'error');
        return;
    }
    
    const confirmed = confirm(`Are you sure you want to reset the password for ${selectedADUser}?`);
    if (!confirmed) return;
    
    try {
        const response = await fetch(`/api/ad/reset-password/${selectedADUser}`, { method: 'POST' });
        const data = await response.json();
        
        if (data.success) {
            showModal('Password Reset', `
                <div class="password-reset-result">
                    <i class="fas fa-check-circle success-icon"></i>
                    <h3>Password Reset Successful</h3>
                    <p>User: <strong>${selectedADUser}</strong></p>
                    <p>Temporary Password: <code class="temp-password">${data.temp_password}</code></p>
                    <p class="warning-text"><i class="fas fa-exclamation-triangle"></i> User will be required to change password on next login.</p>
                </div>
            `, `
                <button class="btn secondary" onclick="copyToClipboard('${data.temp_password}')">
                    <i class="fas fa-copy"></i> Copy Password
                </button>
                <button class="btn primary" onclick="closeModal()">Close</button>
            `);
            
            addAuditLog('Password Reset', selectedADUser, 'success');
        }
    } catch (error) {
        showToast('Error', 'Failed to reset password', 'error');
    }
}

async function unlockUserAccount() {
    if (!selectedADUser) {
        showToast('Error', 'No user selected', 'error');
        return;
    }
    
    try {
        const response = await fetch(`/api/ad/unlock/${selectedADUser}`, { method: 'POST' });
        const data = await response.json();
        
        if (data.success) {
            showToast('Account Unlocked', `Account for ${selectedADUser} has been unlocked`, 'success');
            addAuditLog('Account Unlock', selectedADUser, 'success');
            searchADUsers(); // Refresh the list
        }
    } catch (error) {
        showToast('Error', 'Failed to unlock account', 'error');
    }
}

function viewUserDetails() {
    if (!selectedADUser) return;
    
    showModal('User Details', `
        <div class="user-details-modal">
            <div class="detail-row">
                <span class="label">Username:</span>
                <span class="value">${selectedADUser}</span>
            </div>
            <div class="detail-row">
                <span class="label">Status:</span>
                <span class="value"><span class="status-badge success">Active</span></span>
            </div>
            <div class="detail-row">
                <span class="label">Groups:</span>
                <span class="value">Domain Users, Staff, IT Support</span>
            </div>
            <div class="detail-row">
                <span class="label">Last Password Change:</span>
                <span class="value">2024-01-15</span>
            </div>
            <div class="detail-row">
                <span class="label">Account Created:</span>
                <span class="value">2023-08-20</span>
            </div>
        </div>
    `, '<button class="btn primary" onclick="closeModal()">Close</button>');
}

function sendPasswordEmail() {
    if (!selectedADUser) return;
    showToast('Email Sent', `Password reset instructions sent to ${selectedADUser}`, 'success');
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('Copied', 'Password copied to clipboard', 'success');
    });
}

// ==================== ONBOARDING ====================
let onboardingTasks = [];

async function loadOnboardingChecklist() {
    try {
        const response = await fetch('/api/onboarding/checklist');
        const data = await response.json();
        onboardingTasks = data.tasks || [];
        renderOnboardingChecklist();
    } catch (error) {
        console.error('Error loading checklist:', error);
        showToast('Error', 'Failed to load checklist', 'error');
    }
}

function renderOnboardingChecklist() {
    const container = document.getElementById('onboardingChecklist');
    if (!container) return;
    
    const completedCount = onboardingTasks.filter(t => t.completed).length;
    const totalCount = onboardingTasks.length;
    const percentage = totalCount > 0 ? Math.round((completedCount / totalCount) * 100) : 0;
    
    document.getElementById('onboardProgress').textContent = `${completedCount} / ${totalCount} Complete`;
    document.getElementById('onboardProgressBar').style.width = `${percentage}%`;
    
    // Group tasks by category
    const categories = {};
    onboardingTasks.forEach(task => {
        if (!categories[task.category]) {
            categories[task.category] = [];
        }
        categories[task.category].push(task);
    });
    
    container.innerHTML = Object.entries(categories).map(([category, tasks]) => `
        <div class="checklist-category">
            <h4><i class="fas ${getCategoryIcon(category)}"></i> ${category}</h4>
            <div class="checklist-items">
                ${tasks.map(task => `
                    <div class="checklist-item ${task.completed ? 'completed' : ''}" onclick="toggleOnboardingTask(${task.id})">
                        <div class="checkbox-wrapper">
                            <input type="checkbox" ${task.completed ? 'checked' : ''} onchange="toggleOnboardingTask(${task.id})">
                            <span class="checkmark"></span>
                        </div>
                        <span class="task-name">${task.task}</span>
                    </div>
                `).join('')}
            </div>
        </div>
    `).join('');
}

function getCategoryIcon(category) {
    const icons = {
        'Account Setup': 'fa-user-shield',
        'Hardware': 'fa-laptop',
        'Software': 'fa-download',
        'Access & Permissions': 'fa-key',
        'Training': 'fa-graduation-cap'
    };
    return icons[category] || 'fa-tasks';
}

function toggleOnboardingTask(taskId) {
    const task = onboardingTasks.find(t => t.id === taskId);
    if (task) {
        task.completed = !task.completed;
        renderOnboardingChecklist();
    }
}

function saveOnboardingProgress() {
    const empName = document.getElementById('newEmpName').value || 'New Employee';
    localStorage.setItem('onboardingProgress', JSON.stringify({
        employee: empName,
        tasks: onboardingTasks,
        savedAt: new Date().toISOString()
    }));
    showToast('Saved', 'Onboarding progress saved successfully', 'success');
}

function generateOnboardingReport() {
    const empName = document.getElementById('newEmpName').value || 'New Employee';
    const dept = document.getElementById('newEmpDept').value || 'N/A';
    const completedCount = onboardingTasks.filter(t => t.completed).length;
    
    showModal('Onboarding Report', `
        <div class="onboarding-report">
            <h3>New Employee IT Setup Report</h3>
            <hr>
            <p><strong>Employee:</strong> ${empName}</p>
            <p><strong>Department:</strong> ${dept}</p>
            <p><strong>Date:</strong> ${new Date().toLocaleDateString()}</p>
            <p><strong>Progress:</strong> ${completedCount} / ${onboardingTasks.length} tasks completed</p>
            <h4>Completed Tasks:</h4>
            <ul>
                ${onboardingTasks.filter(t => t.completed).map(t => `<li>✅ ${t.task}</li>`).join('')}
            </ul>
            <h4>Pending Tasks:</h4>
            <ul>
                ${onboardingTasks.filter(t => !t.completed).map(t => `<li>⏳ ${t.task}</li>`).join('')}
            </ul>
        </div>
    `, `
        <button class="btn secondary" onclick="window.print()"><i class="fas fa-print"></i> Print</button>
        <button class="btn primary" onclick="closeModal()">Close</button>
    `);
}

function sendWelcomeEmail() {
    const empName = document.getElementById('newEmpName').value;
    if (!empName) {
        showToast('Error', 'Please enter employee name', 'error');
        return;
    }
    showToast('Email Sent', `Welcome email sent to ${empName}`, 'success');
}

function resetOnboardingChecklist() {
    onboardingTasks.forEach(t => t.completed = false);
    renderOnboardingChecklist();
    showToast('Reset', 'Checklist has been reset', 'info');
}

// ==================== SERVICES ====================
let allServices = [];

async function loadServices() {
    try {
        const response = await fetch('/api/services');
        const data = await response.json();
        allServices = data.services || [];
        renderServices(allServices);
    } catch (error) {
        console.error('Error loading services:', error);
    }
}

async function loadCriticalServices() {
    try {
        const response = await fetch('/api/services/critical');
        const data = await response.json();
        renderCriticalServices(data.services || []);
    } catch (error) {
        console.error('Error loading critical services:', error);
    }
}

function renderCriticalServices(services) {
    const container = document.getElementById('criticalServicesGrid');
    if (!container) return;
    
    container.innerHTML = services.map(svc => `
        <div class="service-status-card ${svc.status === 'Running' ? 'running' : 'stopped'}">
            <div class="service-icon">
                <i class="fas ${svc.status === 'Running' ? 'fa-check-circle' : 'fa-times-circle'}"></i>
            </div>
            <div class="service-info">
                <span class="service-name">${svc.display_name}</span>
                <span class="service-status">${svc.status}</span>
            </div>
        </div>
    `).join('');
}

function renderServices(services) {
    const tbody = document.getElementById('servicesBody');
    if (!tbody) return;
    
    tbody.innerHTML = services.map(svc => `
        <tr>
            <td><code>${svc.name}</code></td>
            <td>${svc.display_name}</td>
            <td>
                <span class="status-badge ${svc.status === 'Running' ? 'success' : 'danger'}">
                    ${svc.status}
                </span>
            </td>
            <td>${svc.start_type}</td>
        </tr>
    `).join('');
}

function filterServices() {
    const query = document.getElementById('serviceSearch').value.toLowerCase();
    const filtered = allServices.filter(svc => 
        svc.name.toLowerCase().includes(query) || 
        svc.display_name.toLowerCase().includes(query)
    );
    renderServices(filtered);
}

// ==================== COMPLIANCE ====================
async function runComplianceCheck() {
    showToast('Checking', 'Running compliance checks...', 'info');
    
    try {
        const response = await fetch('/api/compliance/check');
        const data = await response.json();
        renderComplianceResults(data);
    } catch (error) {
        console.error('Error running compliance check:', error);
        showToast('Error', 'Failed to run compliance check', 'error');
    }
}

function renderComplianceResults(data) {
    // Update score gauge
    const score = data.score || 0;
    const gaugeFill = document.getElementById('complianceGaugeFill');
    const circumference = 2 * Math.PI * 85;
    const offset = circumference - (score / 100) * circumference;
    gaugeFill.style.strokeDasharray = circumference;
    gaugeFill.style.strokeDashoffset = offset;
    
    // Color based on score
    if (score >= 80) {
        gaugeFill.style.stroke = 'var(--success-color)';
    } else if (score >= 60) {
        gaugeFill.style.stroke = 'var(--warning-color)';
    } else {
        gaugeFill.style.stroke = 'var(--danger-color)';
    }
    
    document.getElementById('complianceScore').textContent = score;
    
    // Update stats
    const checks = data.checks || [];
    const passed = checks.filter(c => c.status === 'passed').length;
    const failed = checks.filter(c => c.status === 'failed').length;
    const warnings = checks.filter(c => c.status === 'warning').length;
    
    document.getElementById('passedChecks').textContent = passed;
    document.getElementById('failedChecks').textContent = failed;
    document.getElementById('warningChecks').textContent = warnings;
    
    // Render checks list
    const container = document.getElementById('complianceChecksList');
    container.innerHTML = checks.map(check => `
        <div class="compliance-check-item ${check.status}">
            <div class="check-status-icon">
                <i class="fas ${check.status === 'passed' ? 'fa-check-circle' : check.status === 'failed' ? 'fa-times-circle' : 'fa-exclamation-triangle'}"></i>
            </div>
            <div class="check-details">
                <span class="check-name">${check.name}</span>
                <span class="check-description">${check.description}</span>
            </div>
        </div>
    `).join('');
}

// ==================== REMOTE TOOLS ====================
async function launchRDP() {
    const target = document.getElementById('rdpTarget').value.trim();
    if (!target) {
        showToast('Error', 'Please enter a computer name or IP address', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/remote/rdp', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ target })
        });
        const data = await response.json();
        
        if (data.success) {
            showToast('RDP', `Launching Remote Desktop to ${target}`, 'success');
            addAuditLog('RDP Connection', target, 'success');
        }
    } catch (error) {
        showToast('Error', 'Failed to launch RDP', 'error');
    }
}

function quickConnect(target) {
    document.getElementById('rdpTarget').value = target;
    launchRDP();
}

async function runCommand(cmd) {
    const outputEl = document.getElementById('commandOutput');
    outputEl.textContent = `Running ${cmd}...\n`;
    
    try {
        let endpoint = '';
        switch (cmd) {
            case 'gpupdate':
                endpoint = '/api/system/gpupdate';
                break;
            case 'ipconfig':
                endpoint = '/api/network/ipconfig';
                break;
            case 'systeminfo':
                endpoint = '/api/system/info';
                break;
            case 'whoami':
                endpoint = '/api/system/whoami';
                break;
            default:
                outputEl.textContent = 'Unknown command';
                return;
        }
        
        const response = await fetch(endpoint);
        const data = await response.json();
        
        outputEl.textContent = typeof data === 'string' ? data : JSON.stringify(data, null, 2);
    } catch (error) {
        outputEl.textContent = `Error: ${error.message}`;
    }
}

function clearCommandOutput() {
    document.getElementById('commandOutput').textContent = 'Command output will appear here...';
}

// ==================== AUDIT LOG HELPER ====================
function addAuditLog(action, target, status) {
    const logs = JSON.parse(localStorage.getItem('auditLogs') || '[]');
    logs.unshift({
        timestamp: new Date().toISOString(),
        action,
        target,
        status,
        user: 'IT Admin'
    });
    localStorage.setItem('auditLogs', JSON.stringify(logs.slice(0, 100)));
}

// ==================== macOS SUPPORT ====================
function loadMacInfo() {
    showToast('Refreshing', 'Loading macOS information...', 'info');
    // In production, this would query a Mac via API
    setTimeout(() => {
        showToast('Updated', 'macOS information refreshed', 'success');
    }, 500);
}

function macCommand(command) {
    const guides = {
        resetSMC: {
            title: 'Reset SMC (System Management Controller)',
            content: `<h4>For MacBooks with Apple Silicon (M1/M2/M3):</h4>
<p>Simply restart your Mac. The SMC resets automatically on Apple Silicon.</p>

<h4>For Intel MacBooks with T2 chip:</h4>
<ol>
<li>Shut down your Mac</li>
<li>Press and hold <strong>Control + Option + Shift</strong> (left side) for 7 seconds</li>
<li>While holding those keys, press and hold the <strong>Power button</strong> for 7 more seconds</li>
<li>Release all keys, wait a few seconds, then turn on your Mac</li>
</ol>

<h4>For older Intel MacBooks:</h4>
<ol>
<li>Shut down your Mac</li>
<li>Press <strong>Shift + Control + Option</strong> (left side) + Power button together</li>
<li>Hold for 10 seconds, then release</li>
<li>Turn on your Mac normally</li>
</ol>`
        },
        resetNVRAM: {
            title: 'Reset NVRAM/PRAM',
            content: `<h4>For Apple Silicon Macs:</h4>
<p>NVRAM resets automatically when needed. You can also reset by:</p>
<ol>
<li>Shut down your Mac</li>
<li>Turn it on and immediately open <strong>Terminal</strong></li>
<li>Run: <code>sudo nvram -c</code></li>
<li>Restart your Mac</li>
</ol>

<h4>For Intel Macs:</h4>
<ol>
<li>Shut down your Mac</li>
<li>Turn it on and immediately press and hold: <strong>Option + Command + P + R</strong></li>
<li>Hold for about 20 seconds (you may hear a startup sound)</li>
<li>Release the keys and let your Mac start normally</li>
</ol>

<p><em>This resets display resolution, startup disk selection, sound volume, and time zone.</em></p>`
        },
        safeMode: {
            title: 'Boot into Safe Mode',
            content: `<h4>For Apple Silicon Macs:</h4>
<ol>
<li>Shut down your Mac completely</li>
<li>Press and hold the <strong>Power button</strong> until "Loading startup options" appears</li>
<li>Select your startup disk</li>
<li>Press and hold <strong>Shift</strong>, then click "Continue in Safe Mode"</li>
</ol>

<h4>For Intel Macs:</h4>
<ol>
<li>Shut down your Mac</li>
<li>Turn it on and immediately press and hold <strong>Shift</strong></li>
<li>Release Shift when you see the login window</li>
<li>"Safe Boot" should appear in the menu bar</li>
</ol>

<p><em>Safe Mode runs disk repair, loads only essential extensions, and clears caches.</em></p>`
        },
        diskUtility: {
            title: 'Run Disk Utility First Aid',
            content: `<h4>From within macOS:</h4>
<ol>
<li>Open <strong>Disk Utility</strong> (Applications > Utilities)</li>
<li>Select your startup disk (usually "Macintosh HD")</li>
<li>Click <strong>First Aid</strong> in the toolbar</li>
<li>Click <strong>Run</strong> to start the repair</li>
</ol>

<h4>From Recovery Mode (for serious issues):</h4>
<ol>
<li><strong>Apple Silicon:</strong> Hold Power button at startup until options appear, select Options > Continue</li>
<li><strong>Intel Mac:</strong> Hold Command + R at startup</li>
<li>Select <strong>Disk Utility</strong> from the utilities window</li>
<li>Run First Aid on Macintosh HD - Data first, then Macintosh HD</li>
</ol>

<p><em>First Aid checks the disk for errors and repairs directory structure issues.</em></p>`
        }
    };
    
    const guide = guides[command];
    if (guide) {
        showModal(guide.title, `<div class="mac-guide">${guide.content}</div>`, 
            '<button class="btn primary" onclick="closeModal()">Got It</button>');
    }
}

// ==================== MOBILE DEVICE SUPPORT ====================
function mobileAction(action) {
    const actions = {
        enrollMDM: { title: 'MDM Enrollment', message: 'Opening MDM enrollment portal for device...' },
        configEmail: { title: 'Email Configuration', message: 'Pushing corporate email profile to device...' },
        installApps: { title: 'App Installation', message: 'Deploying required apps via MDM...' },
        configWifi: { title: 'WiFi Setup', message: 'Pushing enterprise WiFi profile (WPA2-Enterprise)...' },
        wipeDevice: { title: 'Remote Wipe', message: 'WARNING: This will erase all data on the device!' }
    };
    
    const act = actions[action];
    if (action === 'wipeDevice') {
        if (confirm('Are you sure you want to remote wipe this device? This action cannot be undone.')) {
            showToast('Remote Wipe', 'Wipe command sent to device', 'warning');
            addAuditLog('Remote Wipe', 'Mobile Device', 'initiated');
        }
    } else {
        showToast(act.title, act.message, 'info');
        setTimeout(() => {
            showToast('Success', `${act.title} completed`, 'success');
        }, 1500);
    }
}

function showMobileKB(topic) {
    const articles = {
        'email-sync': {
            title: 'Email Not Syncing on Mobile',
            content: `<h4>iOS (iPhone/iPad):</h4>
<ol>
<li>Go to <strong>Settings > Mail > Accounts</strong></li>
<li>Select your corporate account</li>
<li>Toggle Mail off and back on</li>
<li>If issues persist, remove account and re-add using: <code>outlook.office365.com</code></li>
</ol>

<h4>Android:</h4>
<ol>
<li>Open <strong>Outlook app</strong> or <strong>Gmail</strong></li>
<li>Go to Settings > Select your account</li>
<li>Check sync settings are enabled</li>
<li>Clear app cache: Settings > Apps > Outlook > Clear Cache</li>
</ol>`
        },
        'wifi-connect': {
            title: 'Connecting to Enterprise WiFi',
            content: `<h4>Connect to WPA2-Enterprise / eduroam:</h4>
<ol>
<li>Go to WiFi settings on your device</li>
<li>Select your <strong>enterprise network</strong></li>
<li>Username: <code>username@yourdomain.com</code></li>
<li>Password: Your corporate password</li>
<li>If prompted for certificate, select "Trust" or "Accept"</li>
</ol>

<p><em>Note: eduroam works at participating institutions worldwide!</em></p>`
        },
        'mfa-setup': {
            title: 'Setting Up MFA/Authenticator',
            content: `<h4>Install Authenticator App:</h4>
<ol>
<li>Download <strong>Microsoft Authenticator</strong> or <strong>Duo Mobile</strong> from App Store or Google Play</li>
<li>Go to your organization's identity portal and sign in</li>
<li>Navigate to Security Settings > Two-Factor Authentication</li>
<li>Click "Add Device" and scan the QR code with your authenticator app</li>
<li>Complete the test authentication</li>
</ol>`
        },
        'vpn-mobile': {
            title: 'VPN on Mobile Devices',
            content: `<h4>iOS:</h4>
<ol>
<li>Download <strong>Cisco AnyConnect</strong> or your company's VPN app from App Store</li>
<li>Open the app, tap "Connections" > "Add VPN Connection"</li>
<li>Server: <code>vpn.yourcompany.com</code></li>
<li>Tap Connect and enter your corporate credentials</li>
</ol>

<h4>Android:</h4>
<ol>
<li>Download <strong>Cisco AnyConnect</strong> or your company's VPN app from Play Store</li>
<li>Add new connection with your corporate VPN server</li>
<li>Connect using your username and password</li>
</ol>`
        }
    };
    
    const article = articles[topic];
    if (article) {
        showModal(article.title, `<div class="mobile-kb-article">${article.content}</div>`,
            '<button class="btn primary" onclick="closeModal()">Close</button>');
    }
}

// ==================== IoT & AV DEVICES ====================
function refreshIoTDevices() {
    showToast('Refreshing', 'Scanning IoT devices...', 'info');
    setTimeout(() => {
        showToast('Updated', 'Device status refreshed', 'success');
    }, 1000);
}

function avControl(action) {
    const actionNames = {
        powerOn: 'Powering on all displays',
        powerOff: 'Powering off all displays',
        hdmi1: 'Switching to HDMI 1 input',
        wireless: 'Enabling wireless display mode',
        camera: 'Toggling room camera',
        mute: 'Muting room audio'
    };
    
    showToast('AV Control', actionNames[action] || 'Sending command...', 'info');
    addAuditLog('AV Control', action, 'success');
    
    setTimeout(() => {
        showToast('Complete', 'AV command executed', 'success');
    }, 800);
}

// ==================== PROCUREMENT ====================
function submitPurchaseRequest() {
    const item = document.getElementById('purchaseItem').value;
    const qty = document.getElementById('purchaseQty').value;
    const vendor = document.getElementById('purchaseVendor').value;
    const cost = document.getElementById('purchaseCost').value;
    const justification = document.getElementById('purchaseJustification').value;
    
    if (!item || !vendor) {
        showToast('Error', 'Please fill in item description and vendor', 'error');
        return;
    }
    
    // Generate PO number
    const poNumber = `PO-2026-${String(Math.floor(Math.random() * 9000) + 1000)}`;
    
    showModal('Purchase Request Submitted', `
        <div class="po-confirmation">
            <i class="fas fa-check-circle" style="font-size: 3rem; color: var(--success); margin-bottom: 1rem;"></i>
            <h3>Request Submitted Successfully</h3>
            <p><strong>PO Number:</strong> ${poNumber}</p>
            <p><strong>Item:</strong> ${item} (x${qty})</p>
            <p><strong>Vendor:</strong> ${vendor}</p>
            <p><strong>Est. Cost:</strong> ${cost || 'TBD'}</p>
            <p class="po-note"><i class="fas fa-info-circle"></i> Your request has been sent to the approver for review.</p>
        </div>
    `, '<button class="btn primary" onclick="closeModal()">Done</button>');
    
    // Clear form
    document.getElementById('purchaseItem').value = '';
    document.getElementById('purchaseJustification').value = '';
    
    addAuditLog('Purchase Request', `${poNumber} - ${item}`, 'submitted');
    showToast('Submitted', `Purchase request ${poNumber} created`, 'success');
}

console.log('🚀 Endpoint Assist loaded successfully');
