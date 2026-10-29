#!/usr/bin/env bash
# ==============================================================================
# Google Cloud Vertex AI Reasoning Engine / Agent Engine Deployment Script
# ==============================================================================
# Usage:
#   ./scripts/deploy_to_cloud.sh <AGENT_FOLDER>
# Example:
#   ./scripts/deploy_to_cloud.sh 08_agent_engine_deployment
# ==============================================================================
set -e

AGENT_PATH="${1:-08_agent_engine_deployment}"

echo "=============================================================================="
echo " Deploying Agent to Vertex AI Agent Engine"
echo " Target: $AGENT_PATH"
echo "=============================================================================="

# Check for gcloud
if ! command -v gcloud &> /dev/null; then
    echo "[ERROR] Google Cloud SDK (gcloud) is not installed."
    exit 1
fi

# Load environment variables
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

echo "[INFO] Project:  ${GOOGLE_CLOUD_PROJECT:-Not Set}"
echo "[INFO] Location: ${GOOGLE_CLOUD_LOCATION:-us-central1}"
echo ""

# Deploy via ADK CLI
python -m google.adk.cli deploy "$AGENT_PATH" "$@"

