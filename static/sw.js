// Omega Control Panel - Service Worker
// Enables offline functionality, background sync, and idle CPU optimization

const CACHE_NAME = 'omega-kitt-v1';
const urlsToCache = [
  '/',
  '/static/manifest.json',
  '/static/icons/icon-192x192.png',
  '/static/icons/icon-512x512.png'
];

// Install service worker and cache resources
self.addEventListener('install', (event) => {
  console.log('[Service Worker] Installing...');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('[Service Worker] Caching app shell');
        return cache.addAll(urlsToCache);
      })
  );
});

// Activate service worker and clean old caches
self.addEventListener('activate', (event) => {
  console.log('[Service Worker] Activating...');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('[Service Worker] Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// Fetch event - offline-first strategy
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        // Cache hit - return cached response
        if (response) {
          return response;
        }
        
        // Clone request for fetch and cache
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
