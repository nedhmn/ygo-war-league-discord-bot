# hat-format-discord-bot

## todos

### deck-submission-session

- [x] Limit `/submit_decks` cmd for team leaders and admins
- [x] Get current season and week from `LeagueSetting` and use for `LeagueDeck` entry
- [x] Validation if submitter has a team role
- [x] Use that team role for `LeagueDeck` entry
- [x] Use the current season, week, and team_role_id to notify the submitter of a resubmission
  - [x] Adjust the `load_league_decks_to_db` function to upsert instead of insert records
- [ ] Render deck preview on deck confirmation step via PIL and ydk file

### decks-cog

- [ ] Finish `/submit_decks` cmd
- [ ] Create `/set_week` cmd for admins to change the current_week in `LeagueSetting`
- [ ] Create `/set_season` cmd for admins to cahnge the current_season in `LeagueSetting`
- [ ] Create `/get_team_decks` cmd for admin to get all decks for a team
  - [ ] With the parameters of season, week, and team_name
  - [ ] Autocomplete for parameters
  - [ ] Output should have submitter, player, and deck preview details
