# Sanity CMS Integration

This directory contains the setup for integrating Rebecca Richards Photography with Sanity.io as a headless CMS for managing client albums.

## Setup Instructions

### 1. Create Sanity Project

1. Go to [sanity.io/manage](https://sanity.io/manage)
2. Click "Create project"
3. Choose a project name (e.g., "rebecca-richards-photography")
4. Select a dataset name (usually "production")
5. Note your Project ID

### 2. Set up API Token

1. In your Sanity project dashboard, go to Settings > API
2. Click "Add API Token"
3. Give it a name (e.g., "Migration Script")
4. Set permissions to "Editor" (needed for creating documents)
5. Copy the token

### 3. Configure Environment Variables

1. Copy your Project ID and API Token
2. Update `.env.local` in your project root:

```bash
SANITY_PROJECT_ID=your-project-id-here
SANITY_DATASET=production
SANITY_API_TOKEN=your-api-token-here
```

### 4. Set up Sanity Studio

1. Create a new Sanity Studio project or add the album schema to your existing studio
2. Add the schema from `album-schema.js` to your studio's schema files
3. Deploy your studio to manage content

### 5. Run Migration

Once everything is configured, run the migration script:

```bash
npm run migrate:sanity
```

This script will:
- Read your existing `metadata.json` file
- Upload images to Sanity's asset system (first 20 images per album to start)
- Create album documents with proper metadata
- Set up proper relationships between albums and images

## Schema Structure

The album schema includes:

- **title**: Album name
- **slug**: URL-friendly identifier
- **albumType**: Category (wedding, engagement, family, etc.)
- **date**: Session date
- **description**: Generated description based on album type
- **coverImage**: Featured image for the album
- **images**: Array of all album images
- **published**: Whether the album is live on the website
- **featured**: Whether to highlight the album
- **sessionLocation**: Where the session took place
- **clientNames**: Names extracted from album titles

## Next Steps

After migration:

1. **Verify Data**: Check your Sanity Studio to ensure albums were created correctly
2. **Update Astro Pages**: Modify your Astro components to fetch data from Sanity instead of local JSON
3. **Set up Webhooks**: Configure automatic site rebuilds when content changes in Sanity
4. **Client Training**: Show Rebecca how to use Sanity Studio to manage albums

## Advantages

- **No GitHub Storage**: Images are stored in Sanity's CDN, not in your repository
- **Easy Management**: Rebecca can easily upload new albums and images
- **Automatic Optimization**: Sanity handles image resizing and optimization
- **Real-time Updates**: Content changes can trigger automatic site rebuilds
- **Professional Interface**: Clean, intuitive content management interface

## API Usage

Once set up, you can query albums from Astro using:

```javascript
import { createClient } from '@sanity/client'

const client = createClient({
  projectId: 'your-project-id',
  dataset: 'production',
  useCdn: true,
  apiVersion: '2023-01-01'
})

// Get all published albums
const albums = await client.fetch(`
  *[_type == "album" && published == true] | order(date desc) {
    title,
    slug,
    albumType,
    date,
    description,
    coverImage,
    "imageCount": length(images),
    sessionLocation
  }
`)
```