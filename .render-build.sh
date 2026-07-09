#!/usr/bin/env bash

echo "▶ Installing Python dependencies..."
pip install -r requirements.txt || exit 1

echo "▶ Clearing Playwright cache (optional safe cleanup)..."
rm -rf /opt/render/.cache/ms-playwright

echo "▶ Installing Chromium via Playwright..."
playwright install chromium || exit 1

playwright install || exit 1

echo "✅ Build script finished."
