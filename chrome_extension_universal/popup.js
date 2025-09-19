/**
 * Universal NSFW Filter Popup JavaScript
 * Manages extension settings and statistics display
 * Superior University - AI Research Division
 */

class UniversalNSFWPopup {
    constructor() {
        this.currentTab = null;
        this.globalStats = {};
        this.currentStats = {};
        this.refreshInterval = null;
        
        this.initializePopup();
    }
    
    async initializePopup() {
        try {
            // Check if chrome APIs are available
            if (typeof chrome === 'undefined' || !chrome.tabs) {
                throw new Error('Chrome APIs not available');
            }
            
            // Get current tab
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            this.currentTab = tab;
            
            // Initialize UI elements
            this.initializeEventListeners();
            
            // Load initial data
            await this.loadSettings();
            await this.updateUI();
            
            // Start auto-refresh
            this.startAutoRefresh();
            
            // Hide loading and show content
            document.getElementById('loading').style.display = 'none';
            document.getElementById('main-content').style.display = 'block';
            
        } catch (error) {
            this.showError('Failed to initialize popup: ' + error.message);
            console.error('Popup initialization error:', error);
            
            // Hide loading even on error
            document.getElementById('loading').style.display = 'none';
            document.getElementById('main-content').style.display = 'block';
        }
    }
    
    initializeEventListeners() {
        // Enable/Disable toggle
        const enableToggle = document.getElementById('enableToggle');
        enableToggle.addEventListener('change', async (e) => {
            await this.toggleEnabled(e.target.checked);
        });
        
        // Settings inputs
        const frameRateInput = document.getElementById('frameRateInput');
        frameRateInput.addEventListener('change', async (e) => {
            await this.updateSetting('frameRate', parseInt(e.target.value));
        });
        
        const sensitivityInput = document.getElementById('sensitivityInput');
        sensitivityInput.addEventListener('change', async (e) => {
            await this.updateSetting('sensitivity', parseFloat(e.target.value));
        });
        
        const qualityInput = document.getElementById('qualityInput');
        qualityInput.addEventListener('change', async (e) => {
            await this.updateSetting('compressionQuality', parseFloat(e.target.value));
        });
        
        // Image blur settings
        document.getElementById('enableImageBlur').addEventListener('change', async (e) => {
            await this.updateImageBlurSetting('enabled', e.target.checked);
        });
        
        document.getElementById('blurIntensityInput').addEventListener('input', (e) => {
            document.getElementById('blurIntensityValue').textContent = e.target.value + 'px';
        });
        
        document.getElementById('blurIntensityInput').addEventListener('change', async (e) => {
            await this.updateImageBlurSetting('blurIntensity', parseInt(e.target.value));
        });
        
        document.getElementById('imageSensitivityInput').addEventListener('input', (e) => {
            document.getElementById('imageSensitivityValue').textContent = e.target.value;
        });
        
        document.getElementById('imageSensitivityInput').addEventListener('change', async (e) => {
            await this.updateImageBlurSetting('sensitivity', parseFloat(e.target.value));
        });
        
        document.getElementById('blurThumbnails').addEventListener('change', async (e) => {
            await this.updateImageBlurSetting('blurThumbnails', e.target.checked);
        });
        
        document.getElementById('blurProfilePictures').addEventListener('change', async (e) => {
            await this.updateImageBlurSetting('blurProfilePictures', e.target.checked);
        });
        
        document.getElementById('blurAds').addEventListener('change', async (e) => {
            await this.updateImageBlurSetting('blurAds', e.target.checked);
        });
        
        document.getElementById('blurAllImages').addEventListener('change', async (e) => {
            await this.updateImageBlurSetting('blurAllImages', e.target.checked);
        });
        
        // Control buttons
        document.getElementById('refreshBtn').addEventListener('click', () => {
            this.refreshCurrentTab();
        });
        
        document.getElementById('helpBtn').addEventListener('click', () => {
            chrome.tabs.create({ 
                url: 'http://localhost:5000/help' 
            });
        });
    }
    
