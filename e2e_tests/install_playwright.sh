#!/bin/bash
echo "Installing Playwright"
pip install playwright pytest-playwright pytest-html
playwright install
playwright install-deps
echo "Playwright install completed!"