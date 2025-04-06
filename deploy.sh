#!/bin/bash

# Exit on error
set -e

# Set variables
PROJECT_ID="229875499807"
SERVICE_NAME="pill-id-api"
REGION="us-central1"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

# Build and push the container image
echo "Building and pushing Docker image..."
gcloud builds submit --tag $IMAGE_NAME

# Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars="PROJECT_ID=$PROJECT_ID,REGION=$REGION,ENDPOINT_ID=3163467576437112832" \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300s

# Get the URL of the deployed service
URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.url)")
echo "Service deployed successfully to: $URL"