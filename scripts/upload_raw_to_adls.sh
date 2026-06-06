#!/bin/bash

set -e

RESOURCE_GROUP="rg-tokyo2021-olympics-dataengwaigi"
STORAGE_ACCOUNT="sttokyo2021waigi"
CONTAINER_NAME="raw"
LOCAL_DATA_DIR="data/raw"
DESTINATION_PATH="tokyo-2021"

echo "Uploading Tokyo 2021 Olympics raw CSV files to ADLS Gen2..."

az storage blob upload-batch \
  --account-name "$STORAGE_ACCOUNT" \
  --destination "$CONTAINER_NAME/$DESTINATION_PATH" \
  --source "$LOCAL_DATA_DIR" \
  --auth-mode login \
  --overwrite

echo "Upload complete."

echo "Listing uploaded files..."
az storage blob list \
  --account-name "$STORAGE_ACCOUNT" \
  --container-name "$CONTAINER_NAME" \
  --prefix "$DESTINATION_PATH" \
  --auth-mode login \
  --output table
