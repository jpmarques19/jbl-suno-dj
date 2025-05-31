#!/bin/bash
# Automated Suno Music Generator using curl
# This script generates music, waits for completion, and downloads the result

set -e  # Exit on any error

# Configuration
API_KEY="4e2feeb494648a5f5845dd5b65558544"
BASE_URL="https://apibox.erweima.ai"
DOWNLOAD_DIR="./downloads"
MAX_WAIT_TIME=300  # 5 minutes
CHECK_INTERVAL=15  # 15 seconds

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Create download directory
mkdir -p "$DOWNLOAD_DIR"

# Function to generate music
generate_music() {
    local prompt="$1"
    local model="${2:-V3_5}"
    
    log_info "Generating music with prompt: '$prompt'"
    log_info "Using model: $model (cheaper option)"
    
    local response=$(curl -s -X POST "$BASE_URL/api/v1/generate" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $API_KEY" \
        -d "{
            \"prompt\": \"$prompt\",
            \"customMode\": false,
            \"instrumental\": false,
            \"model\": \"$model\",
            \"callBackUrl\": \"https://httpbin.org/post\"
        }" \
        --max-time 30)
    
    if [ $? -ne 0 ]; then
        log_error "Failed to make API request"
        return 1
    fi
    
    echo "$response"
}

# Function to check status
check_status() {
    local task_id="$1"
    
    log_info "Checking status for task: $task_id"
    
    local response=$(curl -s -X GET "$BASE_URL/api/v1/generate/record-info?taskId=$task_id" \
        -H "Authorization: Bearer $API_KEY" \
        --max-time 30)
    
    if [ $? -ne 0 ]; then
        log_error "Failed to check status"
        return 1
    fi
    
    echo "$response"
}

# Function to extract JSON value
extract_json_value() {
    local json="$1"
    local key="$2"
    
    # Simple JSON parsing using grep and sed
    echo "$json" | grep -o "\"$key\":[^,}]*" | sed "s/\"$key\"://g" | sed 's/[",]//g' | xargs
}

# Function to download audio file
download_audio() {
    local audio_url="$1"
    local filename="$2"
    
    log_info "Downloading: $filename"
    
    local filepath="$DOWNLOAD_DIR/$filename"
    
    curl -s -L "$audio_url" -o "$filepath" --max-time 60
    
    if [ $? -eq 0 ] && [ -f "$filepath" ]; then
        local file_size=$(stat -c%s "$filepath" 2>/dev/null || stat -f%z "$filepath" 2>/dev/null || echo "unknown")
        log_success "Downloaded: $filepath ($file_size bytes)"
        echo "$filepath"
    else
        log_error "Download failed"
        return 1
    fi
}

# Function to play audio
play_audio() {
    local filepath="$1"
    
    log_info "Attempting to play: $(basename "$filepath")"
    
    # Try different audio players
    local players=("mpv" "vlc" "mplayer" "ffplay" "paplay" "aplay" "open" "xdg-open")
    
    for player in "${players[@]}"; do
        if command -v "$player" >/dev/null 2>&1; then
            log_success "Playing with $player"
            if [ "$player" = "open" ] || [ "$player" = "xdg-open" ]; then
                "$player" "$filepath" >/dev/null 2>&1 &
            else
                "$player" "$filepath" >/dev/null 2>&1 &
            fi
            return 0
        fi
    done
    
    log_warning "No audio player found"
    log_info "Install mpv, vlc, or another audio player to hear the music"
    log_info "File saved at: $filepath"
    return 1
}

# Main workflow
main() {
    echo "🎵 Automated Suno Music Generator"
    echo "=================================="
    
    # Get prompt from user or use default
    local prompt="$1"
    if [ -z "$prompt" ]; then
        echo -n "Enter your music prompt (or press Enter for 'upbeat song'): "
        read -r prompt
        if [ -z "$prompt" ]; then
            prompt="upbeat song"
        fi
    fi
    
    log_info "Using prompt: '$prompt'"
    
    # Step 1: Generate music
    log_info "Step 1: Generating music..."
    local gen_response=$(generate_music "$prompt")
    
    if [ -z "$gen_response" ]; then
        log_error "No response from generation API"
        exit 1
    fi
    
    echo "📄 Generation response: $gen_response"
    
    # Extract task ID
    local task_id=$(extract_json_value "$gen_response" "taskId")
    
    if [ -z "$task_id" ]; then
        log_error "No task ID in response"
        echo "Response: $gen_response"
        exit 1
    fi
    
    log_success "Generation started! Task ID: $task_id"
    
    # Step 2: Wait for completion
    log_info "Step 2: Waiting for completion (max ${MAX_WAIT_TIME}s)..."
    
    local start_time=$(date +%s)
    local audio_url=""
    local title=""
    
    while [ $(($(date +%s) - start_time)) -lt $MAX_WAIT_TIME ]; do
        local elapsed=$(($(date +%s) - start_time))
        log_info "Status check at ${elapsed}s..."
        
        local status_response=$(check_status "$task_id")
        
        if [ -n "$status_response" ]; then
            echo "📄 Status response: $status_response"
            
            # Check if we have audio_url in the response
            audio_url=$(echo "$status_response" | grep -o '"audio_url":"[^"]*"' | sed 's/"audio_url":"//g' | sed 's/"//g' | head -1)
            
            if [ -n "$audio_url" ] && [ "$audio_url" != "null" ]; then
                log_success "Audio ready!"
                title=$(echo "$status_response" | grep -o '"title":"[^"]*"' | sed 's/"title":"//g' | sed 's/"//g' | head -1)
                break
            fi
        fi
        
        if [ $((elapsed + CHECK_INTERVAL)) -lt $MAX_WAIT_TIME ]; then
            log_info "Still generating... waiting ${CHECK_INTERVAL}s"
            sleep $CHECK_INTERVAL
        else
            break
        fi
    done
    
    # Step 3: Download and play
    if [ -n "$audio_url" ] && [ "$audio_url" != "null" ]; then
        log_info "Step 3: Downloading and playing..."
        
        # Generate filename
        local safe_title=$(echo "$title" | sed 's/[^a-zA-Z0-9 _-]//g' | sed 's/ /_/g')
        if [ -z "$safe_title" ]; then
            safe_title="generated_music"
        fi
        local filename="${safe_title}_${task_id:0:8}.mp3"
        
        # Download the file
        local filepath=$(download_audio "$audio_url" "$filename")
        
        if [ -n "$filepath" ]; then
            # Try to play the file
            play_audio "$filepath"
            
            log_success "Workflow completed successfully!"
            log_info "File saved at: $filepath"
            return 0
        else
            log_error "Download failed"
            return 1
        fi
    else
        log_warning "Audio not ready after ${MAX_WAIT_TIME}s"
        log_info "Task ID: $task_id"
        log_info "You can check the status later or visit the dashboard"
        return 1
    fi
}

# Run main function with all arguments
main "$@"
