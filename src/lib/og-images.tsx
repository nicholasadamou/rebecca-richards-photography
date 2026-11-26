import { ImageResponse } from '@vercel/og'

// Brand colors matching the site
const colors = {
  rose: '#fb7185', // rose-400
  roseDark: '#f43f5e', // rose-500
  gray: '#111827', // gray-900
  grayLight: '#f9fafb', // gray-50
  white: '#ffffff',
  textGray: '#6b7280', // gray-500
}

export interface OGImageOptions {
  title: string
  subtitle?: string
  type?: 'homepage' | 'album' | 'service' | 'about' | 'contact'
  backgroundImage?: string
}

export async function generateOGImage(options: OGImageOptions) {
  const { title, subtitle, type = 'homepage', backgroundImage } = options

  // Get the appropriate template based on type
  const template = getTemplate(type, title, subtitle, backgroundImage)

  return new ImageResponse(template, {
    width: 1200,
    height: 630,
    // Use system fonts for better compatibility and faster loading
  })
}

function getTemplate(type: string, title: string, subtitle?: string, backgroundImage?: string) {
  const baseStyles = {
    width: '100%',
    height: '100%',
    display: 'flex',
    position: 'relative' as const,
    fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    backgroundColor: '#ffffff', // Explicit solid white background
  }

  switch (type) {
    case 'homepage':
      return (
        <div style={baseStyles}>
          {/* Solid Background */}
          <div
            style={{
              position: 'absolute',
              inset: 0,
              backgroundColor: '#f9fafb',
            }}
          />
          
          {/* Left accent bar */}
          <div
            style={{
              position: 'absolute',
              left: 0,
              top: '20%',
              bottom: '20%',
              width: '6px',
              backgroundColor: colors.rose,
            }}
          />

          {/* Content */}
          <div
            style={{
              position: 'relative',
              zIndex: 10,
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'center',
              paddingLeft: '100px',
              paddingRight: '60px',
            }}
          >
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                marginBottom: '30px',
              }}
            >
              <div
                style={{
                  width: '80px',
                  height: '80px',
                  borderRadius: '40px',
                  backgroundColor: '#fce7e9',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginRight: '30px',
                }}
              >
                <svg
                  width="40"
                  height="40"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke={colors.rose}
                  strokeWidth="1.5"
                >
                  <path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"/>
                  <circle cx="12" cy="13" r="3"/>
                </svg>
              </div>
              <h1
                style={{
                  fontSize: '64px',
                  fontWeight: 300,
                  color: colors.gray,
                  letterSpacing: '1px',
                  lineHeight: 1.1,
                }}
              >
                {title}
              </h1>
            </div>
            
            {subtitle && (
              <p
                style={{
                  fontSize: '28px',
                  fontWeight: 300,
                  color: colors.textGray,
                  lineHeight: 1.4,
                  maxWidth: '800px',
                  marginLeft: '110px',
                }}
              >
                {subtitle}
              </p>
            )}
            
            {/* Brand mark */}
            <div
              style={{
                position: 'absolute',
                bottom: '40px',
                right: '40px',
                display: 'flex',
                alignItems: 'center',
                color: colors.textGray,
                fontSize: '18px',
                fontWeight: 300,
              }}
            >
              Rebecca Richards Photography
            </div>
          </div>
        </div>
      )

    case 'album':
      return (
        <div style={baseStyles}>
          {/* Solid Background */}
          <div
            style={{
              position: 'absolute',
              inset: 0,
              backgroundColor: '#ffffff',
            }}
          />
          
          {/* Rose accent bar */}
          <div
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              height: '8px',
              backgroundColor: colors.rose,
            }}
          />

          {/* Content */}
          <div
            style={{
              position: 'relative',
              zIndex: 10,
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'center',
              alignItems: 'center',
              textAlign: 'center',
              padding: '80px 60px',
            }}
          >
            {/* Album icon */}
            <div
              style={{
                width: '120px',
                height: '120px',
                borderRadius: '60px',
                backgroundColor: colors.rose,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginBottom: '40px',
              }}
            >
              <svg
                width="60"
                height="60"
                viewBox="0 0 24 24"
                fill="none"
                stroke="white"
                strokeWidth="1.5"
              >
                <path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"/>
                <circle cx="12" cy="13" r="3"/>
              </svg>
            </div>

            <h1
              style={{
                fontSize: '56px',
                fontWeight: 300,
                lineHeight: 1.1,
                marginBottom: '20px',
                color: colors.gray,
                letterSpacing: '1px',
                maxWidth: '900px',
              }}
            >
              {title}
            </h1>
            {subtitle && (
              <p
                style={{
                  fontSize: '24px',
                  fontWeight: 300,
                  color: colors.textGray,
                  lineHeight: 1.4,
                }}
              >
                {subtitle}
              </p>
            )}
            
            {/* Brand mark */}
            <div
              style={{
                position: 'absolute',
                bottom: '40px',
                left: '40px',
                display: 'flex',
                alignItems: 'center',
                color: colors.textGray,
                fontSize: '18px',
                fontWeight: 300,
              }}
            >
              Rebecca Richards Photography
            </div>
          </div>
        </div>
      )

    case 'service':
    case 'about':
    case 'contact':
      return (
        <div style={baseStyles}>
          {/* Solid Background */}
          <div
            style={{
              position: 'absolute',
              inset: 0,
              backgroundColor: '#ffffff',
            }}
          />
          
          {/* Left accent */}
          <div
            style={{
              position: 'absolute',
              left: 0,
              top: '20%',
              bottom: '20%',
              width: '6px',
              backgroundColor: colors.rose,
            }}
          />

          {/* Content */}
          <div
            style={{
              position: 'relative',
              zIndex: 10,
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'center',
              paddingLeft: '100px',
              paddingRight: '60px',
            }}
          >
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                marginBottom: '30px',
              }}
            >
              <div
                style={{
                  width: '80px',
                  height: '80px',
                  borderRadius: '40px',
                  backgroundColor: '#fce7e9',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginRight: '30px',
                }}
              >
                {getServiceIcon(type)}
              </div>
              <h1
                style={{
                  fontSize: '64px',
                  fontWeight: 300,
                  color: colors.gray,
                  letterSpacing: '1px',
                  lineHeight: 1.1,
                }}
              >
                {title}
              </h1>
            </div>
            
            {subtitle && (
              <p
                style={{
                  fontSize: '28px',
                  fontWeight: 300,
                  color: colors.textGray,
                  lineHeight: 1.4,
                  maxWidth: '800px',
                  marginLeft: '110px',
                }}
              >
                {subtitle}
              </p>
            )}
            
            {/* Brand mark */}
            <div
              style={{
                position: 'absolute',
                bottom: '40px',
                right: '40px',
                display: 'flex',
                alignItems: 'center',
                color: colors.textGray,
                fontSize: '18px',
                fontWeight: 300,
              }}
            >
              Rebecca Richards Photography
            </div>
          </div>
        </div>
      )

    default:
      return getTemplate('homepage', title, subtitle, backgroundImage)
  }
}

function getServiceIcon(type: string) {
  const iconColor = colors.rose
  
  switch (type) {
    case 'service':
      return (
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke={iconColor} strokeWidth="1.5">
          <path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"/>
          <circle cx="12" cy="13" r="3"/>
        </svg>
      )
    case 'about':
      return (
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke={iconColor} strokeWidth="1.5">
          <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
        </svg>
      )
    case 'contact':
      return (
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke={iconColor} strokeWidth="1.5">
          <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
          <polyline points="22,6 12,13 2,6"/>
        </svg>
      )
    default:
      return (
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke={iconColor} strokeWidth="1.5">
          <circle cx="12" cy="12" r="3"/>
          <path d="M12 1v6m0 6v6m11-7h-6m-6 0H1"/>
        </svg>
      )
  }
}

// Note: Using system fonts for better compatibility and faster generation
