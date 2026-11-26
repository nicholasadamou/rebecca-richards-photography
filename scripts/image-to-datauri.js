import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

/**
 * Convert local image to data URI for embedding in OG images
 */
function imageToDataUri(imagePath, maxSize = 100000) {
  try {
    const fullPath = path.join(__dirname, '..', imagePath)
    const imageBuffer = fs.readFileSync(fullPath)
    const ext = path.extname(imagePath).toLowerCase()
    
    // If the image is too large, we'll need to use a different approach
    if (imageBuffer.length > maxSize) {
      console.warn(`Image ${imagePath} is ${imageBuffer.length} bytes, which may be too large for OG generation`)
      console.log('Consider using a smaller/compressed version for OG images')
    }
    
    let mimeType = 'image/jpeg'
    if (ext === '.png') mimeType = 'image/png'
    if (ext === '.gif') mimeType = 'image/gif'
    if (ext === '.webp') mimeType = 'image/webp'
    
    const base64 = imageBuffer.toString('base64')
    return `data:${mimeType};base64,${base64}`
  } catch (error) {
    console.error(`Error converting ${imagePath} to data URI:`, error)
    return null
  }
}

// Convert the minified about image
const aboutImageDataUri = imageToDataUri('public/images/about-og.jpg')

if (aboutImageDataUri) {
  console.log('About image data URI generated successfully')
  // Write to a file for use in the OG generation script
  const outputPath = path.join(__dirname, 'about-image-datauri.txt')
  fs.writeFileSync(outputPath, aboutImageDataUri)
  console.log(`Data URI saved to: ${outputPath}`)
  console.log(`Data URI length: ${aboutImageDataUri.length} characters`)
} else {
  console.error('Failed to generate data URI for about image')
}

export { imageToDataUri }