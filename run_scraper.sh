# Bash

# If the command doesn't match with the requirement
if [ $# -lt 1 ]; then
    echo "Usage: $0 <phrase> [proxy_url]"
    exit 1
fi

PHRASE=$1
PROXY_URL=$2

if [ -z "$PROXY_URL" ]; then
    python src/scraper.py "$PHRASE"
else
    python src/scraper.py "$PHRASE" "$PROXY_URL"
fi
