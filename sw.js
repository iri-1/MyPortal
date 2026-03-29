// インストール時に実行される処理（今は空でもOK）
self.addEventListener('install', (event) => {
    console.log('Service Worker installed');
});

// ネットワークリクエストを処理（オフライン対応の土台）
self.addEventListener('fetch', (event) => {
    // ここにキャッシュの仕組みを書くとオフラインでも動きます
});