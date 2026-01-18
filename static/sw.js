// OMEGA KITT - Service Worker
// Knight Industries Two Thousand - Enhanced PWA with Fleet Mesh support
// Provides: Offline functionality, auto-repair, background worker coordination

const CACHE_NAME = 'omega-kitt-fleet-v1';
const ASSETS_TO_CACHE = [
    '/',
    '/manifest.json',
    '/static/manifest.json',
    '/static/icons/icon-192x192.png',
    '/static/icons/icon-512x512.png',
    '/static/audio/kitt_voice.wav'
];

// Install event - cache core assets
self.addEventListener('install', (event) => {
    console.log('[OMEGA SW] ⚡ Installing KITT Service Worker...');
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('[OMEGA SW] 💾 Caching essential assets');
                return cache.addAll(ASSETS_TO_CACHE).catch((err) => {
                    console.warn('[OMEGA SW] ⚠️ Some assets failed to cache:', err);
                });
            })
            .then(() => {
                console.log('[OMEGA SW] ✅ Installation complete');
                return self.skipWaiting();
            })
    );
});

// Activate event - clean old caches and take control
self.addEventListener('activate', (event) => {
    console.log('[OMEGA SW] 🔴 Activating KITT Service Worker...');
    event.waitUntil(
        caches.keys()
            .then((cacheNames) => {
                return Promise.all(
                    cacheNames
                        .filter((name) => name !== CACHE_NAME && name.startsWith('omega'))
                        .map((name) => {
                            console.log('[OMEGA SW] 🗑️ Deleting old cache:', name);
                            return caches.delete(name);
                        })
                );
            })
            .then(() => {
                console.log('[OMEGA SW] ✅ Activation complete - Taking control');
                return self.clients.claim();
            })
    );
});

// Fetch event - offline-first strategy with network fallback
self.addEventListener('fetch', (event) => {
    // Skip non-GET requests
    if (event.request.method !== 'GET') return;

    // Skip API calls (always use network)
    if (event.request.url.includes('/api/')) {
        event.respondWith(fetch(event.request));
        return;
    }

    event.respondWith(
        caches.match(event.request)
            .then((cachedResponse) => {
                if (cachedResponse) {
                    // Return cached version, update in background
                    fetchAndCache(event.request);
                    return cachedResponse;
                }

                // Not in cache - fetch from network
                return fetch(event.request)
                    .then((networkResponse) => {
                        // Cache valid responses
                        if (networkResponse && networkResponse.status === 200) {
                            const responseToCache = networkResponse.clone();
                            caches.open(CACHE_NAME)
                                .then((cache) => {
                                    cache.put(event.request, responseToCache);
                                });
                        }
                        return networkResponse;
                    })
                    .catch(() => {
                        // Network failed - return offline page for navigation
                        if (event.request.mode === 'navigate') {
                            return caches.match('/');
                        }
                    });
            })
    );
});

// Background fetch and cache update
function fetchAndCache(request) {
    fetch(request)
        .then((response) => {
            if (response && response.status === 200) {
                caches.open(CACHE_NAME)
                    .then((cache) => cache.put(request, response));
            }
        })
        .catch(() => {
            // Silent fail for background updates
        });
}

// Push notifications - Fleet status updates
self.addEventListener('push', (event) => {
    console.log('[OMEGA SW] 🔔 Push notification received');

    if (!event.data) return;

    const data = event.data.json();
    const options = {
        body: data.body || 'OMEGA has a message',
        icon: '/static/icons/icon-192x192.png',
        badge: '/static/icons/icon-72x72.png',
        vibrate: [200, 100, 200, 100, 200],
        data: {
            url: data.url || '/',
            timestamp: Date.now()
        },
        actions: [
            {
                action: 'open',
                title: 'Open OMEGA',
                icon: '/static/icons/icon-96x96.png'
            },
            {
                action: 'dismiss',
                title: 'Dismiss',
                icon: '/static/icons/icon-96x96.png'
            }
        ],
        requireInteraction: data.important || false,
        tag: data.tag || 'omega-notification',
        renotify: true
    };

    event.waitUntil(
        self.registration.showNotification(
            data.title || '🔴 OMEGA KITT',
            options
        )
    );
});

