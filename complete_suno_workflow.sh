#!/bin/bash
# Complete automated Suno workflow: Generate → Wait → Download → Play

set -e

# Configuration
API_KEY="4e2feeb494648a5f5845dd5b65558544"
BASE_URL="https://apibox.erweima.ai"
DOWNLOAD_DIR="./downloads"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${BLUE}🎵 $1${NC}"; }
success() { echo -e "${GREEN}✅ $1${NC}"; }
warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }

# Create download directory
mkdir -p "$DOWNLOAD_DIR"

# Get prompt
PROMPT="$1"
if [ -z "$PROMPT" ]; then
    echo -n "Enter music prompt: "
    read -r PROMPT
fi

log "Generating music: '$PROMPT'"

# Step 1: Generate music
RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/generate" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $API_KEY" \
    -d "{
        \"prompt\": \"$PROMPT\",
        \"customMode\": false,
        \"instrumental\": false,
        \"model\": \"V3_5\",
        \"callBackUrl\": \"https://httpbin.org/post\"
    }")

TASK_ID=$(echo "$RESPONSE" | grep -o '"taskId":"[^"]*"' | sed 's/"taskId":"//g' | sed 's/"//g')

if [ -z "$TASK_ID" ]; then
    echo "❌ Failed to generate music"
    echo "Response: $RESPONSE"
    exit 1
fi

success "Generated! Task ID: $TASK_ID"

# Step 2: Wait for completion
log "Waiting for completion..."
for i in {1..20}; do
    sleep 15
    log "Status check #$i..."
    
    STATUS=$(curl -s "$BASE_URL/api/v1/generate/record-info?taskId=$TASK_ID" \
        -H "Authorization: Bearer $API_KEY")
    
    # Extract stream URLs
    STREAM_URL=$(echo "$STATUS" | grep -o '"streamAudioUrl":"[^"]*"' | head -1 | sed 's/"streamAudioUrl":"//g' | sed 's/"//g')
    TITLE=$(echo "$STATUS" | grep -o '"title":"[^"]*"' | head -1 | sed 's/"title":"//g' | sed 's/"//g')
    
    if [ -n "$STREAM_URL" ] && [ "$STREAM_URL" != "null" ]; then
        success "Music ready!"
        break
    fi
    
    if [ $i -eq 20 ]; then
        warning "Timeout reached"
        exit 1
    fi
done

# Step 3: Download
SAFE_TITLE=$(echo "$TITLE" | sed 's/[^a-zA-Z0-9 ]//g' | sed 's/ /_/g')
FILENAME="${SAFE_TITLE:-generated_music}.mp3"
FILEPATH="$DOWNLOAD_DIR/$FILENAME"

log "Downloading: $FILENAME"
curl -L "$STREAM_URL" -o "$FILEPATH" --max-time 60

if [ -f "$FILEPATH" ]; then
    FILE_SIZE=$(stat -c%s "$FILEPATH" 2>/dev/null || stat -f%z "$FILEPATH" 2>/dev/null)
    success "Downloaded: $FILEPATH ($FILE_SIZE bytes)"
    
    # Step 4: Play
    log "Playing music..."
    if command -v mpv >/dev/null; then
        mpv "$FILEPATH" --no-video --really-quiet &
        success "Playing with mpv"
    elif command -v vlc >/dev/null; then
        vlc "$FILEPATH" --intf dummy --play-and-exit &
        success "Playing with vlc"
    else
        warning "No audio player found"
        log "File saved at: $FILEPATH"
    fi
    
    success "Workflow completed!"
    log "Generated: '$TITLE'"
    log "File: $FILEPATH"
else
    echo "❌ Download failed"
    exit 1
fi
