import type { APIRoute } from 'astro'
import { generateOGImage, type OGImageOptions } from '../../lib/og-images'

export const GET: APIRoute = async ({ request }) => {
  try {
    const url = new URL(request.url)
    const searchParams = url.searchParams

    // Extract parameters from query string
    const title = searchParams.get('title') || 'Rebecca Richards Photography'
    const subtitle = searchParams.get('subtitle') || undefined
    const type = (searchParams.get('type') as OGImageOptions['type']) || 'homepage'
    const backgroundImage = searchParams.get('bg') || undefined

    // Generate the OG image
    const imageResponse = await generateOGImage({
      title,
      subtitle,
      type,
      backgroundImage,
    })

    // Return the image with proper headers
    return new Response(await imageResponse.arrayBuffer(), {
      headers: {
        'Content-Type': 'image/png',
        'Cache-Control': 'public, max-age=31536000, immutable',
      },
    })
  } catch (error) {
    console.error('Error generating OG image:', error)
    
    // Return a fallback response
    return new Response('Error generating image', {
      status: 500,
      headers: {
        'Content-Type': 'text/plain',
      },
    })
  }
}