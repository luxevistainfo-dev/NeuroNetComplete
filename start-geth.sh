#!/usr/bin/env bash
set -e

# Initialize nodes (once) and start via docker-compose
# Usage: chmod +x start-geth.sh && ./start-geth.sh

# Create folders and copy genesis
mkdir -p geth/node1 geth/node2 geth/node3
GENESIS=genesis.json

if [ ! -f "$GENESIS" ]; then
  echo "genesis.json not found in current directory"
  exit 1
fi

# Initialize nodes if not already initialized
for n in 1 2 3; do
  DATA_DIR="geth/node${n}"
  if [ ! -d "${DATA_DIR}/geth" ] || [ -z "$(ls -A ${DATA_DIR}/geth 2>/dev/null)" ]; then
    echo "Initializing node ${n}"
    docker run --rm -v "$(pwd)/${DATA_DIR}:/root/.ethereum" -v "$(pwd)/${GENESIS}:/genesis.json:ro" ethereum/client-go:stable init /genesis.json
  else
    echo "Node ${n} already initialized"
  fi
endone

# Start docker-compose (detached)
docker-compose -f docker-compose-geth.yml up -d

echo "Geth nodes started. Wait a few seconds, then fetch enode addresses with:"
echo "docker exec -it geth-node-1 geth attach http://127.0.0.1:8545 --exec admin.nodeInfo.enode"