    async loadSettings() {
        try {
            if (!chrome.storage || !chrome.storage.sync) {
                console.warn('Chrome storage API not available, using defaults');
                return;
            }
            
            const settings = await chrome.storage.sync.get([
                'enabled', 'frameRate', 'sensitivity', 'compressionQuality', 'apiEndpoint',
                'imageBlurSettings'
            ]);
            
            // Update UI with current settings
            document.getElementById('enableToggle').checked = settings.enabled !== false;
            document.getElementById('frameRateInput').value = settings.frameRate || 15;
            document.getElementById('sensitivityInput').value = settings.sensitivity || 0.5;
            document.getElementById('qualityInput').value = settings.compressionQuality || 0.7;
            
            // Load image blur settings
            const imageSettings = settings.imageBlurSettings || {
                enabled: true,
                blurIntensity: 10,
                sensitivity: 0.6,
                blurThumbnails: true,
                blurProfilePictures: true,
                blurAds: false,
                blurAllImages: false
            };
            
            document.getElementById('enableImageBlur').checked = imageSettings.enabled;
            document.getElementById('blurIntensityInput').value = imageSettings.blurIntensity;
            document.getElementById('imageSensitivityInput').value = imageSettings.sensitivity;
            document.getElementById('blurThumbnails').checked = imageSettings.blurThumbnails;
            document.getElementById('blurProfilePictures').checked = imageSettings.blurProfilePictures;
            document.getElementById('blurAds').checked = imageSettings.blurAds;
            document.getElementById('blurAllImages').checked = imageSettings.blurAllImages;
            
            // Update display values
            document.getElementById('blurIntensityValue').textContent = imageSettings.blurIntensity + 'px';
            document.getElementById('imageSensitivityValue').textContent = imageSettings.sensitivity;
            
        } catch (error) {
            console.error('Failed to load settings:', error);
        }
    }
    
    async updateUI() {
        try {
            // Update website information
            await this.updateWebsiteInfo();
            
            // Update global statistics
            await this.updateGlobalStats();
            
            // Update current tab statistics
            await this.updateCurrentTabStats();
            
            // Update status
            this.updateStatus();
            
        } catch (error) {
            console.error('Failed to update UI:', error);
            this.showError('Failed to update display: ' + error.message);
        }
    }
    
    async updateWebsiteInfo() {
        if (!this.currentTab) return;
        
        const websiteName = document.getElementById('websiteName');
        const websiteStatus = document.getElementById('websiteStatus');
        
        try {
            const hostname = new URL(this.currentTab.url).hostname;
            websiteName.textContent = hostname;
            
            // Check if this is a supported website
            const supportedSites = [
                'youtube.com', 'tiktok.com', 'instagram.com', 'twitch.tv',
                'twitter.com', 'x.com', 'facebook.com', 'reddit.com',
                'linkedin.com', 'vimeo.com', 'dailymotion.com'
            ];
            
            const isSupported = supportedSites.some(site => hostname.includes(site));
            const hasVideo = await this.checkForVideoContent();
            
            if (this.shouldSkipWebsite(this.currentTab.url)) {
                websiteStatus.textContent = '⚠️ Extension pages not supported';
                websiteStatus.style.color = '#ffa726';
            } else if (hasVideo) {
                websiteStatus.textContent = '✅ Video content detected - Active monitoring';
                websiteStatus.style.color = '#4caf50';
            } else if (isSupported) {
                websiteStatus.textContent = '🔍 Supported site - Waiting for video content';
                websiteStatus.style.color = '#2196f3';
            } else {
                websiteStatus.textContent = '🌐 Universal support - All video content monitored';
                websiteStatus.style.color = '#9c27b0';
            }
            
        } catch (error) {
            websiteName.textContent = 'Unknown website';
            websiteStatus.textContent = '❌ Unable to analyze website';
            websiteStatus.style.color = '#f44336';
        }
    }
    
    async updateGlobalStats() {
        try {
            // Get global statistics from background script
            const response = await chrome.runtime.sendMessage({ type: 'GET_GLOBAL_STATS' });
            this.globalStats = response;
            
            // Update global stats display
            document.getElementById('activeFrames').textContent = this.globalStats.activeProcessors || 0;
            document.getElementById('processedFrames').textContent = this.globalStats.totalFramesProcessed || 0;
            
        } catch (error) {
            console.error('Failed to get global stats:', error);
        }
    }
    
    async updateCurrentTabStats() {
        if (!this.currentTab) return;
        
        try {
            // Get statistics from current tab's content script
            const response = await chrome.tabs.sendMessage(this.currentTab.id, { 
                type: 'GET_STATS' 
            });
            
            if (response) {
                this.currentStats = response;
                
                // Update current tab stats
                document.getElementById('avgLatency').textContent = response.avgLatency || '0ms';
                document.getElementById('successRate').textContent = response.successRate || '0%';
            }
            
        } catch (error) {
            // Content script might not be loaded yet
            console.log('Content script not available for current tab');
            
            // Try to inject content script
            try {
                await chrome.scripting.executeScript({
                    target: { tabId: this.currentTab.id },
                    files: ['content_script.js']
                });
                
                // Retry getting stats after injection
                setTimeout(() => this.updateCurrentTabStats(), 1000);
                
            } catch (injectionError) {
                console.log('Cannot inject content script:', injectionError.message);
            }
        }
    }
    
    updateStatus() {
        const statusBadge = document.getElementById('statusBadge');
        const enableToggle = document.getElementById('enableToggle');
        
        const isEnabled = enableToggle.checked;
        const hasActiveProcessors = this.globalStats.activeProcessors > 0;
        
        if (!isEnabled) {
            statusBadge.textContent = 'DISABLED';
            statusBadge.className = 'status-badge inactive';
        } else if (hasActiveProcessors) {
            statusBadge.textContent = 'ACTIVE';
            statusBadge.className = 'status-badge active';
        } else {
            statusBadge.textContent = 'STANDBY';
            statusBadge.className = 'status-badge';
            statusBadge.style.background = '#ff9800';
        }
    }
    
