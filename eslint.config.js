import eslintPluginAstro from 'eslint-plugin-astro';
import eslintConfigPrettier from 'eslint-config-prettier';

export default [
  // Recommended rules for Astro
  ...eslintPluginAstro.configs.recommended,
  {
    // Global settings for all files
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
    },
    rules: {
      // Custom rules
      'no-unused-vars': 'warn',
      'no-console': 'warn',
      'prefer-const': 'error',
      'no-var': 'error',
    },
  },
  {
    // TypeScript/JavaScript specific rules
    files: ['**/*.{js,mjs,cjs,ts,tsx}'],
    rules: {
      'no-undef': 'error',
      'no-unused-vars': 'warn',
      // Allow img tags in React components for dynamic content
      'astro/prefer-image-component': 'off',
    },
  },
  {
    // Astro specific rules
    files: ['**/*.astro'],
    rules: {
      // Allow console in Astro files for server-side logging
      'no-console': 'off',
      // Allow unused vars in Astro frontmatter (common for exported functions)
      'no-unused-vars': 'off',
      // Allow img tags for dynamic content from CMS (Sanity)
      'astro/prefer-image-component': 'off',
    },
  },
  {
    // Ignore certain directories and files
    ignores: [
      'dist/',
      'node_modules/',
      '.astro/',
      'public/',
      'tools/',
      'scripts/',
      '*.config.js',
      '*.config.mjs',
      '*.config.ts',
    ],
  },
  // Disable ESLint rules that conflict with Prettier
  eslintConfigPrettier,
];
