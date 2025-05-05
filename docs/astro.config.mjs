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
      favicon: "/favicon.ico",
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
            { label: "Introduction", slug: "getting-started/introduction" },
            { label: "Installation", slug: "getting-started/installation" },
            { label: "Configuration", slug: "getting-started/configuration" },
            {
              label: "Running the Bot",
              slug: "getting-started/running-the-bot",
            },
          ],
        },
        {
          label: "Guides",
          items: [
            { label: "League Settings", slug: "guides/league-settings" },
            { label: "Submitting Decks", slug: "guides/submitting-decks" },
            {
              label: "Get Week Submissions",
              slug: "guides/get-week-submissions",
            },
            {
              label: "Access League Data",
              slug: "guides/access-league-data",
            },
          ],
        },
        {
          label: "Bot Commands",
          items: [
            { label: "set_season", slug: "bot-commands/set-season" },
            { label: "set_week", slug: "bot-commands/set-week" },
            {
              label: "enable_deck_submissions",
              slug: "bot-commands/enable-deck-submissions",
            },
            { label: "submit_decks", slug: "bot-commands/submit-decks" },
            {
              label: "get_team_submission",
              slug: "bot-commands/get-team-submission",
            },
            {
              label: "get_team_matchups",
              slug: "bot-commands/get-team-matchups",
            },
            {
              label: "get_current_week_status",
              slug: "bot-commands/get-current-week-status",
            },
            { label: "latency", slug: "bot-commands/latency" },
          ],
        },
      ],
    }),
  ],
});
