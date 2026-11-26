// Analytics and search console integration for Rebecca Richards Photography
// This file provides ready-to-use code for Google Analytics 4 and Search Console

// Google Analytics 4 Configuration
export const GA4_MEASUREMENT_ID = 'G-XXXXXXXXXX' // Replace with actual GA4 measurement ID

// Google Analytics 4 Setup Script
export function getGA4Script() {
  return {
    // External script tag for gtag
    src: `https://www.googletagmanager.com/gtag/js?id=${GA4_MEASUREMENT_ID}`,
    
    // Initialization script
    initScript: `
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', '${GA4_MEASUREMENT_ID}', {
        page_title: document.title,
        page_location: window.location.href,
        send_page_view: true,
        anonymize_ip: true,
        cookie_flags: 'SameSite=None;Secure'
      });
    `
  }
}

// Enhanced ecommerce tracking for consultation bookings
export function trackConsultationRequest(method: string = 'contact_form') {
  if (typeof gtag !== 'undefined') {
    gtag('event', 'generate_lead', {
      currency: 'USD',
      value: 2000, // Average wedding photography value
      lead_source: method,
      content_category: 'wedding_photography',
      custom_parameters: {
        photographer: 'rebecca_richards',
        service_area: 'doylestown_pa'
      }
    })
  }
}

// Track album views for portfolio engagement
export function trackAlbumView(albumTitle: string, albumType: string) {
  if (typeof gtag !== 'undefined') {
    gtag('event', 'view_item', {
      item_category: 'portfolio',
      item_category2: albumType,
      item_name: albumTitle,
      content_type: 'photo_gallery',
      custom_parameters: {
        photographer: 'rebecca_richards'
      }
    })
  }
}

// Track service page engagement
export function trackServiceEngagement(serviceType: string, engagementType: string = 'view') {
  if (typeof gtag !== 'undefined') {
    gtag('event', 'engagement', {
      engagement_type: engagementType,
      content_category: 'services',
      content_group1: serviceType,
      custom_parameters: {
        photographer: 'rebecca_richards',
        service_area: 'pennsylvania'
      }
    })
  }
}

// Track outbound link clicks (social media, etc.)
export function trackOutboundLink(url: string, linkType: string = 'external') {
  if (typeof gtag !== 'undefined') {
    gtag('event', 'click', {
      event_category: 'outbound',
      event_label: url,
      transport_type: 'beacon',
      custom_parameters: {
        link_type: linkType,
        photographer: 'rebecca_richards'
      }
    })
  }
}

// Google Search Console verification meta tag
export const SEARCH_CONSOLE_VERIFICATION = 'google-site-verification-content-here' // Replace with actual verification

// Bing Webmaster Tools verification (optional)
export const BING_VERIFICATION = 'bing-site-verification-content-here' // Replace with actual verification

// Facebook Domain Verification (for Facebook Pixel if needed)
export const FACEBOOK_DOMAIN_VERIFICATION = 'facebook-domain-verification-content-here' // Replace with actual verification

// Privacy-focused analytics alternative setup (if preferred over GA4)
export function getSimpleAnalyticsScript() {
  return {
    // Simple Analytics or similar privacy-focused alternative
    src: 'https://scripts.simpleanalyticscdn.com/latest.js',
    attributes: {
      'data-hostname': 'rebeccarichardsphoto.com',
      'data-collect-dnt': 'false'
    }
  }
}

// Core Web Vitals tracking
export function trackCoreWebVitals() {
  // This would typically use the web-vitals library
  const vitalsScript = `
    // Core Web Vitals tracking
    // Install: npm install web-vitals
    // import {getCLS, getFID, getFCP, getLCP, getTTFB} from 'web-vitals';
    
    function sendToAnalytics(metric) {
      if (typeof gtag !== 'undefined') {
        gtag('event', metric.name, {
          event_category: 'Web Vitals',
          event_label: metric.id,
          value: Math.round(metric.name === 'CLS' ? metric.value * 1000 : metric.value),
          non_interaction: true,
        });
      }
    }
    
    // Uncomment when web-vitals is installed:
    // getCLS(sendToAnalytics);
    // getFID(sendToAnalytics);  
    // getFCP(sendToAnalytics);
    // getLCP(sendToAnalytics);
    // getTTFB(sendToAnalytics);
  `
  
  return vitalsScript
}

// Social media tracking
export function trackSocialShare(platform: string, url: string, title: string) {
  if (typeof gtag !== 'undefined') {
    gtag('event', 'share', {
      method: platform,
      content_type: 'portfolio',
      item_id: url,
      content_category: 'wedding_photography',
      custom_parameters: {
        shared_title: title,
        photographer: 'rebecca_richards'
      }
    })
  }
}

// Phone number click tracking (for call tracking)
export function trackPhoneCall() {
  if (typeof gtag !== 'undefined') {
    gtag('event', 'phone_call', {
      event_category: 'contact',
      event_label: '(267) 259-1036',
      value: 1,
      custom_parameters: {
        contact_method: 'phone',
        photographer: 'rebecca_richards'
      }
    })
  }
}

// Email link click tracking
export function trackEmailClick() {
  if (typeof gtag !== 'undefined') {
    gtag('event', 'email_click', {
      event_category: 'contact',
      event_label: 'rebeccarichardsevents@gmail.com',
      value: 1,
      custom_parameters: {
        contact_method: 'email',
        photographer: 'rebecca_richards'
      }
    })
  }
}