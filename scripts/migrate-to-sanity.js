#!/usr/bin/env node

/**
 * Multi-threaded Migration script with concurrent image uploads
 *
 * Features:
 * - Concurrent image uploads (configurable thread pool)
 * - Uploads ALL images with smart rate limiting
 * - Skips duplicate images automatically
 * - Progress tracking with real-time statistics
 * - Resumable migration (can run multiple times safely)
 * - Much faster than sequential version
 *
 * Usage:
 * 1. Set your Sanity credentials in .env.local
 * 2. Run: node scripts/migrate-to-sanity-concurrent.js
 */

import fs from 'fs'
import path from 'path'
import { createClient } from '@sanity/client'
import dotenv from 'dotenv'
import { Worker, isMainThread, parentPort, workerData } from 'worker_threads'
import os from 'os'

// Load environment variables
dotenv.config() // Also try default .env

// Configuration
const MAX_CONCURRENT_UPLOADS = Math.min(os.cpus().length * 2, 8) // Use CPU cores * 2, max 8
const RATE_LIMIT_DELAY = 100 // ms between requests per worker
const BATCH_SIZE = 20 // Process images in batches

// Sanity client configuration
const client = createClient({
  projectId: process.env.PUBLIC_SANITY_PROJECT_ID || process.env.SANITY_PROJECT_ID || 'wjbho9cg',
  dataset: process.env.PUBLIC_SANITY_DATASET || process.env.SANITY_DATASET || 'production',
  token: process.env.SANITY_API_TOKEN,
  useCdn: false,
  apiVersion: '2023-10-01'
})

// Helper functions (same as before but extracted for reuse)
function getAlbumType(name) {
  const nameLower = name.toLowerCase()
  if (nameLower.includes('engagement')) return 'engagement'
  if (nameLower.includes('wedding')) return 'wedding'
  if (nameLower.includes('bridal')) return 'bridal'
  if (nameLower.includes('family')) return 'family'
  if (nameLower.includes('maternity') || nameLower.includes('maternit')) return 'maternity'
  if (nameLower.includes('baby') || nameLower.includes('shower')) return 'event'
  if (nameLower.includes('grad')) return 'graduation'
  return 'portrait'
}

function parseNames(albumName) {
  const cleanName = albumName
    .replace(/\s+(engagement|wedding|bridal|session|photography|photos?|album)$/gi, '')
    .replace(/['']s\s/g, ' ')
    .trim()

  let names = []
  if (cleanName.includes(' & ')) {
    names = cleanName.split(' & ').map(n => n.trim())
  } else if (cleanName.includes(' and ')) {
    names = cleanName.split(' and ').map(n => n.trim())
  } else if (cleanName.includes('-') && !cleanName.match(/^[a-z-]+$/)) {
    names = cleanName.split('-').map(n => n.trim())
  } else {
    const words = cleanName.split(' ').filter(w => w.length > 0)
    if (words.length >= 2) {
      names = [words[0], words[1]]
    } else if (words.length === 1) {
      names = [words[0]]
    }
  }

  return names.filter(name => name && name.length > 0)
}

function parseDate(dateString) {
  if (!dateString) return null

  const cleanDate = dateString.replace(/Rebecca Richards Photography|View Photos/gi, '').trim()

  try {
    const date = new Date(cleanDate)
    if (!isNaN(date.getTime())) {
      return date.toISOString().split('T')[0]
    }
  } catch {}

  return null
}

function generateSlug(name) {
  return name
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)/g, '')
}

function getSessionLocation() {
  const possibleLocations = [
    'Historic Downtown',
    'Riverside Park',
    'Garden District',
    'Scenic Overlook',
    'Urban Setting',
    'Natural Setting',
    'Waterfront Location',
    'Countryside Setting'
  ]
  return possibleLocations[Math.floor(Math.random() * possibleLocations.length)]
}

