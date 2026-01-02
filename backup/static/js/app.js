// NeuroNet JavaScript Application

// Global state
let currentWallet = null;
let networkStats = {};
let networkChart = null;

// DOM Elements
const walletModal = document.getElementById('walletModal');
const walletStatus = document.getElementById('walletStatus');
const walletDisplay = document.getElementById('walletDisplay');

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    initWalletModal();
    loadWalletFromStorage();
    updateNetworkStats();
    
    // Update stats every 10 seconds
    setInterval(updateNetworkStats, 10000);
    
    // Initialize charts if on homepage
    if (document.getElementById('networkChart')) {
        initNetworkChart();
    }
});

// Wallet Functions
function initWalletModal() {
    // Tab switching
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const tab = this.dataset.tab;
            
            // Update active tab button
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            // Show corresponding tab content
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            document.getElementById(tab + 'Tab').classList.add('active');
        });
    });
    
    // Close modal when clicking X
    document.querySelector('.close-modal').addEventListener('click', closeWalletModal);
    
    // Close modal when clicking outside
    window.addEventListener('click', function(event) {
        if (event.target === walletModal) {
            closeWalletModal();
        }
    });
    
    // Create wallet button
    document.getElementById('createWalletBtn').addEventListener('click', createWallet);
    
    // Load wallet button
    document.getElementById('loadWalletBtn').addEventListener('click', loadWallet);
    
    // Copy private key button
    document.getElementById('copyPrivateKeyBtn').addEventListener('click', copyPrivateKey);
}

function openWalletModal() {
    walletModal.style.display = 'flex';
}

function closeWalletModal() {
    walletModal.style.display = 'none';
}

async function createWallet() {
    try {
        const response = await fetch('/api/create-wallet', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Show wallet details
            document.getElementById('newAddress').textContent = data.address;
            document.getElementById('newPrivateKey').textContent = data.private_key;
            document.getElementById('newPublicKey').textContent = data.public_key;
            document.getElementById('newWalletInfo').classList.remove('hidden');
            
            // Save to local storage
            localStorage.setItem('neuroWallet', JSON.stringify({
                address: data.address,
                publicKey: data.public_key,
                privateKey: data.private_key
            }));
            
            // Update UI
            updateWalletStatus(data.address);
            
            // Close modal after 3 seconds
            setTimeout(() => {
                closeWalletModal();
                showNotification('Wallet created successfully!', 'success');
                updateNetworkStats();
            }, 3000);
        }
    } catch (error) {
        showNotification('Error creating wallet: ' + error.message, 'error');
    }
}

async function loadWallet() {
    const privateKey = document.getElementById('privateKeyInput').value.trim();
    
    if (!privateKey) {
        showNotification('Please enter your private key', 'warning');
        return;
    }
    
    try {
        const response = await fetch('/api/load-wallet', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ private_key: privateKey })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Save to local storage
            localStorage.setItem('neuroWallet', JSON.stringify({
                address: data.address,
                publicKey: data.public_key,
                privateKey: privateKey
            }));
            
            // Update UI
            updateWalletStatus(data.address);
            closeWalletModal();
            showNotification('Wallet loaded successfully!', 'success');
            updateNetworkStats();
        } else {
            showNotification('Invalid private key', 'error');
        }
    } catch (error) {
        showNotification('Error loading wallet: ' + error.message, 'error');
    }
}

function loadWalletFromStorage() {
    const savedWallet = localStorage.getItem('neuroWallet');
    
    if (savedWallet) {
        const wallet = JSON.parse(savedWallet);
        updateWalletStatus(wallet.address);
    }
}

function updateWalletStatus(address) {
    if (address) {
        const shortAddress = address.substring(0, 8) + '...' + address.substring(address.length - 8);
        walletStatus.textContent = shortAddress;
        currentWallet = address;
        
        // Update display color
        walletDisplay.style.background = 'linear-gradient(45deg, #28a745, #20c997)';
        
        // Get wallet info
        fetchWalletInfo();
    } else {
        walletStatus.textContent = 'Not Connected';
        currentWallet = null;
        walletDisplay.style.background = '';
    }
}

async function fetchWalletInfo() {
    if (!currentWallet) return;
    
    try {
        const response = await fetch('/api/wallet-info');
        if (response.ok) {
            const data = await response.json();
            walletStatus.textContent = `${data.address.substring(0, 8)}... | Balance: ${data.balance.toFixed(2)}`;
        }
    } catch (error) {
        console.error('Error fetching wallet info:', error);
    }
}

