#!/usr/bin/env node

/**
 * Test Sanity connection and preview migration data
 */

import fs from 'fs'
import path from 'path'
import { createClient } from '@sanity/client'
import dotenv from 'dotenv'

// Load environment variables
dotenv.config({ path: '.env' })

// Sanity client configuration
const client = createClient({
  projectId: process.env.PUBLIC_SANITY_PROJECT_ID,
  dataset: process.env.PUBLIC_SANITY_DATASET || 'production',
  token: process.env.SANITY_API_TOKEN,
  useCdn: false,
  apiVersion: '2023-01-01'
})

async function testConnection() {
  console.log('🔍 Testing Sanity connection...\n')

  // Validate environment variables
  if (!process.env.PUBLIC_SANITY_PROJECT_ID || !process.env.SANITY_API_TOKEN) {
    console.error('❌ Missing required environment variables.')
    console.error('Please set PUBLIC_SANITY_PROJECT_ID and SANITY_API_TOKEN in .env')
    return false
  }

  console.log(`Project ID: ${process.env.PUBLIC_SANITY_PROJECT_ID}`)
  console.log(`Dataset: ${process.env.PUBLIC_SANITY_DATASET}`)
  console.log(`Token: ${process.env.SANITY_API_TOKEN.substring(0, 10)}...`)

  try {
    // Test API connection
    const projects = await client.request({ url: '/projects' })
    console.log('✅ Successfully connected to Sanity API')

    // Find our project
    const ourProject = projects.find(p => p.id === process.env.PUBLIC_SANITY_PROJECT_ID)
    if (ourProject) {
      console.log(`✅ Found project: ${ourProject.displayName}`)
    }

    return true
  } catch (error) {
    console.error('❌ Failed to connect to Sanity:', error.message)
    return false
  }
}

function analyzeMetadata() {
  console.log('\n📊 Analyzing existing album data...\n')

  const metadataPath = path.join(process.cwd(), 'client-album-scraper', 'scraped_images', 'metadata.json')

  try {
    const metadataRaw = fs.readFileSync(metadataPath, 'utf-8')
    const metadata = JSON.parse(metadataRaw)

    const successfulAlbums = Object.values(metadata.albums)
      .filter(album => album.scraping_success && album.images_downloaded > 0)

    console.log(`📈 Total albums: ${Object.keys(metadata.albums).length}`)
    console.log(`✅ Successful albums: ${successfulAlbums.length}`)
    console.log(`🖼️  Total images: ${successfulAlbums.reduce((sum, album) => sum + album.images_downloaded, 0)}`)

    console.log('\n📋 Albums to be migrated:')
    successfulAlbums.forEach((album, index) => {
      console.log(`  ${index + 1}. ${album.name} (${album.images_downloaded} images)`)
    })

    return successfulAlbums
  } catch (error) {
    console.error('❌ Failed to load metadata.json:', error.message)
    return []
  }
}

async function main() {
  const connected = await testConnection()

  if (!connected) {
    console.log('\n❌ Connection test failed. Please check your credentials.')
    return
  }

  const albums = analyzeMetadata()

  if (albums.length === 0) {
    console.log('\n❌ No albums found to migrate.')
    return
  }

  console.log('\n🚀 Ready to migrate!')
  console.log('\nTo run the full migration, use:')
  console.log('npm run migrate:sanity')
}

main().catch(error => {
  console.error('❌ Test failed:', error)
})
