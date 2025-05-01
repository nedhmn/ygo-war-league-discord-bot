// @ts-check
import { defineConfig } from "astro/config";
import starlight from "@astrojs/starlight";

// https://astro.build/config
export default defineConfig({
  site: "https://nedhmn.github.io",
  base: "/ygo-war-league-discord-bot/",
  integrations: [
    starlight({
      title: "YGO War League Bot",
      social: [
        {
          icon: "github",
          label: "GitHub",
          href: "https://github.com/nedhmn/ygo-war-league-discord-bot",
        },
      ],
      sidebar: [
        {
          label: "Getting Started",
          items: [
            { label: "Introduction", slug: "getting-started/overview" },
            { label: "Installation", slug: "getting-started/installation" },
            { label: "Configuration", slug: "getting-started/configuration" },
            {
              label: "Running the Bot",
              slug: "getting-started/running-the-bot",
            },
          ],
        },
      ],
    }),
  ],
});
