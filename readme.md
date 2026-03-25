# First Start

## generate sll key and crt file
- chmod +x ssl/generate_ssl.sh && ssl/generate_ssl.sh

# Database init and migrations
- run `oxyde init` to create config file
- run `oxyde makemigrations`
- run `oxyde migrate`

# Implemented
- rate limiter with xginx and slowapi
- redis cache
- TODO from fastapi import BackgroundTasks
- TODO add async logs QueueHandler, RotatingFileHandler,