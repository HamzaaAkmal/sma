/**
 * Test page JavaScript for Universal NSFW Filter
 * Provides testing functionality and real-time monitoring
 */

let logLines = [];

function log(message) {
    const timestamp = new Date().toLocaleTimeString();
    const logLine = `[${timestamp}] ${message}`;
    logLines.push(logLine);
    
    // Keep only last 20 log lines
    if (logLines.length > 20) {
        logLines = logLines.slice(-20);
    }
    
    document.getElementById('logContent').innerHTML = logLines.join('<br>');
    console.log(logLine);
}

function playVideo() {
    const video = document.getElementById('testVideo');
    video.play().then(() => {
        log('✅ Video started playing');
    }).catch(error => {
        log('❌ Error playing video: ' + error.message);
    });
}

function pauseVideo() {
    const video = document.getElementById('testVideo');
    video.pause();
    log('⏸️ Video paused');
}

function clearLog() {
    logLines = [];
    document.getElementById('logContent').innerHTML = 'Log cleared...';
}

function checkExtension() {
    log('🔍 Checking for Universal NSFW Filter...');
    
    // Check if the extension has injected its global object
    if (window.UniversalNSFWFilter) {
        log('✅ Extension detected and active');
        
        const stats = window.UniversalNSFWFilter.getStats();
        log(`📊 Stats: ${JSON.stringify(stats, null, 2)}`);
        
        document.getElementById('statusText').textContent = 'Extension Active ✅';
        document.getElementById('extensionStatus').style.background = '#d4edda';
        document.getElementById('extensionStatus').style.color = '#155724';
        
    } else {
        log('❌ Extension not detected');
        document.getElementById('statusText').textContent = 'Extension Not Found ❌';
        document.getElementById('extensionStatus').style.background = '#f8d7da';
        document.getElementById('extensionStatus').style.color = '#721c24';
    }
}

// Auto-check extension status on page load
document.addEventListener('DOMContentLoaded', () => {
    log('🌐 Test page loaded');
    
    // Add event listeners to buttons
    document.getElementById('playBtn').addEventListener('click', playVideo);
    document.getElementById('pauseBtn').addEventListener('click', pauseVideo);
    document.getElementById('checkBtn').addEventListener('click', checkExtension);
    document.getElementById('clearBtn').addEventListener('click', clearLog);
    
    setTimeout(() => {
        checkExtension();
    }, 2000);
    
    // Check for video processing activity
    setInterval(() => {
        if (window.UniversalNSFWFilter) {
            const processor = window.UniversalNSFWFilter.getProcessor();
            if (processor && processor.stats) {
                const stats = processor.stats;
                if (stats.totalFrames > 0) {
                    log(`📊 Frames processed: ${stats.processedFrames}/${stats.totalFrames}, Success: ${stats.successRate || 'N/A'}`);
                }
            }
        }
    }, 10000); // Check every 10 seconds
    
    // Listen for video events
    const video = document.getElementById('testVideo');
    
    video.addEventListener('loadstart', () => log('📼 Video load started'));
    video.addEventListener('loadeddata', () => log('📼 Video data loaded'));
    video.addEventListener('canplay', () => log('📼 Video can start playing'));
    video.addEventListener('play', () => log('▶️ Video play event'));
    video.addEventListener('pause', () => log('⏸️ Video pause event'));
    video.addEventListener('timeupdate', () => {
        // Log time updates occasionally
        if (Math.floor(video.currentTime) % 5 === 0 && video.currentTime > 0) {
            log(`⏰ Video time: ${Math.floor(video.currentTime)}s`);
        }
    });
    
    log('🚀 Test environment initialized');
});
