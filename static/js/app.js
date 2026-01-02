// NeuroNet AI Blockchain - Main JavaScript

// Global variables
let currentWallet = null;
let networkStats = {};
let walletModal = null;

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    initApplication();
});

function initApplication() {
    // Initialize wallet modal
    walletModal = document.getElementById('walletModal');
    if (walletModal) {
        initWalletModal();
    }
    
    // Load wallet from localStorage
    loadWalletFromStorage();
    
    // Update network stats
    updateNetworkStats();
    
    // Set up periodic updates
    setInterval(updateNetworkStats, 10000); // Update every 10 seconds
    
    // Set up mining button if it exists
    const miningBtn = document.getElementById('startMiningBtn');
    if (miningBtn) {
        miningBtn.addEventListener('click', startMining);
    }
}

// ===== WALLET FUNCTIONS =====

function initWalletModal() {
    // Close modal when clicking X
    const closeBtn = document.querySelector('.close-modal');
    if (closeBtn) {
        closeBtn.addEventListener('click', closeWalletModal);
    }
    
    // Close modal when clicking outside
    window.addEventListener('click', function(event) {
        if (event.target === walletModal) {
            closeWalletModal();
        }
    });
    
    // Tab switching
    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const tab = this.textContent.toLowerCase().includes('create') ? 'create' : 'load';
            switchTab(tab);
        });
    });
    
    // Create wallet button
    const createBtn = document.getElementById('createWalletBtn');
    if (createBtn) {
        createBtn.addEventListener('click', createWallet);
    }
    
    // Load wallet button
    const loadBtn = document.getElementById('loadWalletBtn');
    if (loadBtn) {
        loadBtn.addEventListener('click', loadWallet);
    }
    
    // Copy private key button
    const copyBtn = document.getElementById('copyPrivateKeyBtn');
    if (copyBtn) {
        copyBtn.addEventListener('click', copyPrivateKey);
    }
}

function openWalletModal() {
    if (walletModal) {
        walletModal.style.display = 'flex';
    }
}

function closeWalletModal() {
    if (walletModal) {
        walletModal.style.display = 'none';
    }
}

function switchTab(tab) {
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Update tab contents
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    // Activate selected tab
    if (tab === 'create') {
        document.querySelector('.tab-btn:first-child').classList.add('active');
        document.getElementById('createTab').classList.add('active');
    } else {
        document.querySelector('.tab-btn:last-child').classList.add('active');
        document.getElementById('loadTab').classList.add('active');
    }
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
            document.getElementById('newWalletInfo').classList.remove('hidden');
            
            // Save to localStorage
            localStorage.setItem('neuroWallet', JSON.stringify({
                address: data.address,
                privateKey: data.private_key,
                publicKey: data.public_key
            }));
            
            // Update wallet status
            updateWalletStatus(data.address);
            
            // Close modal after 3 seconds
            setTimeout(() => {
                closeWalletModal();
                showNotification('Wallet created successfully! Save your private key!', 'success');
                updateNetworkStats();
                
                // Refresh page if on wallet-related pages
                if (window.location.pathname.includes('/wallet') || 
                    window.location.pathname.includes('/mint') || 
                    window.location.pathname.includes('/train')) {
                    window.location.reload();
                }
            }, 3000);
        }
    } catch (error) {
        showNotification('Error creating wallet: ' + error.message, 'error');
    }
}

async function loadWallet() {
    const privateKeyInput = document.getElementById('privateKeyInput');
    const privateKey = privateKeyInput.value.trim();
    
    if (!privateKey) {
        showNotification('Please enter your private key', 'error');
        return;
    }
    
    // Validate private key format
    if (privateKey.length !== 64 || !/^[0-9a-f]+$/.test(privateKey)) {
        showNotification('Invalid private key format. Must be 64 hexadecimal characters.', 'error');
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
            // Save to localStorage
            localStorage.setItem('neuroWallet', JSON.stringify({
                address: data.address,
                privateKey: privateKey,
                publicKey: data.public_key
            }));
            
            // Update wallet status
            updateWalletStatus(data.address);
            
            // Clear input and close modal
            privateKeyInput.value = '';
            closeWalletModal();
            
            showNotification('Wallet loaded successfully!', 'success');
            updateNetworkStats();
            
            // Refresh page if on wallet-related pages
            if (window.location.pathname.includes('/wallet') || 
                window.location.pathname.includes('/mint') || 
                window.location.pathname.includes('/train')) {
                window.location.reload();
            }
        } else {
            showNotification(data.error || 'Invalid private key', 'error');
        }
    } catch (error) {
        showNotification('Error loading wallet: ' + error.message, 'error');
    }
}

function loadWalletFromStorage() {
    const saved = localStorage.getItem('neuroWallet');
    if (saved) {
        try {
            const wallet = JSON.parse(saved);
            updateWalletStatus(wallet.address);
        } catch (e) {
            console.error('Error loading wallet from storage:', e);
        }
    }
}

