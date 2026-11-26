// Sanity Schema for Client Albums
// Add this to your Sanity Studio's schema files

export const album = {
  name: 'album',
  title: 'Client Album',
  type: 'document',
  fields: [
    {
      name: 'title',
      title: 'Album Title',
      type: 'string',
      validation: Rule => Rule.required()
    },
    {
      name: 'slug',
      title: 'Slug',
      type: 'slug',
      options: {
        source: 'title',
        maxLength: 96
      },
      validation: Rule => Rule.required()
    },
    {
      name: 'albumType',
      title: 'Album Type',
      type: 'string',
      options: {
        list: [
          { title: 'Wedding Photography', value: 'wedding' },
          { title: 'Engagement Session', value: 'engagement' },
          { title: 'Bridal Session', value: 'bridal' },
          { title: 'Family Portrait', value: 'family' },
          { title: 'Maternity Session', value: 'maternity' },
          { title: 'Special Event', value: 'event' },
          { title: 'Graduation', value: 'graduation' },
          { title: 'Portrait Session', value: 'portrait' }
        ]
      }
    },
    {
      name: 'date',
      title: 'Session Date',
      type: 'date'
    },
    {
      name: 'description',
      title: 'Album Description',
      type: 'text',
      rows: 4
    },
    {
      name: 'coverImage',
      title: 'Cover Image',
      type: 'image',
      options: {
        hotspot: true
      }
    },
    {
      name: 'images',
      title: 'Album Images',
      type: 'array',
      of: [
        {
          type: 'image',
          options: {
            hotspot: true
          },
          fields: [
            {
              name: 'alt',
              title: 'Alternative Text',
              type: 'string'
            }
          ]
        }
      ]
    },
    {
      name: 'featured',
      title: 'Featured Album',
      type: 'boolean',
      description: 'Show this album prominently'
    },
    {
      name: 'published',
      title: 'Published',
      type: 'boolean',
      description: 'Only published albums will be visible on the website'
    },
    {
      name: 'sessionLocation',
      title: 'Session Location',
      type: 'string'
    },
    {
      name: 'clientNames',
      title: 'Client Names',
      type: 'array',
      of: [{ type: 'string' }]
    },
    {
      name: 'originalUrl',
      title: 'Original Album URL',
      type: 'url',
      description: 'The original URL from the previous system (for migration reference)'
    },
    {
      name: 'migrationData',
      title: 'Migration Data',
      type: 'object',
      description: 'Data from the original scraping system',
      fields: [
        {
          name: 'cleanName',
          title: 'Original Clean Name',
          type: 'string'
        },
        {
          name: 'imagesDownloaded',
          title: 'Original Images Downloaded Count',
          type: 'number'
        },
        {
          name: 'addedAt',
          title: 'Originally Added At',
          type: 'datetime'
        }
      ]
    }
  ],
  preview: {
    select: {
      title: 'title',
      media: 'coverImage',
      subtitle: 'albumType'
    }
  },
  orderings: [
    {
      title: 'Date (newest first)',
      name: 'dateDesc',
      by: [{ field: 'date', direction: 'desc' }]
    },
    {
      title: 'Date (oldest first)',
      name: 'dateAsc',
      by: [{ field: 'date', direction: 'asc' }]
    },
    {
      title: 'Title A-Z',
      name: 'titleAsc',
      by: [{ field: 'title', direction: 'asc' }]
    }
  ]
};