/**
 * Welcome page JavaScript for Universal NSFW Filter
 * Handles extension setup and initial configuration
 */

// Check extension status
document.addEventListener('DOMContentLoaded', async () => {
    try {
        // Check if extension is properly installed
        const settings = await chrome.storage.sync.get(['enabled', 'firstRun']);
        
        if (settings.firstRun !== false) {
            // Mark first run as complete
            await chrome.storage.sync.set({ firstRun: false });
        }
        
        // Test API connectivity
        try {
            const response = await fetch('http://localhost:5000/health', {
                method: 'GET',
                timeout: 5000
            });
            
            if (response.ok) {
                document.getElementById('extensionStatus').innerHTML = `
                    <strong>✅ Extension and local API server are both operational!</strong><br>
                    Connected to local Flask server at localhost:5000. Ready for real-time NSFW detection.
                `;
            } else {
                throw new Error('API server not responding');
            }
        } catch (apiError) {
            document.getElementById('extensionStatus').innerHTML = `
                <strong>⚠️ Extension installed, but local API server is not reachable.</strong><br>
                Please start your Flask server on localhost:5000 for full functionality.
            `;
            document.getElementById('extensionStatus').className = 'status-check error';
        }
        
    } catch (error) {
        console.error('Welcome page initialization error:', error);
    }
});

// Button event listeners
document.getElementById('openPopup').addEventListener('click', (e) => {
    e.preventDefault();
    // Open extension popup by clicking the action
    chrome.action.openPopup?.() || alert('Click the extension icon in your toolbar to open settings.');
});

document.getElementById('testExtension').addEventListener('click', (e) => {
    e.preventDefault();
    chrome.tabs.create({ url: 'https://www.youtube.com' });
});

// Auto-close welcome page after 30 seconds unless user is actively engaging
let autoCloseTimer = setTimeout(() => {
    if (confirm('Welcome setup complete! Close this tab and start using the Universal NSFW Filter?')) {
        window.close();
    }
}, 30000);

// Cancel auto-close if user is actively engaging
['scroll', 'click', 'keydown', 'mousemove'].forEach(event => {
    document.addEventListener(event, () => {
        if (autoCloseTimer) {
            clearTimeout(autoCloseTimer);
            autoCloseTimer = null;
        }
    }, { once: true });
});
