export interface OGMetadata {
  title: string
  description: string
  type: 'homepage' | 'album' | 'service' | 'about' | 'contact'
  subtitle?: string
  backgroundImage?: string
}

/**
 * Generate the OG image URL for a given page
 * Prefers static images when available, falls back to dynamic generation
 */
export function generateOGImageURL(metadata: OGMetadata, baseURL = ''): string {
  // Check if we have a static image available for this page type
  const staticImageMap: Record<string, string> = {
    homepage: '/og/homepage.png',
    about: '/og/about.png',
    service: '/og/services.png',
    contact: '/og/contact.png',
  }

  // For static page types, use pre-generated images
  if (staticImageMap[metadata.type] && !metadata.subtitle?.includes('•')) {
    return `${baseURL}${staticImageMap[metadata.type]}`
  }

  // For dynamic content (like specific albums), use API generation
  const params = new URLSearchParams()
  
  params.set('title', metadata.title)
  params.set('type', metadata.type)
  
  if (metadata.subtitle) {
    params.set('subtitle', metadata.subtitle)
  }
  
  if (metadata.backgroundImage) {
    params.set('bg', metadata.backgroundImage)
  }
  
  return `${baseURL}/api/og?${params.toString()}`
}

/**
 * Get OG metadata for different page types
 */
export function getPageOGMetadata(
  pageType: 'homepage' | 'album' | 'service' | 'about' | 'contact',
  customData?: {
    title?: string
    subtitle?: string
    albumTitle?: string
    albumDate?: string
    albumType?: string
  }
): OGMetadata {
  switch (pageType) {
    case 'homepage':
      return {
        title: 'Capturing Love Stories',
        description: 'Professional wedding photography in Doylestown, PA. Capturing authentic, timeless moments for your special day.',
        type: 'homepage',
        subtitle: 'Pennsylvania Wedding Photographer specializing in authentic, timeless moments',
        backgroundImage: '/images/hero.jpg',
      }
    
    case 'album':
      return {
        title: customData?.albumTitle || 'Wedding Album',
        description: `Beautiful wedding photography by Rebecca Richards Photography${customData?.albumDate ? ` - ${customData.albumDate}` : ''}`,
        type: 'album',
        subtitle: customData?.albumType ? `${customData.albumType}${customData?.albumDate ? ` • ${customData.albumDate}` : ''}` : undefined,
      }
    
    case 'service':
      return {
        title: 'Photography Services',
        description: 'Wedding photography, engagement sessions, and special event photography in Pennsylvania.',
        type: 'service',
        subtitle: 'Comprehensive photography services for your most important moments',
      }
    
    case 'about':
      return {
        title: 'About Rebecca',
        description: 'Meet Rebecca Richards, a wedding photographer based in Doylestown, PA, specializing in authentic, joyful moments.',
        type: 'about',
        subtitle: 'Pennsylvania wedding photographer with a passion for authentic storytelling',
      }
    
    case 'contact':
      return {
        title: 'Get in Touch',
        description: 'Ready to book your wedding photography? Contact Rebecca Richards Photography for a consultation.',
        type: 'contact',
        subtitle: "Let's create something beautiful together",
      }
    
    default:
      return getPageOGMetadata('homepage')
  }
}