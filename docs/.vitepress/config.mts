import { defineConfig } from "vitepress";

// https://vitepress.dev/reference/site-config
export default defineConfig({
  base: "/",
  title: "Fishweb",
  description: "Your personal web app manager",
  cleanUrls: true,
  head: [["link", { rel: "icon", href: "/favicon.png" }]],
  themeConfig: {
    logo: "/favicon.png",
    nav: [{ text: "Docs", link: "/content/getting-started" }],
    editLink: {
      pattern: "https://github.com/slumberdemon/fishweb/tree/main/docs/:path",
    },
    sidebar: [
      {
        text: "Introduction",
        items: [{ text: "Getting Started", link: "/content/getting-started" }],
      },
      {
        text: "Concepts",
        items: [
          { text: "ASGI Apps", link: "/content/concepts/asgi" },
          { text: "WSGI Apps", link: "/content/concepts/wsgi" },
          { text: "Static Apps", link: "/content/concepts/static" },
          { text: "Live Reloading", link: "/content/concepts/reload" },
          { text: "Virtual Environments", link: "/content/concepts/venv" },
          { text: "Environment Variables", link: "/content/concepts/env" },
          { text: "Data Storage", link: "/content/concepts/arowana" },
        ],
      },
      {
        text: "Hosting",
        items: [{ text: "Cloudflared", link: "/content/hosting/cloudflared" }],
      },
      {
        text: "Reference",
        items: [
          { text: "App Config", link: "/content/reference/config" },
          { text: "CLI", link: "/content/reference/cli" },
        ],
      },
    ],
    search: {
      provider: "local",
      options: {
        _render: (src, env, md) => {
          if (env.relativePath.startsWith("docs")) {
            return "";
          }

          return md.render(src, env);
        },
      },
    },
    socialLinks: [
      { icon: "bluesky", link: "https://bsky.app/profile/fishweb.sofa.sh" },
      { icon: "github", link: "https://github.com/slumberdemon/fishweb" },
    ],
  },
});
