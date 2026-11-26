// Structured data utility for Rebecca Richards Photography
// Implements schema.org JSON-LD for better SEO

export interface Album {
  title: string;
  slug: { current: string };
  date: string;
  albumType: string;
  coverImage?: any;
  images?: any[];
}

// Local Business Schema
export function getLocalBusinessSchema() {
  return {
    "@context": "https://schema.org",
    "@type": "LocalBusiness",
    "@id": "https://rebeccarichardsphoto.com/#organization",
    "name": "Rebecca Richards Photography",
    "alternateName": "Rebecca Richards Events",
    "description": "Professional wedding photography in Doylestown, PA. Capturing authentic, timeless moments for your special day.",
    "url": "https://rebeccarichardsphoto.com",
    "logo": {
      "@type": "ImageObject",
      "url": "https://rebeccarichardsphoto.com/images/logo.jpg",
      "width": "600",
      "height": "300"
    },
    "image": [
      "https://rebeccarichardsphoto.com/images/hero.jpg",
      "https://rebeccarichardsphoto.com/images/about.jpg"
    ],
    "telephone": "(267) 259-1036",
    "email": "rebeccarichardsevents@gmail.com",
    "address": {
      "@type": "PostalAddress",
      "addressLocality": "Doylestown",
      "addressRegion": "PA",
      "postalCode": "18901",
      "addressCountry": "US"
    },
    "geo": {
      "@type": "GeoCoordinates",
      "latitude": 40.3101,
      "longitude": -75.1298
    },
    "areaServed": [
      {
        "@type": "State",
        "name": "Pennsylvania"
      },
      {
        "@type": "State", 
        "name": "New Jersey"
      },
      {
        "@type": "State",
        "name": "Delaware"
      }
    ],
    "priceRange": "$$$$",
    "openingHours": "Mo-Sa 09:00-18:00",
    "sameAs": [
      "https://www.instagram.com/rebeccarichardsphoto",
      "https://www.facebook.com/rebeccarichardsphoto"
    ]
  };
}

// Professional Service Schema
export function getProfessionalServiceSchema() {
  return {
    "@context": "https://schema.org",
    "@type": "ProfessionalService",
    "@id": "https://rebeccarichardsphoto.com/#service",
    "name": "Rebecca Richards Photography",
    "description": "Professional wedding and event photography services",
    "provider": {
      "@id": "https://rebeccarichardsphoto.com/#organization"
    },
    "serviceType": "Photography",
    "areaServed": [
      "Pennsylvania",
      "New Jersey", 
      "Delaware"
    ],
    "hasOfferCatalog": {
      "@type": "OfferCatalog",
      "name": "Photography Services",
      "itemListElement": [
        {
          "@type": "Offer",
          "itemOffered": {
            "@type": "Service",
            "name": "Wedding Photography",
            "description": "Full-day wedding photography coverage capturing every precious moment"
          }
        },
        {
          "@type": "Offer", 
          "itemOffered": {
            "@type": "Service",
            "name": "Engagement Sessions",
            "description": "Intimate portrait sessions to celebrate your engagement"
          }
        },
        {
          "@type": "Offer",
          "itemOffered": {
            "@type": "Service", 
            "name": "Special Events",
            "description": "Professional photography for anniversaries, family celebrations, and milestones"
          }
        }
      ]
    }
  };
}

// Person Schema for Rebecca
export function getPersonSchema() {
  return {
    "@context": "https://schema.org",
    "@type": "Person",
    "@id": "https://rebeccarichardsphoto.com/#person",
    "name": "Rebecca Richards",
    "jobTitle": "Wedding Photographer", 
    "description": "Professional wedding photographer based in Doylestown, PA, specializing in authentic, joyful moments.",
    "url": "https://rebeccarichardsphoto.com/about",
    "image": "https://rebeccarichardsphoto.com/images/about.jpg",
    "telephone": "(267) 259-1036",
    "email": "rebeccarichardsevents@gmail.com",
    "address": {
      "@type": "PostalAddress",
      "addressLocality": "Doylestown",
      "addressRegion": "PA", 
      "addressCountry": "US"
    },
    "worksFor": {
      "@id": "https://rebeccarichardsphoto.com/#organization"
    },
    "knowsAbout": [
      "Wedding Photography",
      "Portrait Photography", 
      "Event Photography",
      "Engagement Photography"
    ],
    "sameAs": [
      "https://www.instagram.com/rebeccarichardsphoto",
      "https://www.facebook.com/rebeccarichardsphoto"
    ]
  };
}

