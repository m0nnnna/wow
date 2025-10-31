#!/bin/bash

# Quick script to restart only the ac-worldserver container + announcement with 15-min delay
# Explicitly sets working directory to /opt/azerothcore-wotlk
# Requires: socat installed (apk add socat)

set -e

REPO_ROOT="/opt/azerothcore-wotlk"
LOG_FILE="/var/log/azerothcore-restart.log"
SEND_ANNOUNCE_MSG="announce Server restart in 15 minutes"  # Customize message here
ANNOUNCE_WAIT=900  # 15 minutes in seconds (15 * 60)

# Change to repo root
cd "$REPO_ROOT" || { echo "ERROR: Cannot cd to $REPO_ROOT"; exit 1; }

# Function to log and echo messages
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Check if socat is available
if ! command -v socat >/dev/null 2>&1; then
    log "ERROR: socat not installed. Run: apk add socat"
    exit 1
fi

log "Scheduling ac-worldserver restart in $REPO_ROOT (15-min delay after announcement)..."

# Check if container is running
if ! docker compose ps | grep -q ac-worldserver; then
    log "ERROR: ac-worldserver container not running. Start it first."
    exit 1
fi

# Send announcement if container is running
log "=== Sending in-game announcement ==="
RESPONSE=$(echo -e "$SEND_ANNOUNCE_MSG\n" | socat - EXEC:'docker attach ac-worldserver',pty,stderr 2>&1) || {
    log "WARNING: Announcement failed. Output: $RESPONSE"
}
log "Announcement response: $RESPONSE"

log "Announcement sent. Waiting $ANNOUNCE_WAIT seconds (15 minutes) before restart..."
sleep "$ANNOUNCE_WAIT"

# Restart the specific service after delay
log "=== Restarting ac-worldserver after delay ==="
docker container restart ac-worldserver

log "✓ ac-worldserver restarted successfully. Check 'docker compose logs ac-worldserver' for issues."
