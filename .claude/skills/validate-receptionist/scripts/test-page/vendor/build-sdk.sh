#!/usr/bin/env bash
# Rebuild vendor/retell-sdk.mjs: Retell's browser SDK with its dependencies in one ESM file.
# Usage: vendor/build-sdk.sh [sdk-version]   (default 3.0.3; pin a version at least 2 weeks old)
set -euo pipefail
ver="${1:-3.0.3}"
out="$(cd "$(dirname "$0")" && pwd)/retell-sdk.mjs"
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
cd "$tmp"
npm init -y >/dev/null
npm install --silent "retell-client-js-sdk@$ver" esbuild@0.24.2
echo 'export { RetellClient } from "retell-client-js-sdk";' > entry.mjs
npx esbuild entry.mjs --bundle --format=esm --minify --target=es2020 --outfile="$out"
echo "built $out (retell-client-js-sdk@$ver)"