// Website Schema
export function getWebsiteSchema() {
  return {
    "@context": "https://schema.org",
    "@type": "WebSite",
    "@id": "https://rebeccarichardsphoto.com/#website",
    "name": "Rebecca Richards Photography",
    "description": "Professional wedding photography in Doylestown, PA",
    "url": "https://rebeccarichardsphoto.com",
    "publisher": {
      "@id": "https://rebeccarichardsphoto.com/#organization"
    },
    "potentialAction": {
      "@type": "SearchAction",
      "target": {
        "@type": "EntryPoint",
        "urlTemplate": "https://rebeccarichardsphoto.com/client-albums?search={search_term_string}"
      },
      "query-input": "required name=search_term_string"
    }
  };
}

// Breadcrumb Schema
export function getBreadcrumbSchema(items: Array<{ name: string; url: string }>) {
  return {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": items.map((item, index) => ({
      "@type": "ListItem",
      "position": index + 1,
      "name": item.name,
      "item": item.url
    }))
  };
}

// Image Gallery Schema for Album Pages
export function getImageGallerySchema(album: Album, images: string[]) {
  return {
    "@context": "https://schema.org",
    "@type": "ImageGallery", 
    "name": album.title,
    "description": `${getAlbumTypeLabel(album.albumType)} photography by Rebecca Richards`,
    "creator": {
      "@id": "https://rebeccarichardsphoto.com/#person"
    },
    "dateCreated": album.date,
    "associatedMedia": images.map((imageUrl, index) => ({
      "@type": "ImageObject",
      "url": imageUrl,
      "name": `${album.title} - Image ${index + 1}`,
      "creator": {
        "@id": "https://rebeccarichardsphoto.com/#person"
      },
      "copyrightHolder": {
        "@id": "https://rebeccarichardsphoto.com/#organization"
      }
    }))
  };
}

// Photography Event Schema for Wedding Albums
export function getPhotographyEventSchema(album: Album) {
  return {
    "@context": "https://schema.org",
    "@type": "Event",
    "@id": `https://rebeccarichardsphoto.com/albums/${album.slug.current}#event`,
    "name": album.title,
    "description": `${getAlbumTypeLabel(album.albumType)} captured by Rebecca Richards Photography`,
    "startDate": album.date,
    "eventStatus": "https://schema.org/EventScheduled",
    "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
    "location": {
      "@type": "Place",
      "address": {
        "@type": "PostalAddress", 
        "addressRegion": "PA",
        "addressCountry": "US"
      }
    },
    "photographer": {
      "@id": "https://rebeccarichardsphoto.com/#person"
    },
    "organizer": {
      "@id": "https://rebeccarichardsphoto.com/#organization" 
    }
  };
}

// Helper function to get human-readable album type
function getAlbumTypeLabel(albumType: string): string {
  const typeMap: Record<string, string> = {
    'wedding': 'Wedding Photography',
    'engagement': 'Engagement Session',
    'bridal': 'Bridal Session', 
    'family': 'Family Portrait',
    'maternity': 'Maternity Session',
    'event': 'Special Event',
    'graduation': 'Graduation',
    'portrait': 'Portrait Session'
  };
  return typeMap[albumType] || 'Portrait Session';
}

// Combined Schema for Homepage
export function getHomepageSchema() {
  return {
    "@context": "https://schema.org",
    "@graph": [
      getWebsiteSchema(),
      getLocalBusinessSchema(), 
      getProfessionalServiceSchema(),
      getPersonSchema()
    ]
  };
}