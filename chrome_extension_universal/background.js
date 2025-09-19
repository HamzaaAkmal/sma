/**
 * Universal Chrome Extension Background Service
 * Manages extension lifecycle and cross-tab communication
 * Superior University - NSFW Detection System
 */

class UniversalNSFWBackground {
    constructor() {
        this.activeTabProcessors = new Map();
        this.stats = {
            totalTabsProcessed: 0,
            activeProcessors: 0,
            totalFramesProcessed: 0,
            startTime: Date.now()
        };
        
        this.initializeBackground();
    }
    
    initializeBackground() {
        console.log('🚀 Universal NSFW Filter Background Service started');
        
        try {
            // Handle extension installation/update
            chrome.runtime.onInstalled.addListener((details) => {
                this.handleInstallation(details);
            });
            
            // Handle tab updates
            chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
                this.handleTabUpdate(tabId, changeInfo, tab);
            });
            
            // Handle tab removal
            chrome.tabs.onRemoved.addListener((tabId) => {
                this.handleTabRemoval(tabId);
            });
            
            // Handle messages from content scripts and popup
            chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
                this.handleMessage(request, sender, sendResponse);
                return true; // Keep message channel open for async responses
            });
            
            // Handle extension startup
            chrome.runtime.onStartup.addListener(() => {
                console.log('🔄 Extension startup detected');
                this.reinitializeAllTabs();
            });
            
            // Setup webRequest interception for pre-load image blurring
            this.setupWebRequestInterception();
            
            // Periodic cleanup
            setInterval(() => {
                this.cleanupInactiveTabs();
            }, 60000); // Every minute
            
            // Initialize extension badge
            this.updateBadge();
            
        } catch (error) {
            console.error('Failed to initialize background service:', error);
        }
    }
    
    async handleInstallation(details) {
        if (details.reason === 'install') {
            console.log('🎉 Universal NSFW Filter installed');
            
            // Set default settings
            await chrome.storage.sync.set({
                enabled: true,
                apiEndpoint: 'http://localhost:5000/process-frame-stream',
                frameRate: 15,
                compressionQuality: 0.7,
                sensitivity: 0.5,
                firstRun: true
            });
            
            // Open welcome page
            chrome.tabs.create({
                url: chrome.runtime.getURL('welcome.html')
            });
            
        } else if (details.reason === 'update') {
            console.log('🔄 Universal NSFW Filter updated');
            
            // Check if we need to migrate settings
            const settings = await chrome.storage.sync.get();
            if (!settings.apiEndpoint) {
                await chrome.storage.sync.set({
                    apiEndpoint: 'http://localhost:5000/process-frame-stream'
                });
            }
        }
    }
    
    setupWebRequestInterception() {
        console.log('🔍 Setting up webRequest interception for pre-load image blurring');
        
        // Note: In Manifest V3, we cannot use blocking webRequest listeners
        // Instead, we'll rely on content script processing for instant blurring
        
        // Intercept image requests (non-blocking)
        chrome.webRequest.onBeforeRequest.addListener(
            (details) => {
                console.log('🖼️ Intercepting image request:', details.url);
                // For now, just log the request
                return {};
            },
            {
                urls: ["<all_urls>"],
                types: ["image"]
            }
        );
        
        console.log('✅ WebRequest interception setup (non-blocking mode)');
    }
    
    async handleTabUpdate(tabId, changeInfo, tab) {
        // Only process when tab is completely loaded
        if (changeInfo.status !== 'complete') return;
        
        // Skip certain URLs
        if (this.shouldSkipTab(tab)) return;
        
        // Check if extension is enabled
        const settings = await chrome.storage.sync.get(['enabled']);
        if (settings.enabled === false) return;
        
        try {
            // Inject content script if not already injected
            await this.ensureContentScriptInjected(tabId);
            
            // Track this tab
            this.activeTabProcessors.set(tabId, {
                url: tab.url,
                title: tab.title,
                startTime: Date.now(),
                lastActivity: Date.now()
            });
            
            this.stats.totalTabsProcessed++;
            this.updateBadge();
            
            console.log(`📱 Tab ${tabId} ready for processing: ${tab.url}`);
            
        } catch (error) {
            console.error(`❌ Failed to setup tab ${tabId}:`, error);
        }
    }
    
    handleTabRemoval(tabId) {
        if (this.activeTabProcessors.has(tabId)) {
            console.log(`🗑️ Removed tab ${tabId} from tracking`);
            this.activeTabProcessors.delete(tabId);
            this.updateBadge();
        }
    }
    
    async handleMessage(request, sender, sendResponse) {
        try {
            switch (request.type) {
                case 'GET_GLOBAL_STATS':
                    sendResponse(await this.getGlobalStats());
                    break;
                    
                case 'GET_ACTIVE_TABS':
                    sendResponse(Array.from(this.activeTabProcessors.entries()));
                    break;
                    
                case 'TOGGLE_GLOBAL_ENABLE':
                    await this.toggleGlobalEnable();
                    sendResponse({ success: true });
                    break;
                    
                case 'UPDATE_TAB_ACTIVITY':
                    if (sender.tab) {
                        this.updateTabActivity(sender.tab.id, request.data);
                    }
                    sendResponse({ success: true });
                    break;
                    
                case 'REPORT_FRAME_PROCESSED':
                    this.stats.totalFramesProcessed++;
                    if (sender.tab) {
                        this.updateTabActivity(sender.tab.id, { lastFrameTime: Date.now() });
                    }
                    sendResponse({ success: true });
                    break;
                    
                default:
                    sendResponse({ error: 'Unknown message type' });
            }
        } catch (error) {
            console.error('Error handling message:', error);
            sendResponse({ error: error.message });
        }
    }
    
    shouldSkipTab(tab) {
        if (!tab.url) return true;
        
        const skipPatterns = [
            /^chrome:\/\//,
            /^chrome-extension:\/\//,
            /^moz-extension:\/\//,
            /^edge:\/\//,
            /^about:/,
            /^file:\/\//,
            /^data:/,
            /^blob:/,
            /^chrome-error:\/\//,
            /^error:/,
            /^https?:\/\/.*\/.*\?.*error.*/,
            /^https?:\/\/.*\/.*\?.*404.*/,
            /^https?:\/\/.*\/.*\?.*403.*/,
            /^https?:\/\/.*\/.*\?.*500.*/
        ];
        
        // Skip if URL matches skip patterns
        if (skipPatterns.some(pattern => pattern.test(tab.url))) {
            return true;
        }
        
        // Skip if tab is showing an error page
        if (tab.title && (
            tab.title.includes('Error') ||
            tab.title.includes('404') ||
            tab.title.includes('403') ||
            tab.title.includes('500') ||
            tab.title.includes('Not Found') ||
            tab.title.includes('Forbidden') ||
            tab.title.includes('Server Error')
        )) {
            console.log(`⏭️ Skipping error page: ${tab.title}`);
            return true;
        }
        
        return false;
    }
    
    async ensureContentScriptInjected(tabId) {
        try {
            // First check if we can access the tab
            const tab = await chrome.tabs.get(tabId);
            if (!tab || tab.status !== 'complete') {
                console.log(`⏳ Tab ${tabId} not ready, skipping injection`);
                return;
            }
            
            // Check if content script is already injected
            try {
                const response = await chrome.tabs.sendMessage(tabId, { type: 'PING' });
                if (response?.pong) {
                    return; // Already injected
                }
            } catch (error) {
                // Content script not injected, continue with injection
            }
            
            // Check if the script is already running by looking for our global flag
            try {
                const results = await chrome.scripting.executeScript({
                    target: { tabId: tabId },
                    func: () => window.UniversalNSFWFilterLoaded || false
                });
                
                if (results[0]?.result === true) {
                    console.log(`✅ Content script already loaded in tab ${tabId}`);
                    return;
                }
            } catch (scriptError) {
                console.warn(`⚠️ Could not check script status in tab ${tabId}:`, scriptError.message);
                // Continue with injection attempt
            }
            
            // Inject content script
            await chrome.scripting.executeScript({
                target: { tabId: tabId },
                files: ['content_script.js']
            });
            
            console.log(`✅ Content script injected into tab ${tabId}`);
            
        } catch (error) {
            // Don't throw error for injection failures, just log and continue
            console.warn(`⚠️ Failed to inject content script into tab ${tabId}:`, error.message);
            
            // If it's an error page or frame error, don't retry
            if (error.message.includes('error page') || 
                error.message.includes('Frame with ID') ||
                error.message.includes('Cannot access')) {
                console.log(`⏭️ Skipping injection for problematic tab ${tabId}`);
                return;
            }
            
            // For other errors, we could retry, but for now just log
        }
    }
    
    async reinitializeAllTabs() {
        try {
            const tabs = await chrome.tabs.query({});
            const enabledSettings = await chrome.storage.sync.get(['enabled']);
            
            if (enabledSettings.enabled === false) {
                console.log('🔇 Extension disabled, skipping tab reinitialization');
                return;
            }
            
            for (const tab of tabs) {
                if (!this.shouldSkipTab(tab)) {
                    await this.ensureContentScriptInjected(tab.id);
                }
            }
            
            console.log(`🔄 Reinitialized ${tabs.length} tabs`);
            
        } catch (error) {
            console.error('Error reinitializing tabs:', error);
        }
    }
    
    async toggleGlobalEnable() {
        const settings = await chrome.storage.sync.get(['enabled']);
        const newState = !settings.enabled;
        
        await chrome.storage.sync.set({ enabled: newState });
        
        if (newState) {
            await this.reinitializeAllTabs();
        } else {
            // Send disable message to all tabs
            const tabs = await chrome.tabs.query({});
            for (const tab of tabs) {
                if (!this.shouldSkipTab(tab)) {
                    try {
                        await chrome.tabs.sendMessage(tab.id, { 
                            type: 'SET_ENABLED', 
                            enabled: false 
                        });
                    } catch (error) {
                        // Tab might not have content script, ignore
                    }
                }
            }
        }
        
        this.updateBadge();
        console.log(`🔄 Global enable state changed to: ${newState}`);
    }
    
    updateTabActivity(tabId, data) {
        const tabInfo = this.activeTabProcessors.get(tabId);
        if (tabInfo) {
            Object.assign(tabInfo, data, { lastActivity: Date.now() });
            this.activeTabProcessors.set(tabId, tabInfo);
        }
    }
    
    async cleanupInactiveTabs() {
        const cutoffTime = Date.now() - (5 * 60 * 1000); // 5 minutes
        
        for (const [tabId, tabInfo] of this.activeTabProcessors.entries()) {
            if (tabInfo.lastActivity < cutoffTime) {
                try {
                    await chrome.tabs.get(tabId);
                    // Tab still exists but inactive, keep it but mark as stale
                    tabInfo.stale = true;
                } catch (error) {
                    // Tab no longer exists, remove it
                    this.activeTabProcessors.delete(tabId);
                    console.log(`🧹 Cleaned up inactive tab ${tabId}`);
                }
            }
        }
        
        this.updateBadge();
    }
    
    async updateBadge() {
        const settings = await chrome.storage.sync.get(['enabled']);
        const activeCount = this.activeTabProcessors.size;
        
        if (settings.enabled === false) {
            chrome.action.setBadgeText({ text: 'OFF' });
            chrome.action.setBadgeBackgroundColor({ color: '#FF0000' });
        } else if (activeCount > 0) {
            chrome.action.setBadgeText({ text: activeCount.toString() });
            chrome.action.setBadgeBackgroundColor({ color: '#00AA00' });
        } else {
            chrome.action.setBadgeText({ text: '' });
        }
    }
    
    async getGlobalStats() {
        const runtime = (Date.now() - this.stats.startTime) / 1000;
        const settings = await chrome.storage.sync.get();
        
        return {
            ...this.stats,
            activeProcessors: this.activeTabProcessors.size,
            runtime: Math.round(runtime) + 's',
            enabled: settings.enabled !== false,
            apiEndpoint: settings.apiEndpoint || 'http://localhost:5000/process-frame-stream',
            version: chrome.runtime.getManifest().version
        };
    }
}

