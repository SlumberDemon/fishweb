import { defineConfig } from "vitepress";

// https://vitepress.dev/reference/site-config
export default defineConfig({
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
          { text: "ASGI App", link: "/content/concepts/asgi" },
          { text: "Static App", link: "/content/concepts/static" },
          { text: "Live editing", link: "/content/concepts/reload" },
          { text: "Entrypoint", link: "/content/concepts/entry" },
          { text: "Virtual environment", link: "/content/concepts/venv" },
        ],
      },
      {
        text: "References",
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
      { icon: "github", link: "https://github.com/slumberdemon/fishweb" },
    ],
  },
});
