import {defineConfig} from 'sanity'
import {structureTool} from 'sanity/structure'
import {visionTool} from '@sanity/vision'

// Import your album schema
import {album} from './album-schema'

export default defineConfig({
  name: 'default',
  title: 'Rebecca Richards Photography',

  projectId: process.env.SANITY_STUDIO_PROJECT_ID || 'gwf79bj6',
  dataset: process.env.SANITY_STUDIO_DATASET || 'production',

  plugins: [structureTool(), visionTool()],

  schema: {
    types: [album],
  },

  // Development server configuration
  server: {
    port: 3333, // Use a different port from your Astro app
  },
})
