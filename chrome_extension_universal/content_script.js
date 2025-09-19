/**
 * Universal Chrome Extension for Real-Time NSFW Video Filtering
 * Works on ALL websites with video content - Superior University
 * Optimized for maximum compatibility and performance
 */

// Prevent multiple script injections using IIFE
(function() {
    'use strict';
    
    // Check if already loaded
    if (window.UniversalNSFWFilterLoaded) {
        console.log('🔄 Universal NSFW Filter already loaded, skipping duplicate injection');
        return;
    }
    window.UniversalNSFWFilterLoaded = true;

class UniversalVideoProcessor {
    constructor() {
        this.apiEndpoint = 'http://localhost:5000/process-frame-stream';
        this.imageApiEndpoint = 'http://localhost:5000/process-image';
        this.isProcessing = false;
        this.frameQueue = [];
        this.imageQueue = [];
        this.maxQueueSize = 2; // Reduce queue size for faster processing
        this.maxImageQueueSize = 5;
        this.processingInterval = null;
        this.imageProcessingInterval = null;
        this.frameRate = 6; // Ultra-optimized frame rate for fastest processing
        this.imageCheckRate = 2; // Check images every 2 seconds
        this.compressionQuality = 0.4; // Lower quality for speed
        this.canvas = null;
        this.ctx = null;
        this.enabled = true;
        
        // Image blur settings - ENABLED BY DEFAULT for instant blur on ALL websites
        this.imageBlurSettings = {
            enabled: true,
            blurThumbnails: true,
            blurProfilePictures: true,
            blurAds: true,
            blurAllImages: true, // Blur ALL images by default for instant protection
            sensitivity: 0.3, // Lower sensitivity for more aggressive detection
            blurIntensity: 25 // Higher blur intensity for instant effect
        };
        
        // Performance tracking
        this.stats = {
            totalFrames: 0,
            processedFrames: 0,
            totalImages: 0,
            processedImages: 0,
            avgLatency: 0,
            errors: 0,
            startTime: Date.now()
        };
        
        // Adaptive settings based on website
        this.websiteSettings = this.detectWebsiteSettings();
        
        // Performance optimization
        this.lastProcessTime = 0;
        this.skipFrames = 0;
        this.activeOverlays = new Map(); // Track active overlays per video
        this.processedImages = new Set(); // Track processed images
        
        this.initializeCanvas();
        this.loadSettings();
        
        // Start image processing immediately for instant blur on ALL websites
        this.startImageProcessingImmediately();
        
        // Start video processing (can be delayed)
        this.startProcessing();
    }
    
    async startImageProcessingImmediately() {
        // Start image processing immediately, don't wait for settings
        console.log('🚀 Starting immediate image processing for instant blur on ALL websites');
        
        // Start image monitoring with high frequency for instant detection
        this.imageProcessingInterval = setInterval(() => {
            this.processImageQueue();
        }, 500); // Check every 500ms for instant processing
        
        // Find and process existing images immediately
        this.scanForImagesImmediately();
        
        // Watch for new images with instant detection
        this.observeImageElementsImmediately();
        
        console.log('✅ Immediate image NSFW detection started - instant blur on ALL websites');
    }
    
    scanForImagesImmediately() {
        console.log('🔍 Scanning for images immediately...');
        
        const imageSelectors = this.getImageSelectors();
        
        imageSelectors.forEach(selector => {
            const images = document.querySelectorAll(selector);
            images.forEach(img => {
                // Process immediately without any checks
                setTimeout(() => this.processImageElementImmediately(img), 10);
            });
        });
        
        // Also scan for background images
        this.scanForBackgroundImages();
    }
    
    scanForBackgroundImages() {
        // Find elements with background images
        const allElements = document.querySelectorAll('*');
        allElements.forEach(element => {
            const style = window.getComputedStyle(element);
            const backgroundImage = style.backgroundImage;
            
            if (backgroundImage && backgroundImage !== 'none' && backgroundImage.includes('url(')) {
                // Create a temporary img element to process the background image
                const tempImg = document.createElement('img');
                const urlMatch = backgroundImage.match(/url\(['"]?(.*?)['"]?\)/);
                if (urlMatch && urlMatch[1]) {
                    tempImg.src = urlMatch[1];
                    tempImg.style.display = 'none';
                    document.body.appendChild(tempImg);
                    
                    setTimeout(() => {
                        this.processImageElementImmediately(tempImg);
                        document.body.removeChild(tempImg);
                    }, 100);
                }
            }
        });
    }
    
    processImageElementImmediately(imgElement) {
        if (!imgElement || this.processedImages.has(imgElement)) {
            return; // Already processed
        }
        
        // Skip very small images (likely icons)
        const rect = imgElement.getBoundingClientRect();
        if (rect.width < 30 || rect.height < 30) {
            return;
        }
        
        // Handle lazy-loaded images for various websites
        const hostname = window.location.hostname.toLowerCase();
        
        // For Google: Handle lazy-loaded images
        if (hostname.includes('google')) {
            const dataSrc = imgElement.getAttribute('data-src') || imgElement.getAttribute('data-lazy-src');
            if (dataSrc && !imgElement.src) {
                // Set src from data attribute for processing
                imgElement.src = dataSrc;
            }
        }
        
        // For YouTube: Handle thumbnail lazy loading
        if (hostname.includes('youtube') || hostname.includes('youtu.be')) {
            const dataThumb = imgElement.getAttribute('data-thumb') || 
                             imgElement.getAttribute('data-lazy') ||
                             imgElement.getAttribute('data-deferred');
            if (dataThumb && !imgElement.src) {
                imgElement.src = dataThumb;
            }
            
            // YouTube thumbnails often use srcset, try to get the best quality
            if (!imgElement.src && imgElement.srcset) {
                const srcsetUrls = imgElement.srcset.split(',').map(s => s.trim().split(' ')[0]);
                if (srcsetUrls.length > 0) {
                    imgElement.src = srcsetUrls[srcsetUrls.length - 1]; // Use highest quality
                }
            }
        }
        
        // General lazy loading patterns
        const lazyAttrs = ['data-src', 'data-lazy-src', 'data-original', 'data-url', 'data-image', 'data-background'];
        for (const attr of lazyAttrs) {
            const lazySrc = imgElement.getAttribute(attr);
            if (lazySrc && !imgElement.src) {
                imgElement.src = lazySrc;
                break;
            }
        }
        
        // Set crossOrigin for cross-origin images
        if (imgElement.src) {
            try {
                const imgUrl = new URL(imgElement.src, window.location.href);
                if (imgUrl.origin !== window.location.origin && !imgElement.crossOrigin) {
                    imgElement.crossOrigin = 'anonymous';
                }
            } catch (e) {
                // Invalid URL, skip crossOrigin setting
            }
        }
        
        // Check if this image type should be processed
        if (!this.shouldProcessImage(imgElement)) {
            return;
        }
        
        // Mark as processed immediately
        this.processedImages.add(imgElement);
        
        // Add to processing queue with high priority for instant blur
        if (this.imageQueue.length < this.maxImageQueueSize * 3) { // Allow even more in queue for Google
            this.imageQueue.unshift({ // Add to front for immediate processing
                element: imgElement,
                timestamp: Date.now(),
                imageId: `img_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
                priority: (hostname.includes('google') || hostname.includes('youtube')) ? 'high' : 'normal'
            });
            
            this.stats.totalImages++;
        }
        
        console.log(`🎯 Immediately queued image for processing: ${imgElement.src || 'lazy-image'}`);
    }
    
    observeImageElementsImmediately() {
        // Use multiple observers for instant detection
        this.setupInstantImageMutationObserver();
        this.setupInstantImageLoadObserver();
        this.setupInstantDynamicContentObserver();
        
        // Scan every second for instant detection
        setInterval(() => {
            this.scanForImagesImmediately();
        }, 1000);
        
        // Also scan on any DOM changes
        let scanTimeout;
        const instantScan = () => {
            clearTimeout(scanTimeout);
            scanTimeout = setTimeout(() => {
                this.scanForImagesImmediately();
            }, 100); // Very short delay for instant detection
        };
        
        // Listen to various events that might add images
        window.addEventListener('scroll', instantScan, { passive: true });
        window.addEventListener('resize', instantScan, { passive: true });
        window.addEventListener('click', instantScan, { passive: true });
        document.addEventListener('DOMContentLoaded', instantScan);
        
        // Listen for dynamic content loading
        ['load', 'DOMContentLoaded', 'readystatechange'].forEach(event => {
            document.addEventListener(event, instantScan);
        });
    }
    
    setupInstantImageMutationObserver() {
        const observer = new MutationObserver((mutations) => {
            let hasNewImages = false;
            
            mutations.forEach((mutation) => {
                // Check for added nodes
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        if (node.tagName === 'IMG') {
                            setTimeout(() => this.processImageElementImmediately(node), 1);
                            hasNewImages = true;
                        } else if (node.querySelectorAll) {
                            const images = node.querySelectorAll('img');
                            images.forEach(img => {
                                setTimeout(() => this.processImageElementImmediately(img), 1);
                            });
                            if (images.length > 0) hasNewImages = true;
                        }
                    }
                });
                
                // Check for attribute changes
                if (mutation.type === 'attributes' &&
                    (mutation.attributeName === 'src' || mutation.attributeName === 'data-src')) {
                    const target = mutation.target;
                    if (target.tagName === 'IMG') {
                        this.processedImages.delete(target);
                        setTimeout(() => this.processImageElementImmediately(target), 1);
                        hasNewImages = true;
                    }
                }
            });
            
            if (hasNewImages) {
                setTimeout(() => {
                    this.scanForImagesImmediately();
                }, 200);
            }
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true,
            attributes: true,
            attributeFilter: ['src', 'data-src', 'style']
        });
        
        this.instantImageMutationObserver = observer;
    }
    
    setupInstantImageLoadObserver() {
        const observer = new MutationObserver(() => {
            setTimeout(() => {
                this.scanForImagesImmediately();
            }, 50);
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
        
        this.instantImageLoadObserver = observer;
    }
    
    setupInstantDynamicContentObserver() {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.addedNodes.length > 0) {
                    const hasImages = Array.from(mutation.addedNodes).some(node => {
                        if (node.nodeType === Node.ELEMENT_NODE) {
                            return node.querySelectorAll && 
                                   (node.querySelectorAll('img').length > 0 ||
                                    node.querySelectorAll('[style*="background-image"]').length > 0);
                        }
                        return false;
                    });
                    
                    if (hasImages) {
                        setTimeout(() => {
                            this.scanForImagesImmediately();
                        }, 10);
                    }
                }
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
        
        this.instantDynamicContentObserver = observer;
    }
    
    detectWebsiteSettings() {
        const hostname = window.location.hostname.toLowerCase();
        
        // Ultra-optimized settings for different websites - maximum speed focus
        if (hostname.includes('youtube')) {
            return { frameRate: 5, quality: 0.25, queueSize: 1 };
        } else if (hostname.includes('tiktok')) {
            return { frameRate: 6, quality: 0.25, queueSize: 1 };
        } else if (hostname.includes('instagram')) {
            return { frameRate: 4, quality: 0.25, queueSize: 1 };
        } else if (hostname.includes('twitch')) {
            return { frameRate: 6, quality: 0.3, queueSize: 1 };
        } else if (hostname.includes('twitter') || hostname.includes('x.com')) {
            return { frameRate: 4, quality: 0.25, queueSize: 1 };
        } else if (hostname.includes('facebook')) {
            return { frameRate: 4, quality: 0.25, queueSize: 1 };
        } else if (hostname.includes('reddit')) {
            return { frameRate: 3, quality: 0.25, queueSize: 1 };
        } else if (hostname.includes('linkedin')) {
            return { frameRate: 3, quality: 0.25, queueSize: 1 };
        } else if (hostname.includes('pornhub') || hostname.includes('xvideos') || hostname.includes('xnxx')) {
            return { frameRate: 8, quality: 0.4, queueSize: 2 }; // Still optimized for adult sites
        } else {
            // Default settings for any website - ultra-optimized for speed
            return { frameRate: 4, quality: 0.25, queueSize: 1 };
        }
    }
    
    async loadSettings() {
        try {
            const result = await chrome.storage.sync.get([
                'enabled', 'apiEndpoint', 'frameRate', 'compressionQuality', 'sensitivity'
            ]);
            
            this.enabled = result.enabled !== false; // Default to true
            this.apiEndpoint = result.apiEndpoint || 'http://localhost:5000/process-frame-stream';
            this.frameRate = result.frameRate || this.websiteSettings.frameRate;
            this.compressionQuality = result.compressionQuality || this.websiteSettings.quality;
            this.sensitivity = result.sensitivity || 0.5;
            
        } catch (error) {
            console.warn('Failed to load settings, using defaults:', error);
        }
    }
    
    initializeCanvas() {
        // Create off-screen canvas for frame capture
        this.canvas = document.createElement('canvas');
        this.ctx = this.canvas.getContext('2d');
        
        // Optimize canvas for performance
        this.ctx.imageSmoothingEnabled = false;
        this.ctx.imageSmoothingQuality = 'low';
    }
    
    async startProcessing() {
        if (!this.enabled) {
            console.log('🔞 Universal NSFW Filter disabled');
            return;
        }

        // Find all video elements on the page
        this.observeVideoElements();
        
        // Start video processing queue
        this.processingInterval = setInterval(() => {
            this.processFrameQueue();
        }, 1000 / this.frameRate);
        
        // Start image processing
        this.startImageProcessing();

        console.log(`🎬 Universal NSFW Filter started for ${window.location.hostname}`);
        console.log(`⚙️ Settings: ${this.frameRate}fps, quality: ${this.compressionQuality}, queue: ${this.websiteSettings.queueSize}`);
        console.log(`🖼️ Image processing: ${this.imageBlurSettings.enabled ? 'Enabled' : 'Disabled'}`);
    }
    
    observeVideoElements() {
        // Find existing video elements
        this.attachToExistingVideos();

        // Watch for new video elements (SPA navigation, dynamic content)
        const observer = new MutationObserver((mutations) => {
            let hasNewVideos = false;

            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        if (node.tagName === 'VIDEO') {
                            this.attachToVideo(node);
                            hasNewVideos = true;
                        } else if (node.querySelectorAll) {
                            const videos = node.querySelectorAll('video');
                            if (videos.length > 0) {
                                videos.forEach(video => this.attachToVideo(video));
                                hasNewVideos = true;
                            }
                        }
                    }
                });
            });

            // Re-scan if we detected new videos (for complex SPAs)
            if (hasNewVideos) {
                setTimeout(() => this.attachToExistingVideos(), 500);
            }
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });

        // YouTube-specific: Watch for YouTube player changes
        if (window.location.hostname.includes('youtube')) {
            this.setupYouTubeSpecificObservers();
        }

        // Re-scan periodically for dynamic content
        setInterval(() => {
            this.attachToExistingVideos();
        }, 3000); // More frequent for better responsiveness
    }

    setupYouTubeSpecificObservers() {
        // Watch for YouTube player state changes
        const youtubeObserver = new MutationObserver(() => {
            // YouTube dynamically loads videos, so we need to check frequently
            setTimeout(() => {
                this.attachToExistingVideos();
            }, 100);
        });

        // Observe YouTube-specific containers
        const youtubeSelectors = [
            '#player',
            '.html5-video-player',
            'ytd-player',
            '#movie_player',
            '.video-stream'
        ];

        youtubeSelectors.forEach(selector => {
            const element = document.querySelector(selector);
            if (element) {
                youtubeObserver.observe(element, {
                    childList: true,
                    subtree: true,
                    attributes: true,
                    attributeFilter: ['src', 'class']
                });
            }
        });

        // Also observe the entire body for YouTube's dynamic loading
        youtubeObserver.observe(document.body, {
            childList: true,
            subtree: true
        });

        this.youtubeObserver = youtubeObserver;
    }
    
    attachToExistingVideos() {
        const videoSelectors = this.getVideoSelectors();
        const foundVideos = new Set();

        videoSelectors.forEach(selector => {
            const videos = document.querySelectorAll(selector);
            videos.forEach(video => {
                if (!video.dataset.nsfwProcessorAttached && !foundVideos.has(video)) {
                    this.attachToVideo(video);
                    foundVideos.add(video);
                }
            });
        });
    }

    getVideoSelectors() {
        const hostname = window.location.hostname.toLowerCase();
        const selectors = ['video'];

        if (hostname.includes('youtube')) {
            selectors.push(
                '.html5-main-video',
                'video[src*="youtube"]',
                'video[data-youtube-id]',
                '#movie_player video',
                '.video-stream html5-main-video'
            );
        } else if (hostname.includes('tiktok')) {
            selectors.push(
                '.video-player video',
                '[data-testid="video-player"] video'
            );
        } else if (hostname.includes('instagram')) {
            selectors.push(
                'video[data-visualcompletion="media-vc"]',
                '.video-player video'
            );
        } else if (hostname.includes('twitter') || hostname.includes('x.com')) {
            selectors.push(
                '[data-testid="videoPlayer"] video',
                '.video-player video'
            );
        } else if (hostname.includes('facebook')) {
            selectors.push(
                '[data-visualcompletion="media-vc"] video',
                '.video-player video'
            );
        }

        return selectors;
    }
    
    attachToVideo(videoElement) {
        if (videoElement.dataset.nsfwProcessorAttached) {
            return; // Already attached
        }

        // Skip tiny videos (likely thumbnails or icons)
        const rect = videoElement.getBoundingClientRect();
        if (rect.width < 100 || rect.height < 75) {
            return;
        }

        // YouTube-specific: Skip if video is not the main player
        if (window.location.hostname.includes('youtube')) {
            const playerContainer = videoElement.closest('#movie_player, .html5-video-player');
            if (!playerContainer && rect.width < 300) {
                return; // Skip small YouTube videos that aren't the main player
            }
        }

        videoElement.dataset.nsfwProcessorAttached = 'true';

        console.log(`🎯 Attached to video: ${rect.width}x${rect.height} on ${window.location.hostname}`);

        // Capture frames periodically
        let lastCaptureTime = 0;
        const captureFrame = () => {
            if (!this.enabled) return;

            const now = Date.now();
            if (now - lastCaptureTime < (1000 / this.frameRate)) {
                return; // Rate limiting
            }

            lastCaptureTime = now;
            this.captureVideoFrame(videoElement);
        };

        // Listen for various video events
        const events = ['play', 'timeupdate', 'seeked', 'loadeddata', 'canplay', 'loadstart'];
        events.forEach(event => {
            videoElement.addEventListener(event, captureFrame, { passive: true });
        });

        // YouTube-specific: Also listen for YouTube player events
        if (window.location.hostname.includes('youtube')) {
            // Listen for YouTube API events if available
            if (window.YT && window.YT.Player) {
                setTimeout(() => {
                    this.setupYouTubePlayerEvents(videoElement);
                }, 1000);
            }
        }

        // Fallback: periodic capture when playing
        const intervalId = setInterval(() => {
            if (!videoElement.paused && !videoElement.ended && this.enabled) {
                captureFrame();
            }
        }, 1000 / this.frameRate);

        // Cleanup when video is removed
        const cleanupObserver = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.removedNodes.forEach((node) => {
                    if (node === videoElement || (node.contains && node.contains(videoElement))) {
                        clearInterval(intervalId);
                        cleanupObserver.disconnect();
                        console.log('🧹 Cleaned up video processor');
                    }
                });
            });
        });

        cleanupObserver.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    setupYouTubePlayerEvents(videoElement) {
        // Try to find the YouTube player instance
        const playerContainer = videoElement.closest('.html5-video-player, #movie_player');
        if (playerContainer) {
            // YouTube player events
            const playerEvents = ['onStateChange', 'onPlaybackQualityChange'];
            playerEvents.forEach(event => {
                if (playerContainer[event]) {
                    const originalHandler = playerContainer[event];
                    playerContainer[event] = (state) => {
                        // Call original handler
                        if (originalHandler) originalHandler(state);
                        // Trigger our capture
                        setTimeout(() => {
                            if (this.enabled) {
                                this.captureVideoFrame(videoElement);
                            }
                        }, 100);
                    };
                }
            });
        }
    }
    
    captureVideoFrame(videoElement) {
        if (!this.enabled) return;
        
        try {
            if (videoElement.videoWidth === 0 || videoElement.videoHeight === 0) {
                return; // Video not ready
            }
            
            // Skip frames if processing is too slow
            const now = Date.now();
            if (now - this.lastProcessTime < (1000 / this.frameRate)) {
                return;
            }
            
            // Set canvas size to match video (with aggressive optimization)
            const maxSize = 320; // Much smaller for faster processing
            const aspectRatio = videoElement.videoWidth / videoElement.videoHeight;
            
            let width, height;
            if (videoElement.videoWidth > videoElement.videoHeight) {
                width = Math.min(maxSize, videoElement.videoWidth);
                height = width / aspectRatio;
            } else {
                height = Math.min(maxSize, videoElement.videoHeight);
                width = height * aspectRatio;
            }
            
            this.canvas.width = width;
            this.canvas.height = height;
            
            // Draw video frame to canvas
            this.ctx.drawImage(videoElement, 0, 0, width, height);
            
            // Convert to base64 with aggressive compression
            const frameData = this.canvas.toDataURL('image/jpeg', this.compressionQuality);
            const base64Frame = frameData.split(',')[1]; // Remove data:image/jpeg;base64,
            
            // Add to processing queue if not full (priority to newer frames)
            if (this.frameQueue.length >= this.websiteSettings.queueSize) {
                this.frameQueue.shift(); // Remove oldest frame
            }
            
            this.frameQueue.push({
                frameData: base64Frame,
                videoElement: videoElement,
                timestamp: now,
                frameId: `${now}_${Math.random().toString(36).substr(2, 5)}`,
                website: window.location.hostname,
                originalSize: { width: videoElement.videoWidth, height: videoElement.videoHeight }
            });
            
            this.stats.totalFrames++;
            this.lastProcessTime = now;
            
        } catch (error) {
            console.error('Frame capture error:', error);
            this.stats.errors++;
        }
    }
    
    async processFrameQueue() {
        if (this.isProcessing || this.frameQueue.length === 0 || !this.enabled) {
            return;
        }
        
        this.isProcessing = true;
        
        const frameItem = this.frameQueue.shift();
        const startTime = Date.now();
        
        try {
            // Send frame to API with timeout
            const response = await fetch(this.apiEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    frame: frameItem.frameData,
                    frame_id: frameItem.frameId,
                    confidence: this.sensitivity || 0.5,
                    website: frameItem.website,
                    fast_mode: true // Enable fast processing mode
                }),
                signal: AbortSignal.timeout(2000) // Reduce timeout to 2 seconds
            });
            
            if (!response.ok) {
                throw new Error(`API request failed: ${response.status}`);
            }
            
            const result = await response.json();
            const latency = Date.now() - startTime;
            
            // Apply processed frame only if NSFW content was detected and processed
            if (result.processed && result.frame && latency < 800) {
                this.applyBlurredFrame(frameItem.videoElement, result.frame, frameItem.originalSize);
            }
            
            // Update statistics
            this.updateStats(latency);
            this.stats.processedFrames++;
            
            // Adaptive performance: reduce frame rate if processing is slow
            if (latency > 300) {
                this.frameRate = Math.max(3, this.frameRate * 0.8);
            } else if (latency < 100) {
                this.frameRate = Math.min(this.websiteSettings.frameRate, this.frameRate * 1.1);
            }
            
        } catch (error) {
            console.error('Frame processing error:', error);
            this.stats.errors++;
            
            // Implement exponential backoff for failed requests
            if (error.name === 'AbortError' || error.message.includes('network')) {
                this.frameRate = Math.max(2, this.frameRate * 0.5);
                setTimeout(() => {
                    this.frameRate = this.websiteSettings.frameRate;
                }, 10000); // Reset after 10 seconds
            }
        } finally {
            this.isProcessing = false;
        }
    }
    
    applyBlurredFrame(videoElement, processedFrameBase64, originalSize) {
        try {
            const videoId = videoElement.dataset.nsfwVideoId || this.generateVideoId(videoElement);
            if (!videoElement.dataset.nsfwVideoId) {
                videoElement.dataset.nsfwVideoId = videoId;
            }
            
            // Remove existing overlay for this video
            this.removeOverlay(videoId);
            
            // Create new overlay
            const overlay = document.createElement('canvas');
            overlay.classList.add('nsfw-overlay');
            overlay.dataset.videoId = videoId;
            overlay.style.cssText = `
                position: absolute !important;
                pointer-events: none !important;
                z-index: 999999 !important;
                border-radius: inherit !important;
                image-rendering: pixelated !important;
                object-fit: cover !important;
            `;
            
            // Get video container
            const videoContainer = this.getVideoContainer(videoElement);
            
            // Position and size overlay to match video exactly
            this.updateOverlayPosition(videoElement, overlay);
            
            // Draw processed frame to overlay
            const overlayCtx = overlay.getContext('2d');
            const img = new Image();
            img.onload = () => {
                try {
                    overlayCtx.drawImage(img, 0, 0, overlay.width, overlay.height);
                    
                    // Store overlay reference
                    this.activeOverlays.set(videoId, {
                        overlay: overlay,
                        videoElement: videoElement,
                        lastUpdate: Date.now()
                    });
                    
                    // Auto-remove overlay after 3 seconds to prevent stale content
                    setTimeout(() => {
                        this.removeOverlay(videoId);
                    }, 3000);
                    
                } catch (drawError) {
                    console.error('Error drawing overlay:', drawError);
                    overlay.remove();
                }
            };
            img.onerror = () => {
                console.error('Error loading processed frame');
                overlay.remove();
            };
            img.src = `data:image/jpeg;base64,${processedFrameBase64}`;
            
            // Add overlay to container
            videoContainer.appendChild(overlay);
            
            // Update overlay position on video resize/move
            this.setupOverlayTracking(videoElement, overlay);
            
        } catch (error) {
            console.error('Error applying blurred frame:', error);
        }
    }
    
    generateVideoId(videoElement) {
        // Generate unique ID for video element
        return `nsfw_video_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
    
    getVideoContainer(videoElement) {
        // Find the best container for the overlay
        let container = videoElement.parentElement;
        
        // Look for a positioned container
        while (container && container !== document.body) {
            const style = window.getComputedStyle(container);
            if (style.position === 'relative' || style.position === 'absolute' || style.position === 'fixed') {
                break;
            }
            container = container.parentElement;
        }
        
        // If no positioned container found, use video's direct parent
        if (!container || container === document.body) {
            container = videoElement.parentElement;
            // Make container relative if needed
            if (window.getComputedStyle(container).position === 'static') {
                container.style.position = 'relative';
            }
        }
        
        return container;
    }
    
    updateOverlayPosition(videoElement, overlay) {
        const videoRect = videoElement.getBoundingClientRect();
        const containerRect = overlay.parentElement.getBoundingClientRect();
        
        // Calculate relative position
        const relativeTop = videoRect.top - containerRect.top;
        const relativeLeft = videoRect.left - containerRect.left;
        
        // Set overlay dimensions and position
        overlay.width = videoRect.width;
        overlay.height = videoRect.height;
        overlay.style.width = `${videoRect.width}px`;
        overlay.style.height = `${videoRect.height}px`;
        overlay.style.top = `${relativeTop}px`;
        overlay.style.left = `${relativeLeft}px`;
    }
    
    setupOverlayTracking(videoElement, overlay) {
        // Track video position changes
        const updatePosition = () => {
            if (overlay.parentElement && videoElement.isConnected) {
                this.updateOverlayPosition(videoElement, overlay);
            }
        };
        
        // Use ResizeObserver for efficient tracking
        if (window.ResizeObserver) {
            const resizeObserver = new ResizeObserver(updatePosition);
            resizeObserver.observe(videoElement);
            
            // Store observer for cleanup
            overlay.dataset.resizeObserver = 'active';
            overlay._resizeObserver = resizeObserver;
        }
        
        // Fallback: periodic position updates
        const positionInterval = setInterval(updatePosition, 100);
        overlay._positionInterval = positionInterval;
        
        // Cleanup when overlay is removed
        overlay.addEventListener('removed', () => {
            if (overlay._resizeObserver) {
                overlay._resizeObserver.disconnect();
            }
            if (overlay._positionInterval) {
                clearInterval(overlay._positionInterval);
            }
        });
    }
    
    removeOverlay(videoId) {
        const overlayData = this.activeOverlays.get(videoId);
        if (overlayData && overlayData.overlay) {
            const overlay = overlayData.overlay;
            
            // Trigger cleanup event
            overlay.dispatchEvent(new Event('removed'));
            
            // Remove from DOM
            if (overlay.parentElement) {
                overlay.parentElement.removeChild(overlay);
            }
            
            // Remove from tracking
            this.activeOverlays.delete(videoId);
        }
    }
    
    updateStats(latency) {
        // Update rolling average latency
        const alpha = 0.1; // Smoothing factor
        this.stats.avgLatency = this.stats.avgLatency * (1 - alpha) + latency * alpha;
    }
    
    getStats() {
        const runtime = (Date.now() - this.stats.startTime) / 1000;
        return {
            ...this.stats,
            successRate: this.stats.totalFrames > 0 ? 
                ((this.stats.processedFrames / this.stats.totalFrames) * 100).toFixed(1) + '%' : '0%',
            avgLatency: Math.round(this.stats.avgLatency) + 'ms',
            runtime: Math.round(runtime) + 's',
            website: window.location.hostname,
            enabled: this.enabled,
            frameRate: this.frameRate
        };
    }
    
    setEnabled(enabled) {
        this.enabled = enabled;
        if (enabled) {
            this.startProcessing();
        } else {
            // Remove all overlays when disabled
            document.querySelectorAll('.nsfw-overlay').forEach(overlay => {
                overlay.remove();
            });
        }
        
        // Save setting
        chrome.storage.sync.set({ enabled: enabled });
    }
    
    updateSettings(settings) {
        if (settings.frameRate) this.frameRate = settings.frameRate;
        if (settings.compressionQuality) this.compressionQuality = settings.compressionQuality;
        if (settings.sensitivity) this.sensitivity = settings.sensitivity;
        if (settings.apiEndpoint) this.apiEndpoint = settings.apiEndpoint;
        
        // Update image blur settings
        if (settings.imageBlurSettings) {
            Object.assign(this.imageBlurSettings, settings.imageBlurSettings);
        }
        
        // Save settings
        chrome.storage.sync.set(settings);
    }
    
    // ================== IMAGE PROCESSING METHODS ==================
    
    startImageProcessing() {
        if (!this.enabled || !this.imageBlurSettings.enabled) {
            console.log('🖼️ Image processing disabled');
            return;
        }
        
        // Start image monitoring with higher frequency for instant processing
        this.imageProcessingInterval = setInterval(() => {
            this.processImageQueue();
        }, 200); // Process every 200ms for instant blur
        
        // Find and process existing images
        this.scanForImages();
        
        // Watch for new images
        this.observeImageElements();
        
        console.log('🖼️ Image NSFW detection started with instant processing');
    }
    
    scanForImages() {
        if (!this.enabled || !this.imageBlurSettings.enabled) return;
        
        const imageSelectors = this.getImageSelectors();
        
        imageSelectors.forEach(selector => {
            const images = document.querySelectorAll(selector);
            images.forEach(img => this.processImageElement(img));
        });
    }
    
    getImageSelectors() {
        const hostname = window.location.hostname.toLowerCase();

        // Website-specific image selectors
        const selectors = [
            'img', // All images
            '[style*="background-image"]', // Background images
            'video[poster]' // Video thumbnails
        ];

        // Add website-specific selectors
        if (hostname.includes('google')) {
            selectors.push(
                '.rg_i img', // Google Images results
                '.H8Rx8c img', // Google image thumbnails
                '[data-src]', // Lazy-loaded images
                '[data-lazy-src]', // Another lazy loading pattern
                '.ivg-i img', // Google image grid
                '.rg_ic img', // Google image container
                '[jsname*="hSRGPd"] img', // Google search result images
                '.islrc img', // Image search results
                '[data-ved] img', // Google tracking images
                '.wXeWr img', // Google image preview
                '.rg_bk img', // Google image block
                'img[src*="googleusercontent"]', // Google hosted images
                'img[src*="ggpht"]', // Google image proxy
                '.YQ4gaf img', // Google search result images
                '.uhHOwf img', // Google image results
                '[class*="image"] img', // Generic image classes
                '[class*="photo"] img' // Generic photo classes
            );
        } else if (hostname.includes('youtube')) {
            selectors.push(
                '#thumbnail img', '.ytd-thumbnail img', '.yt-img-shadow img',
                '.ytp-cued-thumbnail-overlay-image', // YouTube player thumbnails
                '[class*="thumbnail"] img', // Generic thumbnail class
                'ytd-video-meta-block img', // Video meta images
                'ytd-channel-avatar img', // Channel avatars
                'ytd-playlist-thumbnail img', // Playlist thumbnails
                '#avatar img', // User avatars
                '.comment-avatar img' // Comment avatars
            );
        } else if (hostname.includes('twitter') || hostname.includes('x.com')) {
            selectors.push(
                '[data-testid="tweetPhoto"] img',
                '.css-9pa8cd img',
                '[role="img"]',
                '.avatar img',
                '[data-testid="Tweet-User-Avatar"] img'
            );
        } else if (hostname.includes('instagram')) {
            selectors.push(
                'img[src*="cdninstagram"]',
                '._aagv img',
                '._aa8j img',
                '[data-visualcompletion="media-vc-image"] img'
            );
        } else if (hostname.includes('reddit')) {
            selectors.push(
                '.Post img',
                '[data-test-id="post-content"] img',
                '.thumbnail img',
                '._2_tDEnGMLxpM6uOa2kaDB3 img'
            );
        } else if (hostname.includes('tiktok')) {
            selectors.push(
                '.video-feed img',
                '.tt-video-cover img',
                '.avatar img',
                '[data-testid="user-avatar"] img'
            );
        } else if (hostname.includes('facebook')) {
            selectors.push(
                '[role="img"]',
                '.spotlight img',
                '._6iiz img',
                '[data-visualcompletion="media-vc-image"] img'
            );
        } else if (hostname.includes('tinder') || hostname.includes('bumble') || hostname.includes('hinge')) {
            // Dating apps - be more aggressive
            selectors.push(
                '.profile img',
                '.photo img',
                '[class*="photo"] img',
                '[class*="image"] img'
            );
        }

        return selectors;
    }
    
    processImageElement(imgElement) {
        if (!imgElement || this.processedImages.has(imgElement)) {
            return; // Already processed
        }
        
        // Skip very small images (likely icons) - but be less restrictive for instant blur
        const rect = imgElement.getBoundingClientRect();
        if (rect.width < 40 || rect.height < 40) {
            return;
        }
        
        // Check if this image type should be processed
        if (!this.shouldProcessImage(imgElement)) {
            return;
        }
        
        // Mark as processed
        this.processedImages.add(imgElement);
        
        // Add to processing queue with high priority for instant blur
        if (this.imageQueue.length < this.maxImageQueueSize * 2) { // Allow more in queue
            this.imageQueue.unshift({ // Add to front for immediate processing
                element: imgElement,
                timestamp: Date.now(),
                imageId: `img_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
                priority: 'normal'
            });
            
            this.stats.totalImages++;
        }
        
        console.log(`📸 Queued image for instant processing: ${imgElement.src || 'inline-image'}`);
    }
    
    shouldProcessImage(imgElement) {
        const settings = this.imageBlurSettings;
        
        if (settings.blurAllImages) {
            return true;
        }
        
        // Check for thumbnails
        if (settings.blurThumbnails) {
            const src = imgElement.src || imgElement.getAttribute('data-src') || '';
            const classes = imgElement.className.toLowerCase();
            const parent = imgElement.parentElement;
            
            // Common thumbnail indicators
            if (src.includes('thumb') || src.includes('preview') || 
                classes.includes('thumb') || classes.includes('preview') ||
                parent?.className.toLowerCase().includes('thumb')) {
                return true;
            }
        }
        
        // Check for profile pictures
        if (settings.blurProfilePictures) {
            const classes = imgElement.className.toLowerCase();
            const alt = imgElement.alt?.toLowerCase() || '';
            
            if (classes.includes('profile') || classes.includes('avatar') ||
                alt.includes('profile') || alt.includes('avatar')) {
                return true;
            }
        }
        
        // Check for ads
        if (settings.blurAds) {
            const parent = imgElement.closest('[class*="ad"], [id*="ad"], [data-testid*="ad"]');
            if (parent) {
                return true;
            }
        }
        
        return false;
    }
    
    observeImageElements() {
        // Use multiple observers for better coverage
        this.setupImageMutationObserver();
        this.setupImageLoadObserver();
        this.setupDynamicContentObserver();
        
        // Google-specific: Watch for lazy-loaded images
        if (window.location.hostname.includes('google')) {
            this.setupGoogleSpecificObservers();
        }
        
        // Rescan images periodically for dynamic content
        setInterval(() => {
            this.scanForImages();
        }, 1000); // More frequent for Google
        
        // Also scan on scroll and resize events
        let scrollTimeout;
        const throttledScan = () => {
            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(() => {
                this.scanForImages();
            }, 200); // Faster for Google
        };
        
        window.addEventListener('scroll', throttledScan, { passive: true });
        window.addEventListener('resize', throttledScan, { passive: true });
    }    setupImageMutationObserver() {
        const observer = new MutationObserver((mutations) => {
            let hasNewImages = false;
            let hasImageChanges = false;

            mutations.forEach((mutation) => {
                // Check for added nodes
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        if (node.tagName === 'IMG') {
                            setTimeout(() => this.processImageElement(node), 50);
                            hasNewImages = true;
                        } else if (node.querySelectorAll) {
                            const images = node.querySelectorAll('img');
                            images.forEach(img => {
                                setTimeout(() => this.processImageElement(img), 50);
                            });
                            if (images.length > 0) hasNewImages = true;
                        }
                    }
                });

                // Check for attribute changes (src changes, etc.)
                if (mutation.type === 'attributes' &&
                    (mutation.attributeName === 'src' || mutation.attributeName === 'data-src')) {
                    const target = mutation.target;
                    if (target.tagName === 'IMG') {
                        // Remove from processed set if src changed
                        this.processedImages.delete(target);
                        setTimeout(() => this.processImageElement(target), 100);
                        hasImageChanges = true;
                    }
                }
            });

            // If we detected changes, do a broader scan after a short delay
            if (hasNewImages || hasImageChanges) {
                setTimeout(() => {
                    this.scanForImages();
                }, 1000);
            }
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true,
            attributes: true,
            attributeFilter: ['src', 'data-src', 'style']
        });

        // Store observer for cleanup
        this.imageMutationObserver = observer;
    }

    setupImageLoadObserver() {
        // Observe when images finish loading
        const imageLoadObserver = new MutationObserver(() => {
            // When new images are added to DOM, they might not be loaded yet
            setTimeout(() => {
                this.scanForImages();
            }, 500);
        });

        // Observe the entire document for any changes
        imageLoadObserver.observe(document.body, {
            childList: true,
            subtree: true
        });

        this.imageLoadObserver = imageLoadObserver;
    }

    setupDynamicContentObserver() {
        // For SPAs and dynamic content loading
        const dynamicObserver = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.addedNodes.length > 0) {
                    // Check if this looks like dynamic content
                    const hasSignificantContent = Array.from(mutation.addedNodes).some(node => {
                        if (node.nodeType === Node.ELEMENT_NODE) {
                            return node.querySelectorAll &&
                                   (node.querySelectorAll('img').length > 0 ||
                                    node.querySelectorAll('[style*="background-image"]').length > 0);
                        }
                        return false;
                    });

                    if (hasSignificantContent) {
                        setTimeout(() => {
                            this.scanForImages();
                        }, 200);
                    }
                }
            });
        });

        dynamicObserver.observe(document.body, {
            childList: true,
            subtree: true
        });

        this.dynamicContentObserver = dynamicObserver;
    }
    
    setupGoogleSpecificObservers() {
        console.log('🔍 Setting up Google-specific image observers');
        
        // Watch for Google's lazy loading attributes
        const googleLazyObserver = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'attributes') {
                    const target = mutation.target;
                    if (target.tagName === 'IMG') {
                        // Check if src or data-src changed
                        if (mutation.attributeName === 'src' || 
                            mutation.attributeName === 'data-src' || 
                            mutation.attributeName === 'data-lazy-src') {
                            
                            // Remove from processed set if attributes changed
                            this.processedImages.delete(target);
                            
                            // Process immediately
                            setTimeout(() => {
                                this.processImageElementImmediately(target);
                            }, 10);
                        }
                    }
                }
            });
        });
        
        // Observe all images for attribute changes
        googleLazyObserver.observe(document.body, {
            attributes: true,
            subtree: true,
            attributeFilter: ['src', 'data-src', 'data-lazy-src', 'class']
        });
        
        // Watch for Google search result containers
        const googleContainerObserver = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        // Check for Google-specific containers
                        if (node.matches && (
                            node.matches('.rg_bk') || 
                            node.matches('.islrc') || 
                            node.matches('[jsname*="hSRGPd"]') ||
                            node.matches('.H8Rx8c') ||
                            node.matches('.ivg-i')
                        )) {
                            setTimeout(() => {
                                this.scanGoogleContainer(node);
                            }, 50);
                        }
                        
                        // Check child elements
                        if (node.querySelectorAll) {
                            const googleContainers = node.querySelectorAll(
                                '.rg_bk, .islrc, [jsname*="hSRGPd"], .H8Rx8c, .ivg-i'
                            );
                            googleContainers.forEach(container => {
                                setTimeout(() => {
                                    this.scanGoogleContainer(container);
                                }, 50);
                            });
                        }
                    }
                });
            });
        });
        
        googleContainerObserver.observe(document.body, {
            childList: true,
            subtree: true
        });
        
        // Periodic Google-specific scanning
        setInterval(() => {
            this.scanGoogleImages();
        }, 500); // Very frequent for Google
        
        this.googleLazyObserver = googleLazyObserver;
        this.googleContainerObserver = googleContainerObserver;
    }
    
    scanGoogleContainer(container) {
        const images = container.querySelectorAll('img, [data-src], [data-lazy-src]');
        images.forEach(img => {
            if (!this.processedImages.has(img)) {
                setTimeout(() => {
                    this.processImageElementImmediately(img);
                }, 10);
            }
        });
    }
    
    scanGoogleImages() {
        // Scan for Google-specific image patterns
        const googleSelectors = [
            '.rg_i img',
            '.H8Rx8c img', 
            '[data-src]:not([src])', // Images with data-src but no src
            '[data-lazy-src]:not([src])',
            '.islrc img',
            '[jsname*="hSRGPd"] img',
            '.wXeWr img',
            '.YQ4gaf img',
            '.uhHOwf img',
            // Google Images search specific
            '.islrg img',
            '.rg_ic img',
            '[data-ved] img',
            '.ivg-i img'
        ];
        
        googleSelectors.forEach(selector => {
            const images = document.querySelectorAll(selector);
            images.forEach(img => {
                if (!this.processedImages.has(img)) {
                    this.processImageElementImmediately(img);
                }
            });
        });
        
        // Also check for images that might have been loaded but not processed
        const allImages = document.querySelectorAll('img');
        allImages.forEach(img => {
            if (!this.processedImages.has(img) && 
                (img.src.includes('googleusercontent') || 
                 img.src.includes('ggpht') || 
                 img.getAttribute('data-src')?.includes('google'))) {
                this.processImageElementImmediately(img);
            }
        });
        
        console.log(`🔍 Google scan completed - found ${document.querySelectorAll('img').length} total images`);
    }
    
    async processImageQueue() {
        if (this.imageQueue.length === 0 || !this.enabled || !this.imageBlurSettings.enabled) {
            return;
        }

        // Prioritize high-priority items (from instant processing)
        let imageItem;
        const highPriorityIndex = this.imageQueue.findIndex(item => item.priority === 'high');
        if (highPriorityIndex !== -1) {
            imageItem = this.imageQueue.splice(highPriorityIndex, 1)[0];
        } else {
            imageItem = this.imageQueue.shift();
        }

        const startTime = Date.now();

        try {
            // Skip if already processed too many times
            if (imageItem.retryCount && imageItem.retryCount >= 2) {
                console.warn('Skipping image after too many retries:', imageItem.imageId);
                return;
            }

            // Capture image data
            const imageData = await this.captureImageData(imageItem.element);
            if (!imageData) {
                // Re-queue with retry count if it might be a timing issue
                if (!imageItem.retryCount) {
                    imageItem.retryCount = 1;
                    setTimeout(() => {
                        if (this.imageQueue.length < this.maxImageQueueSize * 2) {
                            this.imageQueue.unshift(imageItem);
                        }
                    }, 500); // Faster retry for instant blur
                }
                return;
            }

            // Send to API for processing with shorter timeout for instant blur
            const response = await fetch(this.imageApiEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    image: imageData,
                    image_id: imageItem.imageId,
                    confidence: this.imageBlurSettings.sensitivity,
                    fast_mode: true
                }),
                signal: AbortSignal.timeout(2000) // Shorter timeout for instant processing
            });

            if (!response.ok) {
                throw new Error(`API request failed: ${response.status}`);
            }

            const result = await response.json();

            // Apply blur if NSFW content detected
            if (result.nsfw_detected) {
                this.applyImageBlur(imageItem.element, result.confidence || 0.8);
                console.log(`🔞 Instantly blurred NSFW image (confidence: ${result.confidence})`);
            }

            this.stats.processedImages++;

        } catch (error) {
            console.error('Image processing error:', error);
            this.stats.errors++;

            // Re-queue on network errors (but not too many times)
            if ((error.name === 'TypeError' || error.message.includes('network') || error.message.includes('fetch')) &&
                (!imageItem.retryCount || imageItem.retryCount < 2)) {
                imageItem.retryCount = (imageItem.retryCount || 0) + 1;
                const isGoogleImage = window.location.hostname.includes('google') && 
                                    (imageItem.element.src?.includes('googleusercontent') || 
                                     imageItem.element.src?.includes('ggpht') ||
                                     imageItem.element.getAttribute('data-src')?.includes('google'));
                setTimeout(() => {
                    if (this.imageQueue.length < this.maxImageQueueSize * (isGoogleImage ? 3 : 2)) {
                        this.imageQueue.unshift(imageItem);
                    }
                }, (isGoogleImage ? 300 : 1000) * imageItem.retryCount); // Faster retry for Google
            }
        }
    }
    
    async captureImageData(imgElement) {
        try {
            // Get image source, trying multiple attributes for lazy-loaded images
            let imgSrc = imgElement.src || imgElement.getAttribute('data-src') ||
                        imgElement.getAttribute('data-lazy-src') ||
                        imgElement.getAttribute('data-original') ||
                        imgElement.getAttribute('data-url') || '';

            if (!imgSrc) {
                console.warn('Image has no source URL');
                return null;
            }

            // For cross-origin images, set crossOrigin to enable CORS
            const imgUrl = new URL(imgSrc, window.location.href);
            const isCrossOrigin = imgUrl.origin !== window.location.origin;

            if (isCrossOrigin && !imgElement.crossOrigin) {
                console.log('Setting crossOrigin for cross-origin image:', imgSrc);
                imgElement.crossOrigin = 'anonymous';

                // If the image doesn't have src set but has data-src, set it now
                if (!imgElement.src && imgSrc !== imgElement.src) {
                    imgElement.src = imgSrc;
                }
            }

            // Wait for image to load if not loaded
            if (!imgElement.complete || imgElement.naturalWidth === 0) {
                await new Promise((resolve, reject) => {
                    const timeout = setTimeout(() => {
                        reject(new Error('Image load timeout'));
                    }, 3000); // Increased timeout for cross-origin images

                    if (imgElement.complete && imgElement.naturalWidth > 0) {
                        clearTimeout(timeout);
                        resolve();
                        return;
                    }

                    const onLoad = () => {
                        clearTimeout(timeout);
                        imgElement.removeEventListener('load', onLoad);
                        imgElement.removeEventListener('error', onError);
                        resolve();
                    };

                    const onError = (error) => {
                        clearTimeout(timeout);
                        imgElement.removeEventListener('load', onLoad);
                        imgElement.removeEventListener('error', onError);
                        console.warn('Image failed to load:', imgSrc, error);
                        reject(new Error('Image failed to load'));
                    };

                    imgElement.addEventListener('load', onLoad);
                    imgElement.addEventListener('error', onError);
                });
            }

            // Double-check image dimensions after load
            if (!imgElement.naturalWidth || !imgElement.naturalHeight) {
                console.warn('Image has no natural dimensions');
                return null;
            }

            // Create a canvas to capture the image
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d', { willReadFrequently: true });

            // Set canvas size (limit for performance and to avoid memory issues)
            const maxSize = 400;
            const aspectRatio = imgElement.naturalWidth / imgElement.naturalHeight;

            let width, height;
            if (imgElement.naturalWidth > imgElement.naturalHeight) {
                width = Math.min(maxSize, imgElement.naturalWidth);
                height = width / aspectRatio;
            } else {
                height = Math.min(maxSize, imgElement.naturalHeight);
                width = height * aspectRatio;
            }

            canvas.width = width;
            canvas.height = height;

            // Enable cross-origin on canvas if needed
            if (imgElement.crossOrigin) {
                canvas.crossOrigin = imgElement.crossOrigin;
            }

            // Draw image to canvas with error handling
            try {
                ctx.drawImage(imgElement, 0, 0, width, height);
            } catch (drawError) {
                console.error('Error drawing image to canvas:', drawError);
                // Try alternative approach for some image types
                if (drawError.name === 'SecurityError') {
                    console.warn('Security error - image may be tainted, skipping:', imgSrc);
                    return null;
                }
                throw drawError;
            }

            // Convert to base64
            let dataURL;
            try {
                dataURL = canvas.toDataURL('image/jpeg', 0.7);
            } catch (dataUrlError) {
                console.error('Error converting canvas to data URL:', dataUrlError);
                return null;
            }

            return dataURL.split(',')[1]; // Remove data:image/jpeg;base64,

        } catch (error) {
            console.error('Error capturing image data:', error);
            // Don't rethrow - just return null to indicate failure
            return null;
        }
    }
    
    applyImageBlur(imgElement, confidence) {
        try {
            // Apply CSS blur filter instantly (no transition for instant blur)
            const blurIntensity = this.imageBlurSettings.blurIntensity;
            imgElement.style.filter = `blur(${blurIntensity}px)`;
            imgElement.style.transition = 'none'; // No transition for instant effect
            
            // Add click to unblur temporarily
            const unblurHandler = () => {
                imgElement.style.filter = 'none';
                setTimeout(() => {
                    imgElement.style.filter = `blur(${blurIntensity}px)`;
                }, 3000); // Show for 3 seconds
            };
            
            imgElement.addEventListener('click', unblurHandler, { once: true });
            
            // Add visual indicator
            const indicator = document.createElement('div');
            indicator.className = 'nsfw-image-indicator';
            indicator.innerHTML = '🔞';
            indicator.style.cssText = `
                position: absolute;
                top: 5px;
                left: 5px;
                background: rgba(255, 0, 0, 0.8);
                color: white;
                padding: 2px 6px;
                border-radius: 3px;
                font-size: 12px;
                z-index: 999999;
                pointer-events: none;
            `;
            
            // Position indicator relative to image
            if (imgElement.parentElement.style.position !== 'relative') {
                imgElement.parentElement.style.position = 'relative';
            }
            imgElement.parentElement.insertBefore(indicator, imgElement.nextSibling);
            
            console.log(`🔞 Instantly blurred NSFW image (confidence: ${confidence})`);
            
        } catch (error) {
            console.error('Error applying instant image blur:', error);
        }
    }
    
    stop() {
        this.enabled = false;
        
        // Stop video processing
        if (this.processingInterval) {
            clearInterval(this.processingInterval);
            this.processingInterval = null;
        }
        
        // Stop image processing
        if (this.imageProcessingInterval) {
            clearInterval(this.imageProcessingInterval);
            this.imageProcessingInterval = null;
        }
        
        // Clear queues
        this.frameQueue = [];
        this.imageQueue = [];
        this.processedImages.clear();
        
        // Remove all overlays and indicators
        document.querySelectorAll('.nsfw-overlay').forEach(overlay => {
            overlay.remove();
        });
        
        document.querySelectorAll('.nsfw-image-indicator').forEach(indicator => {
            indicator.remove();
        });
        
        // Remove blur from images
        document.querySelectorAll('img[style*="blur"]').forEach(img => {
            img.style.filter = '';
        });
        
        console.log('🛑 Universal NSFW Filter stopped');
    }
}

// Initialize the processor
let videoProcessor = null;

function initializeUniversalNSFWFilter() {
    // Prevent duplicate initialization
    if (window.UniversalNSFWFilterInitialized) {
        console.log('🔄 Universal NSFW Filter already initialized, skipping');
        return;
    }
    
    // Skip certain domains that shouldn't be processed
    const skipDomains = [
        'chrome-extension://',
        'moz-extension://',
        'about:',
        'chrome://',
        'edge://',
        'localhost',
        '127.0.0.1'
    ];
    
    const currentUrl = window.location.href.toLowerCase();
    if (skipDomains.some(domain => currentUrl.includes(domain))) {
        return;
    }
    
    // Stop existing processor if any
    if (videoProcessor) {
        videoProcessor.stop();
    }
    
    videoProcessor = new UniversalVideoProcessor();
    window.UniversalNSFWFilterInitialized = true;
    
    console.log(`🔞 Universal NSFW Filter initialized for ${window.location.hostname}`);
}

// Auto-initialize immediately when script loads for instant blur
if (!window.UniversalNSFWFilterInitialized) {
    initializeUniversalNSFWFilter();
    
    // For Google: Force immediate scan after a short delay
    if (window.location.hostname.includes('google')) {
        setTimeout(() => {
            if (window.UniversalNSFWFilter && window.UniversalNSFWFilter.getProcessor) {
                const processor = window.UniversalNSFWFilter.getProcessor();
                if (processor && processor.scanGoogleImages) {
                    console.log('🔍 Forcing immediate Google image scan');
                    processor.scanGoogleImages();
                    
                    // Set up continuous monitoring for Google
                    setInterval(() => {
                        processor.scanGoogleImages();
                    }, 2000); // Check every 2 seconds for new Google images
                }
            }
        }, 1000);
    }
}

// Also initialize on DOMContentLoaded for safety
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        if (!window.UniversalNSFWFilterInitialized) {
            initializeUniversalNSFWFilter();
        }
    });
}

// Handle SPA navigation and page changes
let lastUrl = location.href;
const urlObserver = new MutationObserver(() => {
    const url = location.href;
    if (url !== lastUrl) {
        lastUrl = url;
        console.log(`🔄 Navigation detected: ${url}`);
        
        // Reset initialization flag for new pages
        window.UniversalNSFWFilterInitialized = false;
        
        setTimeout(initializeUniversalNSFWFilter, 1000); // Reinitialize after navigation
    }
});

urlObserver.observe(document, { subtree: true, childList: true });

// Listen for popstate events (back/forward navigation)
window.addEventListener('popstate', () => {
    window.UniversalNSFWFilterInitialized = false;
    setTimeout(initializeUniversalNSFWFilter, 500);
});

// Listen for hash changes
window.addEventListener('hashchange', () => {
    window.UniversalNSFWFilterInitialized = false;
    setTimeout(initializeUniversalNSFWFilter, 500);
});

// Expose API for popup and debugging
if (!window.UniversalNSFWFilter) {
    window.UniversalNSFWFilter = {
        getStats: () => videoProcessor?.getStats() || {},
        setEnabled: (enabled) => videoProcessor?.setEnabled(enabled),
        updateSettings: (settings) => videoProcessor?.updateSettings(settings),
        restart: () => {
            window.UniversalNSFWFilterInitialized = false;
            initializeUniversalNSFWFilter();
        },
        stop: () => videoProcessor?.stop(),
        getProcessor: () => videoProcessor
    };
}

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === 'PING') {
        sendResponse({ pong: true });
    } else if (request.type === 'GET_STATS') {
        sendResponse(window.UniversalNSFWFilter.getStats());
    } else if (request.type === 'SET_ENABLED') {
        window.UniversalNSFWFilter.setEnabled(request.enabled);
        sendResponse({ success: true });
    } else if (request.type === 'UPDATE_SETTINGS') {
        window.UniversalNSFWFilter.updateSettings(request.settings);
        sendResponse({ success: true });
    } else if (request.type === 'RESTART_PROCESSOR') {
        window.UniversalNSFWFilter.restart();
        sendResponse({ success: true });
    }
});

console.log('🌐 Universal NSFW Filter content script loaded for', window.location.hostname);

})(); // End of IIFE
