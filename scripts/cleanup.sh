#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="$REPO_ROOT/docker-compose.yml"

if ! command -v docker >/dev/null 2>&1; then
  echo "docker is not installed or not on PATH"
  exit 1
fi

if [ ! -f "$COMPOSE_FILE" ]; then
  echo "docker-compose.yml not found at $COMPOSE_FILE"
  exit 1
fi

read -r -p "This will stop the stack, remove containers, volumes and local images created by docker-compose. Continue? [y/N] " confirm
confirm=${confirm,,} # tolower
if [[ "$confirm" != "y" && "$confirm" != "yes" ]]; then
  echo "Aborting cleanup. No changes made."
  exit 0
fi

echo "Stopping and removing docker-compose stack..."
docker-compose -f "$COMPOSE_FILE" down --remove-orphans --volumes --rmi local

echo "Optional: prune unused objects (networks, dangling images)."
read -r -p "Run 'docker system prune -f'? [y/N] " prune_confirm
prune_confirm=${prune_confirm,,}
if [[ "$prune_confirm" == "y" || "$prune_confirm" == "yes" ]]; then
  docker system prune -f
fi

echo "Cleanup complete."