function copyPrivateKey() {
    const privateKey = document.getElementById('newPrivateKey').textContent;
    navigator.clipboard.writeText(privateKey)
        .then(() => showNotification('Private key copied to clipboard!', 'success'))
        .catch(err => showNotification('Copy failed: ' + err, 'error'));
}

// Network Stats
async function updateNetworkStats() {
    try {
        const response = await fetch('/api/network-stats');
        const data = await response.json();
        networkStats = data;
        
        // Update stats on homepage
        if (document.getElementById('totalNfts')) {
            document.getElementById('totalNfts').textContent = data.total_nfts;
            document.getElementById('blockHeight').textContent = data.blockchain_length;
            document.getElementById('totalIntelligence').textContent = data.total_intelligence.toFixed(2);
            document.getElementById('networkDifficulty').textContent = data.current_difficulty;
        }
        
        // Update chart if exists
        if (networkChart) {
            updateNetworkChart();
        }
        
        // Update recent blocks
        if (document.getElementById('recentBlocks')) {
            updateRecentBlocks();
        }
    } catch (error) {
        console.error('Error updating network stats:', error);
    }
}

function initNetworkChart() {
    const ctx = document.getElementById('networkChart').getContext('2d');
    
    networkChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Transactions',
                data: [],
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    labels: { color: '#fff' }
                }
            },
            scales: {
                x: {
                    ticks: { color: '#aaa' },
                    grid: { color: 'rgba(255,255,255,0.1)' }
                },
                y: {
                    ticks: { color: '#aaa' },
                    grid: { color: 'rgba(255,255,255,0.1)' }
                }
            }
        }
    });
    
    // Add some sample data
    for (let i = 0; i < 10; i++) {
        networkChart.data.labels.push(`Block ${i}`);
        networkChart.data.datasets[0].data.push(Math.floor(Math.random() * 50));
    }
    networkChart.update();
}

function updateNetworkChart() {
    if (!networkChart) return;
    
    // Add new data point
    const newLabel = `Block ${networkStats.blockchain_length}`;
    const newData = networkStats.pending_transactions || 0;
    
    networkChart.data.labels.push(newLabel);
    networkChart.data.datasets[0].data.push(newData);
    
    // Keep only last 10 points
    if (networkChart.data.labels.length > 10) {
        networkChart.data.labels.shift();
        networkChart.data.datasets[0].data.shift();
    }
    
    networkChart.update();
}

async function updateRecentBlocks() {
    try {
        const response = await fetch('/api/blockchain');
        const data = await response.json();
        
        const recentBlocks = document.getElementById('recentBlocks');
        recentBlocks.innerHTML = '';
        
        // Show last 5 blocks
        const lastBlocks = data.chain.slice(-5).reverse();
        
        lastBlocks.forEach(block => {
            const blockEl = document.createElement('div');
            blockEl.className = 'block-item';
            blockEl.innerHTML = `
                <div class="block-header">
                    <span class="block-index">#${block.index}</span>
                    <span class="block-time">${formatTime(block.timestamp)}</span>
                </div>
                <div class="block-hash">${block.hash.substring(0, 20)}...</div>
                <div class="block-transactions">${block.transactions?.length || 0} transactions</div>
            `;
            recentBlocks.appendChild(blockEl);
        });
    } catch (error) {
        console.error('Error fetching recent blocks:', error);
    }
}

// Utility Functions
function showNotification(message, type = 'info') {
    // Remove existing notification
    const existingNotification = document.querySelector('.notification');
    if (existingNotification) {
        existingNotification.remove();
    }
    
    // Create notification
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <span>${message}</span>
        <button onclick="this.parentElement.remove()">&times;</button>
    `;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background: ${type === 'success' ? '#28a745' : type === 'error' ? '#dc3545' : '#17a2b8'};
        color: white;
        border-radius: 5px;
        z-index: 3000;
        display: flex;
        justify-content: space-between;
        align-items: center;
        min-width: 300px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

function formatTime(timestamp) {
    const date = new Date(timestamp * 1000 || timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

// Make functions available globally
window.openWalletModal = openWalletModal;
window.closeWalletModal = closeWalletModal;
window.createWallet = createWallet;
window.loadWallet = loadWallet;
window.copyPrivateKey = copyPrivateKey;
