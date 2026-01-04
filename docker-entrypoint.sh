#!/bin/bash
set -e

# Get UID and GID from environment or use defaults
USER_ID=${USER_ID:-1000}
GROUP_ID=${GROUP_ID:-1000}

# Create group if it doesn't exist
if ! getent group ${GROUP_ID} > /dev/null 2>&1; then
    groupadd -g ${GROUP_ID} builder 2>/dev/null || true
fi

# Create user if it doesn't exist
if ! getent passwd ${USER_ID} > /dev/null 2>&1; then
    useradd -u ${USER_ID} -g ${GROUP_ID} -m builder 2>/dev/null || true
fi

# Execute command as the builder user
exec gosu ${USER_ID}:${GROUP_ID} "$@"

