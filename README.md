# hat-format-discord-bot

## Requirements

### 1. Download Docker

[Docker Desktop](https://www.docker.com/products/docker-desktop/) for Windows/MacOS or [Docker Engine](https://docs.docker.com/engine/install/ubuntu/) for Linux

## Installation

### 1. Clone the respository

```
git clone https://github.com/hmnned/hat-format-discord-bot
```

### 2. Create .env file

Use `.env.example` as a template for your `.env` file

```
cp .env.example .env
```

Edit the `.env` file to fill out these variables:

```
ENVIORNMENT=production
BOT_TOKEN=<YOUR DISCORD BOT TOKEN>
DATABASE_URL=sqlite+aiosqlite:///data/database.db

CARD_IMAGE_BASE_URL=<YOUR CARD IMAGE BASE URL>
CARD_IMAGE_FORMAT=<YOUR CARD IMAGE FORMAT, OR FILE TYPE>

ADMIN_ROLES=<LIST OF COMMA SEPARATED ADMIN ROLE IDS>
ALLOWED_ROLES=<LIST OF COMMA SEPARATED TEAM CAPTAIN ROLE IDS>
TEAM_ROLES=<LIST OF COMMA SEPARATED TEAMS ROLE IDS>
```

### 3. Run the docker compose file

Make sure you're in the project's directory

```
cd hat-format-discord-bot
```

Build the docker image

```
sudo docker compose build
```

To run the docker container

```
sudo docker compose up -d
```

Boom! The bot should be running now.

## Update The Bot

Make sure you're in the project's directory and shut down the outdated bot.

```
sudo docker stop hat-format-discord-bot-bot-1
```

Pull the latest changes from this repo

```
git pull
```

Rebuild the docker image

```
sudo docker compose build --no-cache
```

Rerun the docker container

```
sudo docker compose up -d
```

## Access Data

Once the bot is running and taking submissions, it'll generate data that you can access.

### 1. Database

The deck submissions are in a sqlite3 database located in `data/database.db` after you run the bot for the first time.

### 2. Submitted deck images

The bot stores composed deck images locally in lieu of a cloud solution. They are located in `data/decks/` as webp files.

## Useful Commands

To view built docker containers and their size

```
sudo docker ps -a
```

To delete all containers, images, and clear cache (reset docker)

```
sudo docker system prune -a
```