// Initialize background service
let backgroundService = null;

// Wait for service worker to be ready before initializing
if (typeof chrome !== 'undefined' && chrome.runtime && chrome.runtime.id) {
    backgroundService = new UniversalNSFWBackground();
} else {
    // Retry initialization after a short delay
    setTimeout(() => {
        backgroundService = new UniversalNSFWBackground();
    }, 100);
}

// Handle context menu creation
chrome.runtime.onInstalled.addListener(() => {
    // Create context menu for quick toggle
    try {
        chrome.contextMenus.create({
            id: 'toggle-nsfw-filter',
            title: 'Toggle NSFW Filter',
            contexts: ['video']
        });
        
        chrome.contextMenus.create({
            id: 'nsfw-filter-settings',
            title: 'NSFW Filter Settings',
            contexts: ['action']
        });
    } catch (error) {
        console.error('Failed to create context menus:', error);
    }
});

// Handle context menu clicks
chrome.contextMenus.onClicked.addListener(async (info, tab) => {
    try {
        if (!backgroundService) {
            console.warn('Background service not yet initialized');
            return;
        }
        
        switch (info.menuItemId) {
            case 'toggle-nsfw-filter':
                await backgroundService.toggleGlobalEnable();
                break;
                
            case 'nsfw-filter-settings':
                if (chrome.runtime.openOptionsPage) {
                    chrome.runtime.openOptionsPage();
                } else {
                    // Fallback for older Chrome versions
                    chrome.tabs.create({ url: chrome.runtime.getURL('popup.html') });
                }
                break;
        }
    } catch (error) {
        console.error('Context menu click error:', error);
    }
});

// Handle alarms for periodic tasks
chrome.alarms.onAlarm.addListener((alarm) => {
    try {
        if (!backgroundService) {
            console.warn('Background service not yet initialized for alarm:', alarm.name);
            return;
        }
        
        switch (alarm.name) {
            case 'cleanup':
                backgroundService.cleanupInactiveTabs();
                break;
        }
    } catch (error) {
        console.error('Alarm handler error:', error);
    }
});

// Set up periodic cleanup alarm
try {
    chrome.alarms.create('cleanup', { periodInMinutes: 5 });
} catch (error) {
    console.error('Failed to create cleanup alarm:', error);
}

console.log('🌐 Universal NSFW Filter Background Service initialized');
