#!/bin/bash

PLIST_NAME="com.tamadajeyesh.finder.plist"
DEST_DIR="$HOME/Library/LaunchAgents"
DEST_PATH="$DEST_DIR/$PLIST_NAME"

echo "Installing Auto-Start for Finder..."

# Ensure directory exists
mkdir -p "$DEST_DIR"

# Copy the plist file
cp "$PLIST_NAME" "$DEST_PATH"

# Set correct permissions
chmod 644 "$DEST_PATH"

# Unload if already loaded (to refresh)
launchctl unload "$DEST_PATH" 2>/dev/null

# Load the agent
launchctl load "$DEST_PATH"

echo "Success! Finder will now start automatically when you log in."
echo "Logs can be found at /tmp/com.tamadajeyesh.finder.out"
