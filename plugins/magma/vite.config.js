import { fileURLToPath, URL } from "url";

import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    fs: {
      allow: ["../"],
    },
  },
  build: {
    rollupOptions: {
      external: (id) => {
        // Keep branding assets as external URLs (don't bundle them)
        if (id.startsWith('/branding/')) return true;
        if (id.includes('/gui/')) return true;
        return false;
      }
    },
    // Prevent asset inlining for branding files
    assetsInlineLimit: (filePath) => {
      if (filePath.includes('/branding/')) return false;
      return 4096; // default is 4096
    }
  },
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url))
    },
  }
});
