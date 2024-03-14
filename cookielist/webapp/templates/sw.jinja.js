const appId = "{{ SITE_NAME }}".replace(/ /g, "")
const appVersion = "{{ COOKIE_VERSION }}"
const coreAssets = [
  // {% assets 'SASS' %}
  "$ASSET_URL",
  // {% endassets %}
  // {% assets 'JS' %}
  "$ASSET_URL",
  // {% endassets %}

  "{{ url_for('static', filename='apple-touch-icon.png') }}",
  "{{ url_for('static', filename='favicon-32x32.png') }}",
  "{{ url_for('static', filename='favicon-16x16.png') }}",
  "{{ url_for('AboutView:favicon_ico') }}",
  "{{ url_for('static', filename='images/favicon.webp') }}",
  "{{ url_for('static', filename='images/pong.png') }}",

  "https://cdn.jsdelivr.net/npm/animate.css@4.1.1/animate.min.css",
  "https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/styles/stackoverflow-dark.min.css",
  "https://cdn.jsdelivr.net/npm/jquery@3.7.1/dist/jquery.min.j",
  "https://cdn.jsdelivr.net/npm/mustache@4.2.0/mustache.min.js",
  "https://cdn.jsdelivr.net/npm/js-yaml@4.1.0/dist/js-yaml.min.js",
  "https://cdn.jsdelivr.net/npm/clipboard@2.0.11/dist/clipboard.min.js",
  "https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/highlight.min.js",
  "https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/languages/json.min.js",
  "https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/languages/markdown.min.js",
  "https://cdn.jsdelivr.net/npm/lazyload@2.0.0-rc.2/lazyload.min.js",
  "https://cdn.jsdelivr.net/npm/fuse.js@7.0.0/dist/fuse.min.js",
  "https://cdn.jsdelivr.net/npm/@jsonurl/jsonurl@1.1.7/dist/jsonurl.min.js",
  "https://cdn.jsdelivr.net/npm/ace-builds@1.32.7/src-min-noconflict/ace.js",
  "https://cdn.jsdelivr.net/npm/ace-builds@1.32.7/src-min-noconflict/mode-yaml.js",
  "https://cdn.jsdelivr.net/npm/ace-builds@1.32.7/src-min-noconflict/theme-one_dark.js",
]

self.addEventListener('install', function (event) {
  event.waitUntil(caches.open(appId + appVersion).then(function (cache) {
    for (let asset of coreAssets) {
      cache.add(new Request(asset));
    }
    return cache;
  }));
  self.skipWaiting();
});


self.addEventListener('fetch', function (event) {
  if (event.request.cache === 'only-if-cached' && event.request.mode !== 'same-origin') return;
  event.respondWith(
    caches.match(event.request).then(function (request) {
      if (request) { 
        return request
      } else {       
        return fetch(event.request)
      }
    })
  )
})

self.addEventListener('activate', function (event) {
  event.waitUntil(
    caches.keys().then(function (keyList) {
      var cacheWhitelist = keyList.filter(function (key) {
        return key.indexOf(appId)
      })
      cacheWhitelist.push(appId + appVersion);
      return Promise.all(keyList.map(function (key, index) {
        if (cacheWhitelist.indexOf(key) === -1) {
          return caches.delete(keyList[index])
        }
      }))
    })
  )
  event.waitUntil(clients.claim());
})