# Open Graph (OG) Image System

This documentation covers the comprehensive OG image system implemented for Rebecca Richards Photography website.

## Overview

The OG image system provides beautiful, branded social media preview images that match the site's aesthetic. The system uses a hybrid approach:

1. **Static Images**: Pre-generated during build for common pages (homepage, about, services, contact)
2. **Dynamic Images**: Generated on-demand for unique content like individual album pages

## Design Features

### Brand Colors
- Rose: #fb7185 (rose-400)
- Rose Dark: #f43f5e (rose-500)
- Gray: #111827 (gray-900)
- Light Gray: #f9fafb (gray-50)
- Text Gray: #6b7280 (gray-500)

### Templates

#### Homepage Template
- Hero-style layout with gradient background
- Large, elegant typography
- Text shadow for readability
- Brand mark in bottom right

#### Album Template
- Clean, minimal design with camera icon
- Centered layout with album title
- Date and type information
- Rose accent bar at top

#### Service/About/Contact Templates
- Professional layout with left accent bar
- Icon + title combination
- Subtle background patterns
- Brand consistency

## File Structure

```
src/
├── lib/
│   ├── og-images.ts          # Core OG generation templates
│   └── og-utils.ts           # Helper functions and metadata
├── pages/
│   └── api/
│       └── og.ts             # API endpoint for dynamic generation
└── layouts/
    └── Layout.astro          # Updated with OG meta tags

scripts/
└── generate-og-images.js     # Build-time static generation

public/
└── og/                       # Generated static images
    ├── homepage.png
    ├── about.png
    ├── services.png
    ├── contact.png
    ├── default-album.png
    └── manifest.json
```

## Usage

### Page Templates
Pages automatically get appropriate OG images by setting the `pageType` prop:

```astro
<Layout 
  title="Page Title"
  pageType="homepage|about|service|contact|album"
  customOGData={{ albumTitle: "...", albumDate: "..." }} // for albums
>
```

### API Endpoint
Dynamic images can be generated via API:
```
GET /api/og?title=Custom%20Title&type=album&subtitle=Wedding%20Photography
```

### Build Process
Static images are generated automatically during build:
```bash
npm run og:generate  # Generate static images
npm run build        # Includes OG generation + site build
```

## Testing Checklist

### Local Testing
- [ ] Visit http://localhost:4323/ and inspect `<head>` for OG meta tags
- [ ] Check static images: http://localhost:4323/og/homepage.png
- [ ] Test dynamic API: http://localhost:4323/api/og?title=Test&type=homepage
- [ ] Verify album pages have dynamic OG images

### Social Media Testing
Use these tools to test how your OG images appear:

1. **Facebook Sharing Debugger**
   - URL: https://developers.facebook.com/tools/debug/
   - Test URLs: homepage, about, services, contact, sample album

2. **Twitter Card Validator**
   - URL: https://cards-dev.twitter.com/validator
   - Test summary_large_image cards

3. **LinkedIn Post Inspector**
   - URL: https://www.linkedin.com/post-inspector/
   - Test professional appearance

4. **Discord/Slack**
   - Paste links in channels to see preview generation

### Performance Testing
- [ ] Check image file sizes (should be < 1MB, ideally < 300KB)
- [ ] Verify caching headers on /api/og endpoint
- [ ] Test generation speed for dynamic images
- [ ] Monitor build time impact

## Dimensions & Specifications

- **Size**: 1200×630 pixels (Facebook/LinkedIn recommended)
- **Format**: PNG for better quality with transparency
- **Aspect Ratio**: 1.91:1 (optimal for most platforms)
- **File Size**: Optimized for web (typically 25-100KB)

## Troubleshooting

### Common Issues

1. **Images not showing in social media**
   - Clear platform caches using debugger tools
   - Check that images are publicly accessible
   - Verify meta tag syntax

2. **Build failing during OG generation**
   - Check that all dependencies are installed
   - Verify React is available for the build script
   - Review console output for specific errors

3. **Dynamic images not generating**
   - Check API endpoint is working: `/api/og?title=test`
   - Verify @vercel/og package is installed
   - Review server logs for errors

4. **Styling issues**
   - Remember: CSS properties must be camelCase in React
   - No units for properties like zIndex
   - Limited CSS support compared to regular web pages

## Customization

### Adding New Templates
1. Update `getTemplate()` function in `og-images.ts`
2. Add new type to `OGImageOptions` interface
3. Update `og-utils.ts` metadata functions
4. Add static generation in build script if needed

### Modifying Colors/Fonts
1. Update color constants in both files
2. Modify font family in baseStyles
3. Regenerate static images: `npm run og:generate`

### Background Images
- For homepage: Update backgroundImage URL in og-utils.ts
- For dynamic content: Pass via API parameters
- Ensure images are accessible and optimized

## SEO Benefits

1. **Improved Click-Through Rates**: Attractive previews increase social media engagement
2. **Brand Consistency**: Professional appearance across all platforms
3. **Better User Experience**: Clear preview of page content
4. **Social Media Algorithm**: Platforms favor content with proper OG images

## Performance Optimizations

1. **Static Generation**: Common pages use pre-built images
2. **Caching**: API responses cached for 1 year
3. **Optimized Sizes**: Images compressed for web delivery
4. **System Fonts**: Faster generation without external font loading