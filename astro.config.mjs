// @ts-check
import { defineConfig } from 'astro/config';
import react from '@astrojs/react';
import sitemap from '@astrojs/sitemap';

import tailwindcss from '@tailwindcss/vite';

// https://astro.build/config
export default defineConfig({
  site: 'https://rebecca-richards-photography.vercel.app',
  integrations: [
    react(),
    sitemap({
      changefreq: 'weekly',
      priority: 0.7,
      lastmod: new Date(),
      entryLimit: 10000,
      // Custom filter to include all pages
      filter: (page) => {
        // Include all pages except API routes
        return !page.includes('/api/') && !page.includes('/og-preview');
      },
      // Custom serializer for better control
      serialize: (item) => {
        // Homepage gets highest priority
        if (item.url.endsWith('/') || item.url === 'https://rebecca-richards-photography.vercel.app') {
          return {
            ...item,
            priority: 1.0,
            changefreq: 'weekly'
          };
        }
        // Album pages get high priority
        if (item.url.includes('/albums/')) {
          return {
            ...item,
            priority: 0.8,
            changefreq: 'monthly'
          };
        }
        // Main pages get medium-high priority
        if (item.url.includes('/about') ||
            item.url.includes('/services') ||
            item.url.includes('/contact') ||
            item.url.includes('/client-albums')) {
          return {
            ...item,
            priority: 0.9,
            changefreq: 'monthly'
          };
        }
        return item;
      }
    })
  ],
  vite: {
    plugins: [tailwindcss()],
    build: {
	  rollupOptions: {
	     external: ['@typescript-eslint/prefer-astro-image']
	  }
    }
  }
});
