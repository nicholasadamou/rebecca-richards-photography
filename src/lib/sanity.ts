import { createClient } from '@sanity/client'
import imageUrlBuilder from '@sanity/image-url'

// Function to get environment variables that works in both Node.js and Astro
function getEnvVar(key: string, fallback: string = ''): string {
  // In Astro/Vite environment
  if (typeof import.meta !== 'undefined' && import.meta.env) {
    return import.meta.env[key] || fallback
  }
  // In Node.js environment
  return process.env[key] || fallback
}

// Configure the Sanity client
export const sanityClient = createClient({
  projectId: getEnvVar('PUBLIC_SANITY_PROJECT_ID', 'gwf79bj6'),
  dataset: getEnvVar('PUBLIC_SANITY_DATASET', 'production'),
  useCdn: getEnvVar('NODE_ENV') === 'production', // Use CDN in production
  apiVersion: '2023-10-01', // Use current date in YYYY-MM-DD format
  token: getEnvVar('SANITY_API_TOKEN'), // Only needed for mutations
})

// Image URL builder
const builder = imageUrlBuilder(sanityClient)

// Helper function to build Sanity image URLs
export function urlFor(source: any) {
  return builder.image(source)
}

// Query helpers for albums
export const albumQueries = {
  // Get all published albums
  getAllAlbums: `*[_type == "album" && published == true] | order(date desc) {
    _id,
    title,
    slug,
    albumType,
    date,
    description,
    coverImage,
    "imageCount": count(images),
    featured,
    sessionLocation,
    clientNames
  }`,

  // Get single album by slug
  getAlbumBySlug: `*[_type == "album" && slug.current == $slug && published == true][0] {
    _id,
    title,
    slug,
    albumType,
    date,
    description,
    coverImage,
    images[] {
      asset,
      alt,
      hotspot
    },
    featured,
    sessionLocation,
    clientNames
  }`,

  // Get featured albums
  getFeaturedAlbums: `*[_type == "album" && published == true && featured == true] | order(date desc) {
    _id,
    title,
    slug,
    albumType,
    date,
    description,
    coverImage,
    "imageCount": count(images),
    sessionLocation,
    clientNames
  }`,

  // Get all album slugs for static generation
  getAllSlugs: `*[_type == "album" && published == true && defined(slug.current)][].slug.current`
}

// Fetch functions
export async function getAllAlbums(): Promise<any[]> {
  try {
    const albums = await sanityClient.fetch(albumQueries.getAllAlbums)
    return albums || []
  } catch (error) {
    console.error('Error fetching albums:', error)
    return []
  }
}

export async function getAlbumBySlug(slug: string): Promise<any | null> {
  try {
    const album = await sanityClient.fetch(albumQueries.getAlbumBySlug, { slug })
    return album
  } catch (error) {
    console.error('Error fetching album:', error)
    return null
  }
}

export async function getFeaturedAlbums(): Promise<any[]> {
  try {
    const albums = await sanityClient.fetch(albumQueries.getFeaturedAlbums)
    return albums || []
  } catch (error) {
    console.error('Error fetching featured albums:', error)
    return []
  }
}

export async function getAllAlbumSlugs(): Promise<string[]> {
  try {
    const slugs = await sanityClient.fetch(albumQueries.getAllSlugs)
    return slugs || []
  } catch (error) {
    console.error('Error fetching album slugs:', error)
    return []
  }
}
