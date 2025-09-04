// Crusont API Key Management Frontend
class CrusontAPI {
    constructor() {
        this.apiKey = null;
        this.userInfo = null;
        this.apiKeys = [];
        this.baseURL = window.location.origin; // Use same origin as frontend
        
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // Auth
        document.getElementById('authBtn').addEventListener('click', () => this.authenticate());
        document.getElementById('apiKey').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.authenticate();
        });

        // Create key modal
        document.getElementById('createKeyBtn').addEventListener('click', () => this.showCreateKeyModal());
        document.getElementById('closeModal').addEventListener('click', () => this.hideCreateKeyModal());
        document.getElementById('cancelCreate').addEventListener('click', () => this.hideCreateKeyModal());
        document.getElementById('confirmCreate').addEventListener('click', () => this.createApiKey());

        // New key modal
        document.getElementById('closeNewKeyModal').addEventListener('click', () => this.hideNewKeyModal());
        document.getElementById('closeNewKey').addEventListener('click', () => this.hideNewKeyModal());
        document.getElementById('copyKey').addEventListener('click', () => this.copyApiKey());

        // Filtering and sorting
        document.getElementById('sortKeys').addEventListener('change', () => this.renderApiKeys());
        document.getElementById('filterKeys').addEventListener('change', () => this.renderApiKeys());

        // Close modals on outside click
        document.getElementById('createKeyModal').addEventListener('click', (e) => {
            if (e.target.id === 'createKeyModal') this.hideCreateKeyModal();
        });
        document.getElementById('newKeyModal').addEventListener('click', (e) => {
            if (e.target.id === 'newKeyModal') this.hideNewKeyModal();
        });

        // Add keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch(e.key) {
                    case 'k':
                        e.preventDefault();
                        document.getElementById('apiKey').focus();
                        break;
                    case 'n':
                        e.preventDefault();
                        if (!document.getElementById('dashboard').classList.contains('hidden')) {
                            this.showCreateKeyModal();
                        }
                        break;
                }
            }
        });
    }

    async authenticate() {
        const apiKeyInput = document.getElementById('apiKey');
        const authBtn = document.getElementById('authBtn');
        const status = document.getElementById('authStatus');

        const apiKey = apiKeyInput.value.trim();
        if (!apiKey) {
            this.showStatus('Please enter an API key', 'error');
            return;
        }

        authBtn.textContent = 'Authenticating...';
        authBtn.disabled = true;

        try {
            // Test the API key by making a request to get user info
            const response = await fetch(`${this.baseURL}/v1/keys`, {
                headers: {
                    'Authorization': `Bearer ${apiKey}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                this.apiKey = apiKey;
                this.showStatus('Authentication successful!', 'success');
                await this.loadUserData();
                this.showDashboard();
            } else {
                const error = await response.json();
                this.showStatus(`Authentication failed: ${error.detail || 'Invalid API key'}`, 'error');
            }
        } catch (error) {
            this.showStatus(`Authentication failed: ${error.message}`, 'error');
        } finally {
            authBtn.textContent = 'Authenticate';
            authBtn.disabled = false;
        }
    }

    async loadUserData() {
        try {
            // Load API keys
            const keysResponse = await fetch(`${this.baseURL}/v1/keys`, {
                headers: {
                    'Authorization': `Bearer ${this.apiKey}`,
                    'Content-Type': 'application/json'
                }
            });

            if (keysResponse.ok) {
                const keysData = await keysResponse.json();
                this.apiKeys = keysData.data || [];
                this.renderApiKeys();
            }

            // Load user info (we'll get this from the first API key response)
            if (this.apiKeys.length > 0) {
                this.userInfo = {
                    totalKeys: this.apiKeys.length,
                    activeKeys: this.apiKeys.filter(key => key.last_used).length
                };
                this.renderUserInfo();
            }
        } catch (error) {
            console.error('Failed to load user data:', error);
        }
    }

    renderUserInfo() {
        const userDetails = document.getElementById('userDetails');
        userDetails.innerHTML = `
            <div class="user-detail">
                <strong>Total API Keys</strong>
                ${this.userInfo.totalKeys}
            </div>
            <div class="user-detail">
                <strong>Active Keys</strong>
                ${this.userInfo.activeKeys}
            </div>
            <div class="user-detail">
                <strong>Status</strong>
                <span style="color: #228B22;">✓ Authenticated</span>
            </div>
        `;
    }

    renderApiKeys() {
        const keysList = document.getElementById('keysList');
        
        if (this.apiKeys.length === 0) {
            keysList.innerHTML = `
                <div style="text-align: center; padding: 40px; color: #888;">
                    <div style="font-size: 3rem; margin-bottom: 20px;">🗝️</div>
                    <p>No API keys found. Create your first key to get started!</p>
                    <button class="btn btn-primary" onclick="crusontAPI.showCreateKeyModal()" style="margin-top: 15px;">
                        <span class="btn-text">Create Your First Key</span>
                        <span class="btn-icon">✨</span>
                    </button>
                </div>
            `;
            return;
        }

        // Apply filtering and sorting
        let filteredKeys = this.getFilteredKeys();
        let sortedKeys = this.getSortedKeys(filteredKeys);

        keysList.innerHTML = sortedKeys.map(key => `
            <div class="key-item" data-key-id="${key.id}">
                <div class="key-info">
                    <div class="key-name">${this.escapeHtml(key.name)}</div>
                    <div class="key-value">${key.key}</div>
                    <div class="key-meta">
                        <span class="meta-item">
                            <span class="meta-icon">📅</span>
                            Created: ${new Date(key.created_at * 1000).toLocaleDateString()}
                        </span>
                        <span class="meta-item">
                            <span class="meta-icon">${key.last_used ? '🕒' : '⏸️'}</span>
                            ${key.last_used ? `Last used: ${new Date(key.last_used * 1000).toLocaleDateString()}` : 'Never used'}
                        </span>
                    </div>
                </div>
                <div class="key-actions">
                    <button class="btn btn-small" onclick="crusontAPI.copyToClipboard('${key.key}')" title="Copy API Key">
                        <span class="btn-text">📋 Copy</span>
                    </button>
                    <button class="btn btn-small btn-danger" onclick="crusontAPI.deleteApiKey('${key.id}')" title="Delete API Key">
                        <span class="btn-text">🗑️ Delete</span>
                    </button>
                </div>
            </div>
        `).join('');

        // Add animation to key items
        setTimeout(() => {
            const keyItems = keysList.querySelectorAll('.key-item');
            keyItems.forEach((item, index) => {
                item.style.opacity = '0';
                item.style.transform = 'translateY(20px)';
                setTimeout(() => {
                    item.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
                    item.style.opacity = '1';
                    item.style.transform = 'translateY(0)';
                }, index * 100);
            });
        }, 50);
    }

    getFilteredKeys() {
        const filter = document.getElementById('filterKeys').value;
        
        switch(filter) {
            case 'active':
                return this.apiKeys.filter(key => key.last_used);
            case 'unused':
                return this.apiKeys.filter(key => !key.last_used);
            default:
                return this.apiKeys;
        }
    }

    getSortedKeys(keys) {
        const sortBy = document.getElementById('sortKeys').value;
        
        return [...keys].sort((a, b) => {
            switch(sortBy) {
                case 'name':
                    return a.name.localeCompare(b.name);
                case 'created':
                    return b.created_at - a.created_at;
                case 'last_used':
                    const aUsed = a.last_used || 0;
                    const bUsed = b.last_used || 0;
                    return bUsed - aUsed;
                default:
                    return 0;
            }
        });
    }

    showCreateKeyModal() {
        document.getElementById('createKeyModal').classList.remove('hidden');
        document.getElementById('keyName').focus();
    }

    hideCreateKeyModal() {
        document.getElementById('createKeyModal').classList.add('hidden');
        document.getElementById('keyName').value = '';
    }

    async createApiKey() {
        const keyName = document.getElementById('keyName').value.trim();
        if (!keyName) {
            alert('Please enter a key name');
            return;
        }

        try {
            const response = await fetch(`${this.baseURL}/v1/keys`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.apiKey}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ name: keyName })
            });

            if (response.ok) {
                const newKey = await response.json();
                this.hideCreateKeyModal();
                this.showNewKeyModal(newKey);
                await this.loadUserData(); // Refresh the keys list
            } else {
                const error = await response.json();
                alert(`Failed to create API key: ${error.detail || 'Unknown error'}`);
            }
        } catch (error) {
            alert(`Failed to create API key: ${error.message}`);
        }
    }

    showNewKeyModal(newKey) {
        document.getElementById('newKeyName').textContent = newKey.name;
        document.getElementById('newKeyValue').textContent = newKey.key;
        document.getElementById('newKeyModal').classList.remove('hidden');
    }

    hideNewKeyModal() {
        document.getElementById('newKeyModal').classList.add('hidden');
    }

    async deleteApiKey(keyId) {
        if (!confirm('Are you sure you want to delete this API key? This action cannot be undone.')) {
            return;
        }

        try {
            const response = await fetch(`${this.baseURL}/v1/keys/${keyId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${this.apiKey}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                this.showStatus('API key deleted successfully', 'success');
                await this.loadUserData(); // Refresh the keys list
            } else {
                const error = await response.json();
                alert(`Failed to delete API key: ${error.detail || 'Unknown error'}`);
            }
        } catch (error) {
            alert(`Failed to delete API key: ${error.message}`);
        }
    }

    copyToClipboard(text) {
        navigator.clipboard.writeText(text).then(() => {
            this.showStatus('API key copied to clipboard!', 'success');
        }).catch(() => {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            this.showStatus('API key copied to clipboard!', 'success');
        });
    }

    copyApiKey() {
        const keyValue = document.getElementById('newKeyValue').textContent;
        this.copyToClipboard(keyValue);
    }

    showDashboard() {
        document.getElementById('dashboard').classList.remove('hidden');
    }

    showStatus(message, type) {
        const status = document.getElementById('authStatus');
        status.textContent = message;
        status.className = `status ${type}`;
        
        // Auto-hide success messages after 3 seconds
        if (type === 'success') {
            setTimeout(() => {
                status.textContent = '';
                status.className = 'status';
            }, 3000);
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize the app when the page loads
let crusontAPI;
document.addEventListener('DOMContentLoaded', () => {
    crusontAPI = new CrusontAPI();
});
