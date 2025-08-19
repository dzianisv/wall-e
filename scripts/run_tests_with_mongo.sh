#!/usr/bin/env bash
set -euo pipefail

if ! command -v mongod >/dev/null 2>&1; then
  echo "mongod not installed" >&2
  exit 1
fi

DBPATH=$(mktemp -d)
PORT=27017
mongod --dbpath "$DBPATH" --bind_ip 127.0.0.1 --port $PORT --quiet &
MONGOD_PID=$!

cleanup() {
  kill $MONGOD_PID 2>/dev/null || true
  wait $MONGOD_PID 2>/dev/null || true
  rm -rf "$DBPATH"
}
trap cleanup EXIT

# wait for mongod to be ready
for i in {1..30}; do
  if python - <<'PY'
import pymongo, sys
try:
    pymongo.MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=100).admin.command('ping')
    sys.exit(0)
except Exception:
    sys.exit(1)
PY
  then
    break
  else
    sleep 0.1
  fi
done

pytest "$@"