// Notification clicks
self.addEventListener('notificationclick', (event) => {
    console.log('[OMEGA SW] 👆 Notification clicked');
    event.notification.close();

    if (event.action === 'dismiss') {
        return;
    }

    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true })
            .then((clientList) => {
                // Focus existing window
                for (const client of clientList) {
                    if (client.url.includes(event.notification.data.url) && 'focus' in client) {
                        return client.focus();
                    }
                }
                // Open new window
                if (clients.openWindow) {
                    return clients.openWindow(event.notification.data.url);
                }
            })
    );
});

// Background sync - Sync fleet status and auto-repair
self.addEventListener('sync', (event) => {
    console.log('[OMEGA SW] 🔄 Background sync triggered:', event.tag);

    if (event.tag === 'fleet-status-sync') {
        event.waitUntil(syncFleetStatus());
    } else if (event.tag === 'auto-repair-sync') {
        event.waitUntil(runAutoRepair());
    } else if (event.tag === 'source-control-sync') {
        event.waitUntil(syncSourceControl());
    }
});

// Sync fleet mesh status
async function syncFleetStatus() {
    console.log('[OMEGA SW] 🐝 Syncing fleet mesh status...');
    try {
        const response = await fetch('/api/mesh/status');
        if (response.ok) {
            const data = await response.json();
            console.log('[OMEGA SW] ✅ Fleet status synced:', data);

            // Notify if workers changed
            if (data.fleet && data.fleet.active_workers > 0) {
                self.registration.showNotification('🐝 Fleet Mesh Active', {
                    body: `${data.fleet.active_workers} workers contributing compute power`,
                    icon: '/static/icons/icon-192x192.png',
                    tag: 'fleet-status'
                });
            }
        }
    } catch (error) {
        console.error('[OMEGA SW] ❌ Fleet sync failed:', error);
    }
}

// Run auto-repair checks
async function runAutoRepair() {
    console.log('[OMEGA SW] 🔧 Running auto-repair checks...');
    try {
        // Check source control status
        const scResponse = await fetch('/api/source-control/status');
        if (scResponse.ok) {
            const scData = await scResponse.json();
            if (scData.uncommitted_changes > 0) {
                console.log('[OMEGA SW] 📝 Auto-committing changes...');
                await fetch('/api/source-control/auto-commit', { method: 'POST' });
            }
        }

        console.log('[OMEGA SW] ✅ Auto-repair complete');
    } catch (error) {
        console.error('[OMEGA SW] ❌ Auto-repair failed:', error);
    }
}

// Sync source control (auto-commit)
async function syncSourceControl() {
    console.log('[OMEGA SW] 📝 Syncing source control...');
    try {
        const response = await fetch('/api/source-control/auto-commit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        if (response.ok) {
            const data = await response.json();
            console.log('[OMEGA SW] ✅ Source control synced:', data);
        }
    } catch (error) {
        console.error('[OMEGA SW] ❌ Source control sync failed:', error);
    }
}

// Periodic background sync (every 30 seconds when idle)
self.addEventListener('periodicsync', (event) => {
    console.log('[OMEGA SW] ⏰ Periodic sync:', event.tag);

    if (event.tag === 'fleet-monitor') {
        event.waitUntil(syncFleetStatus());
    } else if (event.tag === 'auto-repair') {
        event.waitUntil(runAutoRepair());
    }
});

// Message handling from main app
self.addEventListener('message', (event) => {
    console.log('[OMEGA SW] 💬 Message received:', event.data);

    if (event.data && event.data.type) {
        switch (event.data.type) {
            case 'SKIP_WAITING':
                self.skipWaiting();
                break;
            case 'FLEET_UPDATE':
                syncFleetStatus();
                break;
            case 'AUTO_REPAIR':
                runAutoRepair();
                break;
            case 'CLEAR_CACHE':
                caches.delete(CACHE_NAME);
                break;
        }
    }
});

