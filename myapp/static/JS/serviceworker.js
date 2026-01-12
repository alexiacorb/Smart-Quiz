var staticCacheName='quiz-static';

self.addEventListener('install',function(event){
    event.waitUntil(
        caches.open(staticCacheName).then(function(cache){
            return cache.addAll([
                '',
            ]);
        })
    );
});

self.addEventListener('fetch',function(event){
    var requwestURL=new URL(event.request.url);
    if(requwestURL.origin===location.origin){
        if(requestURL.pathname=== '/'){
            event.respondWith(caches.match(''));
            return;
        }
    }
    event.respondWith(
        cache.match(event.request).then(function(response){
            return response || fetch(event.request);
        })
    );
});
