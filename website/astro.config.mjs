import { defineConfig } from 'astro/config';
import vue from '@astrojs/vue';
import sitemap from '@astrojs/sitemap';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

export default defineConfig({
  site: 'https://evmore.cryptuon.com',
  output: 'static',
  build: {
    format: 'directory',
  },
  integrations: [
    vue({
      appEntrypoint: '/src/vue-app',
    }),
    sitemap({
      filter: (page) => !page.includes('/app/'),
    }),
  ],
  vite: {
    resolve: {
      alias: {
        '@': path.resolve(__dirname, '../frontend/src'),
      },
    },
  },
});