// Log service worker lifecycle
console.log('[OMEGA SW] 🔴 KITT Service Worker loaded and ready');
console.log('[OMEGA SW] Features: Offline, Auto-Repair, Fleet Mesh, Background Sync');                // Clone request for fetch and cache
const fetchRequest = event.request.clone();

return fetch(fetchRequest).then((response) => {
    // Check if valid response
    if (!response || response.status !== 200 || response.type !== 'basic') {
        return response;
    }

    // Clone response for caching
    const responseToCache = response.clone();

    caches.open(CACHE_NAME)
        .then((cache) => {
            cache.put(event.request, responseToCache);
        });

    return response;
});
            })
    );
});

// Background sync for offline operations
self.addEventListener('sync', (event) => {
    console.log('[Service Worker] Background sync:', event.tag);

    if (event.tag === 'sync-omega-data') {
        event.waitUntil(syncOmegaData());
    }
});

async function syncOmegaData() {
    try {
        // Sync any pending data when online
        console.log('[Service Worker] Syncing Omega data...');
        // Implementation for data sync
        return Promise.resolve();
    } catch (error) {
        console.error('[Service Worker] Sync failed:', error);
        return Promise.reject(error);
    }
}

// Push notifications
self.addEventListener('push', (event) => {
    console.log('[Service Worker] Push notification received');

    const options = {
        body: event.data ? event.data.text() : 'Omega notification',
        icon: '/static/icons/icon-192x192.png',
        badge: '/static/icons/badge-72x72.png',
        vibrate: [200, 100, 200],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: 1
        },
        actions: [
            {
                action: 'open',
                title: 'Open Omega',
                icon: '/static/icons/check.png'
            },
            {
                action: 'close',
                title: 'Dismiss',
                icon: '/static/icons/close.png'
            }
        ]
    };

    event.waitUntil(
        self.registration.showNotification('Omega Control Panel', options)
    );
});

// Notification click handler
self.addEventListener('notificationclick', (event) => {
    console.log('[Service Worker] Notification clicked:', event.action);

    event.notification.close();

    if (event.action === 'open') {
        event.waitUntil(
            clients.openWindow('/')
        );
    }
});

// Idle CPU optimization - process background tasks
self.addEventListener('message', (event) => {
    if (event.data && event.data.type === 'IDLE_CPU_TASK') {
        console.log('[Service Worker] Processing idle CPU task');
        event.waitUntil(processIdleTask(event.data.payload));
    }
});

async function processIdleTask(payload) {
    // Knight Rider style: use spare CPU cycles smoothly
    console.log('[Service Worker] Idle task processing:', payload);

    // Simulate background processing (can be ML inference, data processing, etc.)
    return new Promise((resolve) => {
        setTimeout(() => {
            console.log('[Service Worker] Idle task complete');
            resolve();
        }, 1000);
    });
}

// Wake lock for keeping app active during voice sessions
let wakeLock = null;

self.addEventListener('message', async (event) => {
    if (event.data && event.data.type === 'WAKE_LOCK_REQUEST') {
        try {
            if ('wakeLock' in navigator) {
                wakeLock = await navigator.wakeLock.request('screen');
                console.log('[Service Worker] Wake lock acquired');

                wakeLock.addEventListener('release', () => {
                    console.log('[Service Worker] Wake lock released');
                });
            }
        } catch (err) {
            console.error('[Service Worker] Wake lock error:', err);
        }
    }

    if (event.data && event.data.type === 'WAKE_LOCK_RELEASE') {
        if (wakeLock) {
            wakeLock.release();
            wakeLock = null;
        }
    }
});

console.log('[Service Worker] Omega KITT Service Worker loaded');
