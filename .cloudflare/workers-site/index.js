import { getAssetFromKV } from '@cloudflare/kv-asset-handler'

/**
 * The DEBUG flag will do two things that help during development:
 * 1. we will skip caching on the edge, which makes it easier to debug
 * 2. we will return an error message on exception in your Response rather than the default 404.html page
 */
const DEBUG = false

addEventListener('fetch', event => {
  try {
    event.respondWith(handleEvent(event))
  } catch (e) {
    if (DEBUG) {
      return event.respondWith(
        new Response(e.message || e.toString(), {
          status: 500,
        }),
      )
    }
    event.respondWith(new Response('Internal Error', { status: 500 }))
  }
})

async function handleEvent(event) {
  const url = new URL(event.request.url)
  
  try {
    // First attempt to serve static assets
    const page = await getAssetFromKV(event, {
      mapRequestToAsset: req => new Request(`${new URL(req.url).origin}/frontend${new URL(req.url).pathname}`, req),
    })
    return page
  } catch (e) {
    // If static asset not found, fallback to the Flask application
    return await fetch('https://emotcare.workers.dev', event.request)
  }
}
