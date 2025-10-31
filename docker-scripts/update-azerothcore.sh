#!/bin/bash

# Combined AzerothCore update script: Core + Modules + Docker Build/Up + Announcement with 15-min delay
# Explicitly sets working directory to /opt/azerothcore-wotlk
# Handles git divergence with stash + rebase pull
# Restart delayed 15 min after announcement
# Backs up entire /opt/azerothcore-wotlk before Git changes

set -e  # Exit on error

REPO_ROOT="/opt/azerothcore-wotlk"
BACKUPS_DIR="/opt/backups"
LOG_FILE="/var/log/azerothcore-update.log"
SEND_ANNOUNCE_MSG="announce Server restart in 15 minutes"  # Customize message here
ANNOUNCE_WAIT=900  # 15 minutes in seconds (15 * 60)
FAILURE=false

# Change to repo root
cd "$REPO_ROOT" || { echo "ERROR: Cannot cd to $REPO_ROOT"; exit 1; }

# Function to log and echo messages
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

log "Starting AzerothCore update process in $REPO_ROOT..."

# Backup entire directory before any changes
log "=== Creating pre-update backup ==="
mkdir -p "$BACKUPS_DIR"
BACKUP_FILE="$BACKUPS_DIR/azerothcore-backup-$(date +%Y%m%d-%H%M%S).tar.gz"
tar -czf "$BACKUP_FILE" -C /opt azerothcore-wotlk --exclude=backups || { log "ERROR: Backup failed"; FAILURE=true; exit 1; }
log "✓ Backup created: $BACKUP_FILE"
log "Rollback tip: If needed, docker compose down; mv azerothcore-wotlk azerothcore-wotlk-old; tar -xzf $BACKUP_FILE -C /opt; docker compose up -d"

# Part 1: Update core repo (with divergence handling)
log "=== Updating core repo ==="
log "Stashing local changes (including untracked files)..."
git stash push --include-untracked || { log "WARNING: Stash failed (no changes? Continuing...)"; }

git fetch origin || { log "ERROR: git fetch failed"; FAILURE=true; }
git status

log "Pulling with rebase to handle divergence..."
git pull --rebase origin master || { log "ERROR: git pull --rebase failed (possible conflicts—check stash and resolve manually)"; FAILURE=true; }

log "Restoring stashed changes..."
git stash pop || { log "WARNING: Stash pop failed (conflicts? Review git status and resolve)"; }

if [ "$FAILURE" = true ]; then
    log "Core update failed. Use backup: $BACKUP_FILE for rollback."
    exit 1
fi
log "✓ Core repo updated successfully"

# Part 2: Update modules (integrated logic)
log "=== Updating modules ==="
MODULES_DIR="modules"
MODULES=(
    "add mod folder names here"
	"mod-sample"

)

cd "$MODULES_DIR" || { log "Error: $MODULES_DIR not found!"; FAILURE=true; exit 1; }

for mod in "${MODULES[@]}"; do
    if [ -d "$mod" ]; then
        log "Updating $mod..."
        cd "$mod"
        
        # Fetch latest changes
        git fetch origin || { log "ERROR: git fetch failed for $mod"; FAILURE=true; }
        
        # Pull latest (assumes 'master' branch; add stash/rebase if modules diverge often)
        git pull origin master || { log "ERROR: git pull failed for $mod"; FAILURE=true; }
        
        # Update submodules
        git submodule update --init --recursive || { log "WARNING: Submodule update failed for $mod (non-fatal)"; }
        
        cd ..  # Back to modules/
        log "✓ $mod updated successfully"
    else
        log "⚠ Directory $mod not found; skipping"
    fi
done

cd ..  # Back to root
if [ "$FAILURE" = true ]; then
    log "Module update failed. Use backup: $BACKUP_FILE for rollback."
    exit 1
fi
log "✓ All modules updated successfully"

# Part 3: Trigger Docker build (only if no failures)
if [ "$FAILURE" = false ]; then
    log "=== Triggering Docker build ==="
    docker compose build || { log "ERROR: Docker build failed"; FAILURE=true; }
    
    # Part 4: Announcement + 15-min Wait + Reload containers (only if build succeeded)
    if [ "$FAILURE" = false ]; then
        log "=== Sending in-game announcement ==="
        # Pipe command + newline to docker attach via socat PTY (handles TTY-enabled containers)
        RESPONSE=$(echo -e "$SEND_ANNOUNCE_MSG\n" | socat - EXEC:'docker attach ac-worldserver',pty,stderr 2>&1) || {
            log "WARNING: Announcement failed. Output: $RESPONSE"
        }
        log "Announcement response: $RESPONSE"
        
        log "Announcement sent. Waiting $ANNOUNCE_WAIT seconds (15 minutes) before restart..."
        sleep "$ANNOUNCE_WAIT"
        
        log "=== Reloading containers after delay ==="
        docker compose up -d || { log "ERROR: Docker up failed"; FAILURE=true; }
    fi
    
    if [ "$FAILURE" = true ]; then
        log "Docker process failed. Use backup: $BACKUP_FILE for rollback."
        exit 1
    fi
    log "✓ Docker build, announcement + delay, and container reload completed successfully"
else
    log "Skipping Docker due to prior failures."
fi

log "Update process completed. Check $LOG_FILE for full details."
