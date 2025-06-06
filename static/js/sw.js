// เวอร์ชันของ Service Worker
const CACHE_NAME = 'weather-app-v1.0.0';

// ไฟล์ที่ต้องแคช
const urlsToCache = [
  '/',
  '/static/css/style.css',
  '/static/js/main.js',
  'https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css',
  '/static/images/icon-72x72.png',
  '/static/images/icon-96x96.png',
  '/static/images/icon-128x128.png',
  '/static/images/icon-144x144.png',
  '/static/images/icon-152x152.png',
  '/static/images/icon-192x192.png',
  '/static/images/icon-384x384.png',
  '/static/images/icon-512x512.png',
  '/static/images/favicon.png',
  '/static/images/weather-icons/01d.png',
  '/static/images/weather-icons/01n.png',
  '/static/images/weather-icons/02d.png',
  '/static/images/weather-icons/02n.png',
  '/static/images/weather-icons/03d.png',
  '/static/images/weather-icons/03n.png',
  '/static/images/weather-icons/04d.png',
  '/static/images/weather-icons/04n.png',
  '/static/images/weather-icons/09d.png',
  '/static/images/weather-icons/09n.png',
  '/static/images/weather-icons/10d.png',
  '/static/images/weather-icons/10n.png',
  '/static/images/weather-icons/11d.png',
  '/static/images/weather-icons/11n.png',
  '/static/images/weather-icons/13d.png',
  '/static/images/weather-icons/13n.png',
  '/static/images/weather-icons/50d.png',
  '/static/images/weather-icons/50n.png',
  '/static/images/weather-icons/unknown.png'
];

// ติดตั้ง Service Worker
self.addEventListener('install', event => {
  console.log('[Service Worker] กำลังติดตั้ง...');
  
  // แคชไฟล์ที่จำเป็น
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('[Service Worker] กำลังแคชไฟล์');
        return cache.addAll(urlsToCache);
      })
      .then(() => self.skipWaiting())
  );
});

// เปิดใช้งาน Service Worker
self.addEventListener('activate', event => {
  console.log('[Service Worker] เปิดใช้งานแล้ว');
  
  // ลบแคชเก่าทิ้ง
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cache => {
          if (cache !== CACHE_NAME) {
            console.log('[Service Worker] ลบแคชเก่า:', cache);
            return caches.delete(cache);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// ดึงข้อมูลจากแคชหรือเครือข่าย
self.addEventListener('fetch', event => {
  // ไม่อ่านไฟล์จากแคชสำหรับ API
  if (event.request.url.includes('/api/')) {
    return;
  }

  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // คืนค่าจากแคชถ้ามี
        if (response) {
          return response;
        }
        
        // ไม่มีในแคช ให้โหลดจากเครือข่าย
        return fetch(event.request)
          .then(response => {
            // ตรวจสอบว่าการตอบกลับถูกต้อง
            if (!response || response.status !== 200 || response.type !== 'basic') {
              return response;
            }

            // คัดลอกการตอบกลับเพื่อแคช
            const responseToCache = response.clone();

            // เพิ่มลงในแคช
            caches.open(CACHE_NAME)
              .then(cache => {
                cache.put(event.request, responseToCache);
              });

            return response;
          });
      })
      .catch(() => {
        // หน้าข้อผิดพลาดแบบออฟไลน์
        if (event.request.mode === 'navigate') {
          return caches.match('/offline.html');
        }
      })
  );
});

// รับข้อมูลแบบ Push
self.addEventListener('push', event => {
  const title = 'Weather App';
  const options = {
    body: event.data.text(),
    icon: '/static/images/icon-192x192.png',
    badge: '/static/images/icon-96x96.png'
  };

  event.waitUntil(
    self.registration.showNotification(title, options)
  );
});

// รับการคลิกที่การแจ้งเตือน
self.addEventListener('notificationclick', event => {
  event.notification.close();
  
  event.waitUntil(
    clients.matchAll({ type: 'window' })
      .then(clientList => {
        for (const client of clientList) {
          if (client.url === '/' && 'focus' in client) {
            return client.focus();
          }
        }
        
        if (clients.openWindow) {
          return clients.openWindow('/');
        }
      })
  );
});
