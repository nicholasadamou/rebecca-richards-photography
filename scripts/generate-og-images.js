import { promises as fs } from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'
import { ImageResponse } from '@vercel/og'
import React from 'react'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

// Load Rebecca's minified image data URI
let aboutImageDataUri = null
try {
  const dataUriPath = path.join(__dirname, 'about-image-datauri.txt')
  aboutImageDataUri = await fs.readFile(dataUriPath, 'utf8')
  console.log('✅ Loaded Rebecca\'s actual photo for about page OG image')
  console.log(`📏 Data URI length: ${aboutImageDataUri.length} characters`)
} catch (error) {
  console.warn('⚠️  Could not load Rebecca\'s photo, using placeholder')
  console.error(error)
  aboutImageDataUri = null
}

const aboutImageUrl = aboutImageDataUri || 'https://images.unsplash.com/photo-1594736797933-d0501ba2fe65?w=600&h=800&fit=crop&crop=faces&crop=center'

/**
 * Pre-generate static OG images for better performance
 * This script generates commonly needed OG images during build time
 */
async function generateStaticOGImages() {
  try {
    console.log('🎨 Generating static OG images...')

    // Ensure the public/og directory exists
    const ogDir = path.join(__dirname, '..', 'public', 'og')
    await fs.mkdir(ogDir, { recursive: true })

    // Create inline OG generation function to avoid JSX issues
    const generateOGImage = async (options) => {
      const { title, subtitle, type = 'homepage' } = options
      
      // Brand colors matching the site
      const colors = {
        rose: '#fb7185',
        roseDark: '#f43f5e',
        gray: '#111827',
        grayLight: '#f9fafb',
        white: '#ffffff',
        textGray: '#6b7280',
      }

      const baseStyles = {
        width: '100%',
        height: '100%',
        display: 'flex',
        position: 'relative',
        fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
        backgroundColor: '#ffffff',
      }

      let template
      
      if (type === 'homepage') {
        template = React.createElement('div', { style: baseStyles },
          // Solid Background
          React.createElement('div', {
            style: {
              position: 'absolute',
              inset: 0,
              backgroundColor: colors.grayLight,
            }
          }),
          // Left accent bar
          React.createElement('div', {
            style: {
              position: 'absolute',
              left: 0,
              top: '20%',
              bottom: '20%',
              width: '6px',
              backgroundColor: colors.rose,
            }
          }),
          // Content
          React.createElement('div', {
            style: {
              position: 'relative',
              zIndex: 10,
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'center',
              paddingLeft: '100px',
              paddingRight: '60px',
            }
          },
            React.createElement('div', {
              style: {
                display: 'flex',
                alignItems: 'center',
                marginBottom: '30px',
              }
            },
              React.createElement('div', {
                style: {
                  width: '80px',
                  height: '80px',
                  borderRadius: '40px',
                  backgroundColor: '#fce7e9',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginRight: '30px',
                }
              },
                // Camera icon
                React.createElement('svg', {
                  width: '40',
                  height: '40',
                  viewBox: '0 0 24 24',
                  fill: 'none',
                  stroke: colors.rose,
                  strokeWidth: '1.5'
                },
                  React.createElement('path', {
                    d: 'M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z'
                  }),
                  React.createElement('circle', {
                    cx: '12',
                    cy: '13',
                    r: '3'
                  })
                )
              ),
              React.createElement('h1', {
                style: {
                  fontSize: '64px',
                  fontWeight: 300,
                  color: colors.gray,
                  letterSpacing: '1px',
                  lineHeight: 1.1,
                }
              }, title)
            ),
            subtitle && React.createElement('p', {
              style: {
                fontSize: '28px',
                fontWeight: 300,
                color: colors.textGray,
                lineHeight: 1.4,
                maxWidth: '800px',
                marginLeft: '110px',
              }
            }, subtitle)
          ),
          // Brand mark in bottom right
          React.createElement('div', {
            style: {
              position: 'absolute',
              bottom: '40px',
              right: '40px',
              color: colors.textGray,
              fontSize: '18px',
              fontWeight: 300,
            }
          }, 'Rebecca Richards Photography')
        )
      } else if (type === 'about') {
        // Special about template with Rebecca's photo
        template = React.createElement('div', { style: baseStyles },
          // Solid Background
          React.createElement('div', {
            style: {
              position: 'absolute',
              inset: 0,
              backgroundColor: colors.white,
            }
          }),
          // Left side with Rebecca's photo
          React.createElement('div', {
            style: {
              position: 'absolute',
              left: 0,
              top: 0,
              bottom: 0,
              width: '45%',
              backgroundImage: aboutImageDataUri ? `url(${aboutImageDataUri})` : `url(${aboutImageUrl})`,
              backgroundSize: 'cover',
              backgroundPosition: 'center bottom',
              backgroundRepeat: 'no-repeat',
            }
          }),
          // Subtle overlay on photo
          React.createElement('div', {
            style: {
              position: 'absolute',
              left: 0,
              top: 0,
              bottom: 0,
              width: '45%',
              backgroundColor: 'rgba(251, 113, 133, 0.1)',
            }
          }),
          // Right side content
          React.createElement('div', {
            style: {
              position: 'relative',
              zIndex: 10,
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'center',
              marginLeft: '50%',
              padding: '80px 60px 80px 40px',
            }
          },
            React.createElement('h1', {
              style: {
                fontSize: '72px',
                fontWeight: 300,
                color: colors.gray,
                letterSpacing: '2px',
                lineHeight: 1.0,
                marginBottom: '30px',
              }
            }, title),
            subtitle && React.createElement('p', {
              style: {
                fontSize: '26px',
                fontWeight: 300,
                color: colors.textGray,
                lineHeight: 1.4,
                marginBottom: '40px',
              }
            }, subtitle),
            // Decorative element
            React.createElement('div', {
              style: {
                width: '80px',
                height: '3px',
                background: colors.rose,
              }
            })
          ),
          // Brand mark in bottom right
          React.createElement('div', {
            style: {
              position: 'absolute',
              bottom: '40px',
              right: '40px',
              color: colors.textGray,
              fontSize: '18px',
              fontWeight: 300,
            }
          }, 'Rebecca Richards Photography')
        )
      } else {
        // Default template for other types
        template = React.createElement('div', { style: baseStyles },
          React.createElement('div', {
            style: {
              position: 'absolute',
              inset: 0,
              backgroundColor: colors.white,
            }
          }),
          React.createElement('div', {
            style: {
              position: 'absolute',
              left: 0,
              top: '20%',
              bottom: '20%',
              width: '6px',
              backgroundColor: colors.rose,
            }
          }),
          React.createElement('div', {
            style: {
              position: 'relative',
              zIndex: 10,
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'center',
              paddingLeft: '100px',
              paddingRight: '60px',
            }
          },
            React.createElement('div', {
              style: {
                display: 'flex',
                alignItems: 'center',
                marginBottom: '30px',
              }
            },
              React.createElement('div', {
                style: {
                  width: '80px',
                  height: '80px',
                  borderRadius: '40px',
                  backgroundColor: '#fce7e9',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginRight: '30px',
                }
              },
                // Service-specific icons
                type === 'service' ? React.createElement('svg', {
                  width: '40',
                  height: '40',
                  viewBox: '0 0 24 24',
                  fill: 'none',
                  stroke: colors.rose,
                  strokeWidth: '1.5'
                },
                  React.createElement('path', {
                    d: 'M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z'
                  }),
                  React.createElement('circle', {
                    cx: '12',
                    cy: '13',
                    r: '3'
                  })
                ) : type === 'contact' ? React.createElement('svg', {
                  width: '40',
                  height: '40',
                  viewBox: '0 0 24 24',
                  fill: 'none',
                  stroke: colors.rose,
                  strokeWidth: '1.5'
                },
                  React.createElement('path', {
                    d: 'M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z'
                  }),
                  React.createElement('polyline', {
                    points: '22,6 12,13 2,6'
                  })
                ) : React.createElement('svg', {
                  width: '40',
                  height: '40',
                  viewBox: '0 0 24 24',
                  fill: 'none',
                  stroke: colors.rose,
                  strokeWidth: '1.5'
                },
                  React.createElement('path', {
                    d: 'M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z'
                  }),
                  React.createElement('circle', {
                    cx: '12',
                    cy: '13',
                    r: '3'
                  })
                )
              ),
              React.createElement('h1', {
                style: {
                  fontSize: '64px',
                  fontWeight: 300,
                  color: colors.gray,
                  letterSpacing: '1px',
                  lineHeight: 1.1,
                }
              }, title)
            ),
            subtitle && React.createElement('p', {
              style: {
                fontSize: '28px',
                fontWeight: 300,
                color: colors.textGray,
                lineHeight: 1.4,
                maxWidth: '800px',
                marginLeft: '110px',
              }
            }, subtitle),
          ),
          // Brand mark in bottom right
          React.createElement('div', {
            style: {
              position: 'absolute',
              bottom: '40px',
              right: '40px',
              color: colors.textGray,
              fontSize: '18px',
              fontWeight: 300,
            }
          }, 'Rebecca Richards Photography')
        )
      }

      return new ImageResponse(template, {
        width: 1200,
        height: 630,
      })
    }

    // Define static images to generate
    const staticImages = [
      {
        filename: 'homepage.png',
        options: {
          title: 'Capturing Love Stories',
          subtitle: 'Pennsylvania Wedding Photographer specializing in authentic, timeless moments',
          type: 'homepage',
          backgroundImage: '/images/hero.jpg',
        }
      },
      {
        filename: 'about.png',
        options: {
          title: 'About Rebecca',
          subtitle: 'Pennsylvania wedding photographer with a passion for authentic storytelling',
          type: 'about',
        }
      },
      {
        filename: 'services.png',
        options: {
          title: 'Photography Services',
          subtitle: 'Comprehensive photography services for your most important moments',
          type: 'service',
        }
      },
      {
        filename: 'contact.png',
        options: {
          title: 'Get in Touch',
          subtitle: "Let's create something beautiful together",
          type: 'contact',
        }
      },
      {
        filename: 'default-album.png',
        options: {
          title: 'Wedding Album',
          subtitle: 'Wedding Photography',
          type: 'album',
        }
      }
    ]

    // Generate each image
    for (const image of staticImages) {
      try {
        console.log(`  📸 Generating ${image.filename}...`)
        
        const imageResponse = await generateOGImage(image.options)
        const arrayBuffer = await imageResponse.arrayBuffer()
        const buffer = Buffer.from(arrayBuffer)
        
        const filePath = path.join(ogDir, image.filename)
        await fs.writeFile(filePath, buffer)
        
        console.log(`  ✅ Generated ${image.filename} (${(buffer.length / 1024).toFixed(1)}kb)`)
      } catch (error) {
        console.error(`  ❌ Failed to generate ${image.filename}:`, error)
      }
    }

    console.log('🎉 Static OG images generated successfully!')

    // Generate a manifest file for reference
    const manifest = {
      generatedAt: new Date().toISOString(),
      images: staticImages.map(img => ({
        filename: img.filename,
        url: `/og/${img.filename}`,
        type: img.options.type,
        title: img.options.title,
      }))
    }

    await fs.writeFile(
      path.join(ogDir, 'manifest.json'),
      JSON.stringify(manifest, null, 2)
    )

    console.log('📄 Generated OG images manifest')

  } catch (error) {
    console.error('❌ Failed to generate static OG images:', error)
    process.exit(1)
  }
}

// Run the script
generateStaticOGImages()