# hat-format-discord-bot

## Installation

### 1. Clone the respository

```
git clone https://github.com/hmnned/hat-format-discord-bot
```

### 2. Run the docker compose file

Make sure you're in the project's directory

```
cd hat-format-discord-bot
```

Build the docker image

```
sudo docker compose build
```

To run the docker container in local (testing) enviornment:

```
sudo docker compose up -d
```

To run the docker container in production enviornment:

```
sudo docker compose -f docker-compose.yml up -d
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

Rerun the docker container in production mode

```
sudo docker compose -f docker-compose.yml up -d
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
