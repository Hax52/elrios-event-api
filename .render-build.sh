#!/usr/bin/env bash

echo "▶ Installing Python dependencies..."
pip install -r requirements.txt || exit 1

echo "▶ Installing Chromium via Playwright..."
playwright install chromium || exit 1

echo "✅ Build script finished."
