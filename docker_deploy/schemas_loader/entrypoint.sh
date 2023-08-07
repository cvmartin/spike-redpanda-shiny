#!/bin/bash

# Define variables for the schema file and the target URL
SCHEMA_FILE="etc/schemas_loader/schemas/purchase-value.avsc"
TARGET_URL="http://redpanda-1:8081/subjects/purchase-value/versions"

# Use 'jq' to read the schema file and format it as JSON
SCHEMA_JSON=$(jq -Rs '{schema: .}' < "$SCHEMA_FILE")

# Use 'curl' to POST the data to the target URL
curl -X POST \
    -H "Content-Type: application/vnd.schemaregistry.v1+json" \
    --data "$SCHEMA_JSON" \
    "$TARGET_URL"
