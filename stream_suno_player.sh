#!/bin/bash
# Suno Stream Player - Generate music and stream directly with controls

set -e

# Configuration
API_KEY="4e2feeb494648a5f5845dd5b65558544"
BASE_URL="https://apibox.erweima.ai"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

log() { echo -e "${BLUE}🎵 $1${NC}"; }
success() { echo -e "${GREEN}✅ $1${NC}"; }
warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
error() { echo -e "${RED}❌ $1${NC}"; }
info() { echo -e "${CYAN}ℹ️  $1${NC}"; }

# Function to generate music
generate_music() {
    local prompt="$1"
    log "Generating music: '$prompt'"
    
    local response=$(curl -s -X POST "$BASE_URL/api/v1/generate" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $API_KEY" \
        -d "{
            \"prompt\": \"$prompt\",
            \"customMode\": false,
            \"instrumental\": false,
            \"model\": \"V3_5\",
            \"callBackUrl\": \"https://httpbin.org/post\"
        }")
    
    local task_id=$(echo "$response" | grep -o '"taskId":"[^"]*"' | sed 's/"taskId":"//g' | sed 's/"//g')
    
    if [ -n "$task_id" ]; then
        success "Generated! Task ID: $task_id"
        echo "$task_id"
    else
        error "Failed to generate music"
        echo "Response: $response"
        return 1
    fi
}

# Function to wait for music and get stream URLs
wait_for_music() {
    local task_id="$1"
    log "Waiting for music generation..."
    
    for i in {1..24}; do  # Wait up to 6 minutes (24 * 15s)
        sleep 15
        info "Status check #$i (${i}5s elapsed)..."
        
        local status=$(curl -s "$BASE_URL/api/v1/generate/record-info?taskId=$task_id" \
            -H "Authorization: Bearer $API_KEY")
        
        # Extract all stream URLs and titles
        local stream_urls=($(echo "$status" | grep -o '"streamAudioUrl":"[^"]*"' | sed 's/"streamAudioUrl":"//g' | sed 's/"//g'))
        local titles=($(echo "$status" | grep -o '"title":"[^"]*"' | sed 's/"title":"//g' | sed 's/"//g'))
        
        if [ ${#stream_urls[@]} -gt 0 ] && [ "${stream_urls[0]}" != "null" ] && [ -n "${stream_urls[0]}" ]; then
            success "Music ready! Found ${#stream_urls[@]} track(s)"
            
            # Return the data in a format we can parse
            for j in "${!stream_urls[@]}"; do
                echo "TRACK:${titles[$j]:-Track $((j+1))}:${stream_urls[$j]}"
            done
            return 0
        fi
        
        if [ $i -eq 24 ]; then
            warning "Timeout reached after 6 minutes"
            return 1
        fi
    done
}

# Function to play stream with controls
play_stream() {
    local title="$1"
    local stream_url="$2"
    
    success "Now playing: $title"
    info "Stream URL: ${stream_url:0:50}..."
    echo
    info "🎮 PLAYBACK CONTROLS:"
    info "  SPACE - Play/Pause"
    info "  ← → - Seek backward/forward"
    info "  ↑ ↓ - Volume up/down"
    info "  q - Quit"
    info "  m - Mute/Unmute"
    echo
    
    # Check available players and use the best one
    if command -v mpv >/dev/null; then
        success "Using mpv player"
        mpv "$stream_url" \
            --title="Suno: $title" \
            --no-video \
            --volume=70 \
            --osd-level=2 \
            --osd-duration=2000
    elif command -v vlc >/dev/null; then
        success "Using VLC player"
        vlc "$stream_url" \
            --intf ncurses \
            --no-video \
            --volume 70
    elif command -v mplayer >/dev/null; then
        success "Using mplayer"
        mplayer "$stream_url" \
            -volume 70 \
            -title "Suno: $title"
    elif command -v ffplay >/dev/null; then
        success "Using ffplay"
        ffplay "$stream_url" \
            -nodisp \
            -volume 70 \
            -window_title "Suno: $title"
    else
        error "No compatible audio player found!"
        info "Please install one of: mpv, vlc, mplayer, or ffplay"
        info "Stream URL: $stream_url"
        return 1
    fi
}

# Function to show track selection menu
select_track() {
    local tracks=("$@")
    
    if [ ${#tracks[@]} -eq 1 ]; then
        # Only one track, play it directly
        local track_info="${tracks[0]}"
        local title=$(echo "$track_info" | cut -d':' -f2)
        local url=$(echo "$track_info" | cut -d':' -f3-)
        play_stream "$title" "$url"
    else
        # Multiple tracks, show selection menu
        echo
        success "Multiple tracks available:"
        for i in "${!tracks[@]}"; do
            local track_info="${tracks[$i]}"
            local title=$(echo "$track_info" | cut -d':' -f2)
            echo "  $((i+1)). $title"
        done
        echo "  a. Play all tracks"
        echo
        
        while true; do
            echo -n "Select track to play (1-${#tracks[@]}, a for all): "
            read -r choice
            
            if [ "$choice" = "a" ] || [ "$choice" = "A" ]; then
                # Play all tracks sequentially
                for track_info in "${tracks[@]}"; do
                    local title=$(echo "$track_info" | cut -d':' -f2)
                    local url=$(echo "$track_info" | cut -d':' -f3-)
                    echo
                    play_stream "$title" "$url"
                done
                break
            elif [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le ${#tracks[@]} ]; then
                local track_info="${tracks[$((choice-1))]}"
                local title=$(echo "$track_info" | cut -d':' -f2)
                local url=$(echo "$track_info" | cut -d':' -f3-)
                echo
                play_stream "$title" "$url"
                break
            else
                warning "Invalid choice. Please enter 1-${#tracks[@]} or 'a'"
            fi
        done
    fi
}

# Main function
main() {
    echo "🎵 Suno Stream Player"
    echo "===================="
    echo
    
    # Get prompt
    local prompt="$1"
    if [ -z "$prompt" ]; then
        echo -n "Enter music prompt: "
        read -r prompt
    fi
    
    if [ -z "$prompt" ]; then
        error "No prompt provided"
        exit 1
    fi
    
    # Generate music
    local task_id=$(generate_music "$prompt")
    if [ -z "$task_id" ]; then
        exit 1
    fi
    
    # Wait for completion and get tracks
    local track_data=$(wait_for_music "$task_id")
    if [ $? -ne 0 ]; then
        error "Failed to get music tracks"
        exit 1
    fi
    
    # Parse track data into array
    local tracks=()
    while IFS= read -r line; do
        if [[ "$line" == TRACK:* ]]; then
            tracks+=("$line")
        fi
    done <<< "$track_data"
    
    if [ ${#tracks[@]} -eq 0 ]; then
        error "No tracks found"
        exit 1
    fi
    
    # Play tracks
    select_track "${tracks[@]}"
    
    success "Playback completed!"
}

# Handle Ctrl+C gracefully
trap 'echo; warning "Interrupted by user"; exit 0' INT

# Run main function
main "$@"