function updateWalletStatus(address) {
    const walletStatus = document.getElementById('walletStatus');
    const walletDisplay = document.getElementById('walletDisplay');
    
    if (!walletStatus || !walletDisplay) return;
    
    if (address) {
        currentWallet = address;
        const shortAddr = address.substring(0, 10) + '...' + address.substring(address.length - 6);
        walletStatus.textContent = shortAddr;
        walletDisplay.style.background = 'linear-gradient(45deg, #28a745, #20c997)';
        
        // Update wallet info if on wallet page
        if (typeof loadWalletData === 'function') {
            loadWalletData();
        }
    } else {
        currentWallet = null;
        walletStatus.textContent = 'Not Connected';
        walletDisplay.style.background = '';
    }
}

function copyPrivateKey() {
    const privateKey = document.getElementById('newPrivateKey').textContent;
    if (!privateKey) return;
    
    navigator.clipboard.writeText(privateKey)
        .then(() => showNotification('Private key copied to clipboard!', 'success'))
        .catch(err => showNotification('Copy failed: ' + err, 'error'));
}

// ===== NETWORK FUNCTIONS =====

async function updateNetworkStats() {
    try {
        const response = await fetch('/api/network-stats');
        const data = await response.json();
        networkStats = data;
        
        // Update stats on homepage
        if (document.getElementById('totalNfts')) {
            document.getElementById('totalNfts').textContent = data.total_nfts;
            document.getElementById('blockHeight').textContent = data.blockchain_length;
            document.getElementById('networkIntelligence').textContent = data.total_intelligence;
            document.getElementById('currentDifficulty').textContent = data.current_difficulty;
            document.getElementById('pendingTx').textContent = data.pending_transactions;
            document.getElementById('miningReward').textContent = data.mining_reward + ' NN';
            document.getElementById('totalValue').textContent = data.total_value + ' NN';
        }
        
        // Update marketplace stats
        if (document.getElementById('marketTotalNFTs')) {
            document.getElementById('marketTotalNFTs').textContent = data.total_nfts;
            document.getElementById('marketTotalValue').textContent = data.total_value;
            document.getElementById('marketAvgIntelligence').textContent = data.average_intelligence;
        }
        
        // Update recent blocks if on homepage
        if (document.getElementById('recentBlocks') && currentWallet) {
            updateRecentBlocks();
        }
    } catch (error) {
        console.error('Error updating network stats:', error);
    }
}

async function startMining() {
    if (!currentWallet) {
        showNotification('Please connect wallet first', 'warning');
        openWalletModal();
        return;
    }
    
    try {
        const response = await fetch('/api/start-mining', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification(data.message, 'success');
            updateNetworkStats();
        } else {
            showNotification(data.error || 'Mining failed', 'error');
        }
    } catch (error) {
        showNotification('Error starting mining: ' + error.message, 'error');
    }
}

async function updateRecentBlocks() {
    try {
        const response = await fetch('/api/blockchain');
        const data = await response.json();
        
        const recentBlocksDiv = document.getElementById('recentBlocks');
        if (!recentBlocksDiv) return;
        
        if (data.chain && data.chain.length > 0) {
            let html = '<div class="blocks-list">';
            const lastBlocks = data.chain.slice(-5).reverse();
            
            lastBlocks.forEach(block => {
                const txCount = Array.isArray(block.transactions) ? block.transactions.length : 0;
                html += `
                    <div class="block-item">
                        <div class="block-header">
                            <span class="block-index">Block #${block.index}</span>
                            <span class="block-time">${formatTime(block.timestamp)}</span>
                        </div>
                        <div class="block-hash">${block.hash.substring(0, 20)}...</div>
                        <div class="block-info">
                            <span>Transactions: ${txCount}</span>
                            <span>Difficulty: ${block.difficulty}</span>
                        </div>
                    </div>
                `;
            });
            
            html += '</div>';
            recentBlocksDiv.innerHTML = html;
        }
    } catch (error) {
        console.error('Error loading recent blocks:', error);
    }
}

// ===== UTILITY FUNCTIONS =====

function showNotification(message, type = 'info') {
    const container = document.getElementById('notificationContainer');
    if (!container) return;
    
    // Remove existing notifications after 5 seconds
    const notifications = container.querySelectorAll('.notification');
    notifications.forEach(notification => {
        setTimeout(() => {
            if (notification.parentElement) {
                notification.style.animation = 'slideOut 0.3s ease-out';
                setTimeout(() => notification.remove(), 300);
            }
        }, 5000);
    });
    
    // Create notification
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            ${type === 'success' ? '✅' : type === 'error' ? '❌' : type === 'warning' ? '⚠️' : 'ℹ️'} ${message}
        </div>
    `;
    
    container.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => notification.remove(), 300);
        }
    }, 5000);
}

function formatTime(timestamp) {
    const date = new Date(timestamp * 1000 || timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function formatDate(timestamp) {
    const date = new Date(timestamp * 1000 || timestamp);
    return date.toLocaleDateString();
}

// ===== MAKE FUNCTIONS GLOBALLY AVAILABLE =====

window.openWalletModal = openWalletModal;
window.closeWalletModal = closeWalletModal;
window.createWallet = createWallet;
window.loadWallet = loadWallet;
window.copyPrivateKey = copyPrivateKey;
window.startMining = startMining;
window.showNotification = showNotification;