    async toggleEnabled(enabled) {
        try {
            // Update global setting
            await chrome.storage.sync.set({ enabled: enabled });
            
            // Notify background script
            await chrome.runtime.sendMessage({ 
                type: 'TOGGLE_GLOBAL_ENABLE' 
            });
            
            // Update current tab if possible
            if (this.currentTab) {
                try {
                    await chrome.tabs.sendMessage(this.currentTab.id, { 
                        type: 'SET_ENABLED', 
                        enabled: enabled 
                    });
                } catch (error) {
                    // Tab might not have content script, that's okay
                }
            }
            
            // Update UI
            setTimeout(() => this.updateUI(), 500);
            
        } catch (error) {
            console.error('Failed to toggle enabled state:', error);
            this.showError('Failed to update settings');
        }
    }
    
    async updateSetting(key, value) {
        try {
            // Save to storage
            await chrome.storage.sync.set({ [key]: value });
            
            // Update current tab if possible
            if (this.currentTab) {
                try {
                    await chrome.tabs.sendMessage(this.currentTab.id, { 
                        type: 'UPDATE_SETTINGS', 
                        settings: { [key]: value }
                    });
                } catch (error) {
                    // Tab might not have content script
                }
            }
            
            console.log(`Updated ${key} to ${value}`);
            
        } catch (error) {
            console.error(`Failed to update ${key}:`, error);
            this.showError(`Failed to update ${key}`);
        }
    }
    
    async updateImageBlurSetting(key, value) {
        try {
            // Get current image blur settings
            const result = await chrome.storage.sync.get(['imageBlurSettings']);
            const imageBlurSettings = result.imageBlurSettings || {
                enabled: true,
                blurIntensity: 10,
                sensitivity: 0.6,
                blurThumbnails: true,
                blurProfilePictures: true,
                blurAds: false,
                blurAllImages: false
            };
            
            // Update the specific setting
            imageBlurSettings[key] = value;
            
            // Save to storage
            await chrome.storage.sync.set({ imageBlurSettings });
            
            // Update current tab if possible
            if (this.currentTab) {
                try {
                    await chrome.tabs.sendMessage(this.currentTab.id, { 
                        type: 'UPDATE_SETTINGS', 
                        settings: { imageBlurSettings }
                    });
                } catch (error) {
                    // Tab might not have content script
                }
            }
            
            console.log(`Updated image blur ${key} to ${value}`);
            
        } catch (error) {
            console.error(`Failed to update image blur ${key}:`, error);
            this.showError(`Failed to update image blur ${key}`);
        }
    }
    
    async refreshCurrentTab() {
        if (!this.currentTab) return;
        
        try {
            // Send refresh message to current tab
            await chrome.tabs.sendMessage(this.currentTab.id, { 
                type: 'RESTART_PROCESSOR' 
            });
            
            // Update UI after refresh
            setTimeout(() => this.updateUI(), 1000);
            
        } catch (error) {
            // If content script not available, reload the tab
            chrome.tabs.reload(this.currentTab.id);
        }
    }
    
    async checkForVideoContent() {
        if (!this.currentTab) return false;
        
        try {
            const result = await chrome.scripting.executeScript({
                target: { tabId: this.currentTab.id },
                func: () => {
                    const videos = document.querySelectorAll('video');
                    return videos.length > 0;
                }
            });
            
            return result[0]?.result || false;
            
        } catch (error) {
            return false;
        }
    }
    
    shouldSkipWebsite(url) {
        if (!url) return true;
        
        const skipPatterns = [
            /^chrome:\/\//,
            /^chrome-extension:\/\//,
            /^moz-extension:\/\//,
            /^edge:\/\//,
            /^about:/
        ];
        
        return skipPatterns.some(pattern => pattern.test(url));
    }
    
    startAutoRefresh() {
        // Refresh stats every 3 seconds
        this.refreshInterval = setInterval(() => {
            this.updateUI();
        }, 3000);
    }
    
    showError(message) {
        const errorDisplay = document.getElementById('errorDisplay');
        errorDisplay.textContent = message;
        errorDisplay.style.display = 'block';
        
        // Hide error after 5 seconds
        setTimeout(() => {
            errorDisplay.style.display = 'none';
        }, 5000);
    }
    
    cleanup() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
    }
}

// Initialize popup when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const popup = new UniversalNSFWPopup();
    
    // Cleanup when popup is closed
    window.addEventListener('beforeunload', () => {
        popup.cleanup();
    });
});

// Handle popup close
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        // Popup is being closed or hidden
        // Perform any necessary cleanup
    }
});
