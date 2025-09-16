#!/bin/bash

# Script to upload only specific missing plant images
# Faster option if you only want to upload known missing items

echo "=========================================="
echo "UPLOADING SPECIFIC MISSING IMAGES"
echo "=========================================="

LOCAL_BASE="/Users/kevin/Downloads/plant_images"
GCS_BASE="gs://plantopia-images-1757656642/plant_images"

# List of specific missing folders (based on our check)
MISSING_FOLDERS=(
    "flower_plant_images/Ageratum- Ball Blue_Ageratum houstonianum"
    "flower_plant_images/Ageratum- Ball White_Ageratum houstonianum"
)

echo ""
echo "Found ${#MISSING_FOLDERS[@]} missing folders to upload"
echo ""

# Upload each missing folder
for folder in "${MISSING_FOLDERS[@]}"; do
    echo "📤 Uploading: $folder"

    if [ -d "$LOCAL_BASE/$folder" ]; then
        gsutil -m cp -r "$LOCAL_BASE/$folder" "$GCS_BASE/${folder%/*}/"

        if [ $? -eq 0 ]; then
            echo "   ✅ Successfully uploaded"
        else
            echo "   ❌ Upload failed"
        fi
    else
        echo "   ⚠️  Local folder not found: $LOCAL_BASE/$folder"
    fi
    echo ""
done

echo "=========================================="
echo "UPLOAD COMPLETE!"
echo "=========================================="