function generateDescription(album, albumType) {
  const names = parseNames(album.name)
  const firstName = names[0] || 'The client'
  const secondName = names[1] || null

  const descriptions = {
    engagement: secondName
      ? `${firstName} and ${secondName}'s engagement session was a beautiful celebration of their love story. The natural chemistry and joy between them created the perfect atmosphere for capturing authentic moments that truly reflect their connection.`
      : 'This engagement session was a beautiful celebration of love and connection. The natural chemistry and joy captured created the perfect atmosphere for authentic moments.',

    wedding: secondName
      ? `${firstName} and ${secondName}'s wedding day was filled with love, laughter, and unforgettable moments. From the intimate getting-ready moments to the celebration with family and friends, every detail was perfectly captured.`
      : 'This wedding day was filled with love, laughter, and unforgettable moments. From the intimate getting-ready moments to the celebration with family and friends, every detail was perfectly captured.',

    bridal: `${firstName}'s bridal session was an elegant celebration of this special milestone. The session captured the beauty, grace, and excitement of the bride-to-be.`,

    family: names.length > 0 && !names[0].toLowerCase().includes('family')
      ? `The ${firstName} family session was filled with genuine laughter, love, and connection. These portraits capture the unique bond and personality of each family member.`
      : 'This family session was filled with genuine laughter, love, and connection. These portraits capture the unique bond and personality of each family member.',

    maternity: 'This maternity session beautifully captured the anticipation and joy of expecting a new little one. The glowing expectant mother and the love of the growing family created the perfect atmosphere.',

    event: 'This special celebration was filled with joy, laughter, and meaningful moments shared with loved ones. Every photograph captures the essence of this memorable occasion.',

    graduation: 'This graduation session celebrated an incredible achievement and milestone. The portraits capture the pride, joy, and excitement of this significant accomplishment.',

    portrait: 'This portrait session was designed to capture authentic moments and genuine expressions. The relaxed atmosphere allowed for natural interactions.'
  }

  return descriptions[albumType] || descriptions.portrait
}

