import os

# Bot token @Botfather
BOT_TOKEN = os.environ.get("BOT_TOKEN", "7978077458:AAGlcsLBqSo9eDkrQ9rYLgyWBC0a3Rqqfxc")

# Your API ID from my.telegram.org
API_ID = int(os.environ.get("API_ID", "22581733"))

# Your API Hash from my.telegram.org
API_HASH = os.environ.get("API_HASH", "1db7bdcf908100cc641c6a5276765c3d")

# Your Owner / Admin Id For Broadcast 
ADMINS = int(os.environ.get("ADMINS", "6530997270"))

# Your Mongodb Database Url
# Warning - Give Db uri in deploy server environment variable, don't give in repo.
DB_URI = os.environ.get("DB_URI", "") # Warning - Give Db uri in deploy server environment variable, don't give in repo.
DB_NAME = os.environ.get("DB_NAME", "")

# If You Want Error Message In Your Personal Message Then Turn It True Else If You Don't Want Then Flase
ERROR_MESSAGE = bool(os.environ.get('ERROR_MESSAGE', True))