// Worker thread for image processing
if (!isMainThread) {
  const { images, albumName, projectId, dataset, token } = workerData

  const workerClient = createClient({
    projectId,
    dataset,
    token,
    useCdn: false,
    apiVersion: '2023-10-01'
  })

  async function checkExistingAsset(filename, imageBuffer) {
    try {
      const query = '*[_type == "sanity.imageAsset" && originalFilename == $filename][0]'
      const existingAsset = await workerClient.fetch(query, { filename })

      if (existingAsset && existingAsset.size === imageBuffer.length) {
        return {
          _type: 'image',
          asset: {
            _type: 'reference',
            _ref: existingAsset._id
          }
        }
      }
      return null
    } catch {
      return null
    }
  }

  async function uploadImage(imagePath, filename, albumName) {
    try {
      const imageBuffer = fs.readFileSync(imagePath)

      // Check if exists
      const existingAsset = await checkExistingAsset(filename, imageBuffer)
      if (existingAsset) {
        return {
          ...existingAsset,
          wasSkipped: true,
          filename
        }
      }

      // Upload new
      const asset = await workerClient.assets.upload('image', imageBuffer, {
        filename: filename,
        title: `${albumName} - ${filename}`,
        description: `Photo from ${albumName} album`
      })

      return {
        _type: 'image',
        asset: {
          _type: 'reference',
          _ref: asset._id
        },
        wasSkipped: false,
        filename
      }
    } catch (error) {
      return { error: error.message, filename }
    }
  }

  // Process images assigned to this worker
  async function processImages() {
    const results = []

    for (const imageInfo of images) {
      const result = await uploadImage(imageInfo.path, imageInfo.filename, albumName)
      results.push(result)

      // Report progress back to main thread
      parentPort.postMessage({
        type: 'progress',
        filename: imageInfo.filename,
        success: !result.error,
        skipped: result.wasSkipped
      })

      // Rate limiting
      await new Promise(resolve => setTimeout(resolve, RATE_LIMIT_DELAY))
    }

    parentPort.postMessage({ type: 'complete', results })
  }

  processImages().catch(error => {
    parentPort.postMessage({ type: 'error', error: error.message })
  })
} else {
  // Main thread - orchestrates the workers

  async function checkExistingAlbum(albumName, slug) {
    try {
      const query = '*[_type == "album" && (title == $title || slug.current == $slug)][0]'
      const existingAlbum = await client.fetch(query, { title: albumName, slug })
      return existingAlbum
    } catch (error) {
      return null
    }
  }

  function chunkArray(array, chunkSize) {
    const chunks = []
    for (let i = 0; i < array.length; i += chunkSize) {
      chunks.push(array.slice(i, i + chunkSize))
    }
    return chunks
  }

  async function uploadImagesWithWorkers(imageFiles, albumDir, albumName) {
    return new Promise((resolve, reject) => {
      // Prepare image data
      const images = imageFiles.map(file => ({
        filename: file,
        path: path.join(albumDir, file)
      }))

      // Split images into chunks for workers
      const chunks = chunkArray(images, Math.ceil(images.length / MAX_CONCURRENT_UPLOADS))
      const workers = []
      const results = []
      let completedWorkers = 0
      let totalUploaded = 0
      let totalSkipped = 0
      let totalFailed = 0

      console.log(`    🚀 Starting ${chunks.length} workers for ${images.length} images...`)

      // Create workers
      for (let i = 0; i < chunks.length; i++) {
        if (chunks[i].length === 0) continue

        const worker = new Worker(import.meta.filename, {
          workerData: {
            images: chunks[i],
            albumName,
            projectId: process.env.PUBLIC_SANITY_PROJECT_ID || process.env.SANITY_PROJECT_ID || 'wjbho9cg',
            dataset: process.env.PUBLIC_SANITY_DATASET || process.env.SANITY_DATASET || 'production',
            token: process.env.SANITY_API_TOKEN
          }
        })

        worker.on('message', (message) => {
          if (message.type === 'progress') {
            if (message.success) {
              if (message.skipped) {
                totalSkipped++
                process.stdout.write('↻')
              } else {
                totalUploaded++
                process.stdout.write('✓')
              }
            } else {
              totalFailed++
              process.stdout.write('✗')
            }

            // Show progress every 20 images
            const total = totalUploaded + totalSkipped + totalFailed
            if (total % 20 === 0 || total === images.length) {
              console.log(`\n      Progress: ${total}/${images.length} (↑${totalUploaded} ↻${totalSkipped} ✗${totalFailed})`)
            }
          } else if (message.type === 'complete') {
            results.push(...message.results)
            completedWorkers++

            if (completedWorkers === chunks.length) {
              console.log(`\n    📊 Upload summary: ${totalUploaded} uploaded, ${totalSkipped} skipped, ${totalFailed} failed`)

              // Process results for Sanity format
              const uploadedImages = results
                .filter(r => !r.error)
                .map((r, i) => ({
                  ...r,
                  alt: `${albumName} - Photo ${i + 1}`,
                  _key: `image-${i}`
                }))

              resolve(uploadedImages)
            }
          } else if (message.type === 'error') {
            reject(new Error(message.error))
          }
        })

        worker.on('error', reject)
        workers.push(worker)
      }
    })
  }

  async function migrateAlbum(album) {
    console.log(`\n📁 Migrating album: ${album.name}`)

    // Get album images
    const albumDir = path.join(process.cwd(), 'client-album-scraper', 'scraped_images', album.clean_name)
    let imageFiles = []

    try {
      const files = fs.readdirSync(albumDir)
      imageFiles = files.filter(file => file.toLowerCase().match(/\.(jpg|jpeg|png|webp)$/))
    } catch (error) {
      console.warn(`  ⚠ Could not read album directory: ${albumDir}`)
      return null
    }

    console.log(`  📊 Processing ${imageFiles.length} images with ${MAX_CONCURRENT_UPLOADS} workers...`)

    // Upload images concurrently
    let uploadedImages
    try {
      uploadedImages = await uploadImagesWithWorkers(imageFiles, albumDir, album.name)
    } catch (error) {
      console.error(`  ✗ Failed to upload images:`, error.message)
      return null
    }

    if (uploadedImages.length === 0) {
      console.warn(`  ⚠ No images processed for ${album.name}`)
      return null
    }

    // Create/update album document (same as before)
    const albumType = getAlbumType(album.name)
    const names = parseNames(album.name)
    const sessionDate = parseDate(album.date)
    const slug = generateSlug(album.name)
    const description = generateDescription(album, albumType)

    const existingAlbum = await checkExistingAlbum(album.name, slug)

    const albumDoc = {
      _type: 'album',
      title: album.name,
      slug: {
        _type: 'slug',
        current: slug
      },
      albumType: albumType,
      date: sessionDate,
      description: description,
      coverImage: uploadedImages[0],
      images: uploadedImages,
      featured: existingAlbum ? existingAlbum.featured || false : false,
      published: existingAlbum ? existingAlbum.published !== false : true,
      sessionLocation: existingAlbum ? existingAlbum.sessionLocation || getSessionLocation() : getSessionLocation(),
      clientNames: names,
      originalUrl: album.url,
      migrationData: {
        cleanName: album.clean_name,
        imagesDownloaded: album.images_downloaded,
        addedAt: album.added_at ? new Date(album.added_at).toISOString() : null
      }
    }

    try {
      let result
      if (existingAlbum) {
        result = await client.patch(existingAlbum._id).set(albumDoc).commit()
        console.log(`  ✓ Updated existing album: ${result._id}`)
      } else {
        result = await client.create(albumDoc)
        console.log(`  ✓ Created new album: ${result._id}`)
      }
      return result
    } catch (error) {
      console.error(`  ✗ Failed to ${existingAlbum ? 'update' : 'create'} album:`, error.message)
      return null
    }
  }

  async function main() {
    console.log('🚀 Starting CONCURRENT Sanity migration...\n')

    // Validate environment variables
    const projectId = process.env.PUBLIC_SANITY_PROJECT_ID || process.env.SANITY_PROJECT_ID
    const apiToken = process.env.SANITY_API_TOKEN

    if (!projectId || !apiToken) {
      console.error('❌ Missing required environment variables:')
      console.error('  PUBLIC_SANITY_PROJECT_ID or SANITY_PROJECT_ID (current:', projectId || 'missing', ')')
      console.error('  SANITY_API_TOKEN (', apiToken ? 'present' : 'missing', ')')
      console.error('\nPlease check your .env file or copy from .env.example')
      process.exit(1)
    }

    // Load metadata
    const metadataPath = path.join(process.cwd(), 'client-album-scraper', 'scraped_images', 'metadata.json')
    let metadata

    try {
      const metadataRaw = fs.readFileSync(metadataPath, 'utf-8')
      metadata = JSON.parse(metadataRaw)
    } catch (error) {
      console.error('❌ Failed to load metadata.json:', error.message)
      process.exit(1)
    }

    const successfulAlbums = Object.values(metadata.albums)
      .filter(album => album.scraping_success && album.images_downloaded > 0)
      .sort((a, b) => a.name.localeCompare(b.name))

    console.log(`Found ${successfulAlbums.length} albums to migrate`)
    console.log(`Total images: ${successfulAlbums.reduce((sum, album) => sum + album.images_downloaded, 0)}`)
    console.log(`\n⚡ CONCURRENT features:`)
    console.log(`  • ${MAX_CONCURRENT_UPLOADS} concurrent workers`)
    console.log(`  • Smart rate limiting (${RATE_LIMIT_DELAY}ms per request)`)
    console.log(`  • Real-time progress indicators`)
    console.log(`  • Automatic duplicate detection`)
    console.log(`  • Much faster than sequential processing!`)

    const results = []
    const startTime = Date.now()

    for (let i = 0; i < successfulAlbums.length; i++) {
      const album = successfulAlbums[i]
      console.log(`\n[${i + 1}/${successfulAlbums.length}] Processing: ${album.name} (${album.images_downloaded} images)`)

      const albumStartTime = Date.now()
      const result = await migrateAlbum(album)
      const albumTime = Math.round((Date.now() - albumStartTime) / 1000)

      if (result) {
        results.push(result)
        console.log(`  ⏱️ Album completed in ${albumTime}s (${Math.round(album.images_downloaded/albumTime)} img/s)`)
      }
    }

    const totalTime = Math.round((Date.now() - startTime) / 1000)
    const totalImages = successfulAlbums.reduce((sum, album) => sum + album.images_downloaded, 0)

    console.log(`\n✅ CONCURRENT Migration complete!`)
    console.log(`📊 Performance Results:`)
    console.log(`  • Albums: ${results.length}/${successfulAlbums.length}`)
    console.log(`  • Images: ${totalImages}`)
    console.log(`  • Time: ${totalTime}s (${Math.round(totalTime/60)} minutes)`)
    console.log(`  • Speed: ${Math.round(totalImages/totalTime)} images/second`)
    console.log(`  • Workers: ${MAX_CONCURRENT_UPLOADS} concurrent threads`)

    if (results.length > 0) {
      console.log('\n📝 Next steps:')
      console.log('1. Verify albums in Sanity Studio')
      console.log('2. Update Astro pages to use Sanity API')
      console.log('3. Set up webhooks for auto-rebuilds')
    }
  }

  main().catch(error => {
    console.error('❌ Migration failed:', error)
    process.exit(1)
  })
}
