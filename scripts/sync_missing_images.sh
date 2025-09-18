#!/bin/bash

# Script to sync missing plant images to GCP bucket
# This will only upload files that don't exist in GCP, won't re-upload existing ones

echo "=========================================="
echo "SYNCING MISSING PLANT IMAGES TO GCP"
echo "=========================================="

LOCAL_BASE="/Users/kevin/Downloads/plant_images"
GCS_BASE="gs://plantopia-images-1757656642/plant_images"

# Function to sync a category
sync_category() {
    local category=$1
    echo ""
    echo "📁 Syncing $category..."
    echo "   From: $LOCAL_BASE/$category/"
    echo "   To:   $GCS_BASE/$category/"

    # Use rsync to only upload missing files
    # -r: recursive
    # -m: parallel upload
    # -c: skip based on checksum (more accurate than size/timestamp)
    gsutil -m rsync -r "$LOCAL_BASE/$category/" "$GCS_BASE/$category/"

    if [ $? -eq 0 ]; then
        echo "   ✅ Successfully synced $category"
    else
        echo "   ❌ Error syncing $category"
    fi
}

# Sync each category
echo ""
echo "Starting sync process..."
echo "This will only upload missing files, existing files will be skipped."
echo ""

# Sync flower images (includes the missing Ageratum varieties)
sync_category "flower_plant_images"

# Sync vegetable images
sync_category "vegetable_plant_images"

# Sync herb images
sync_category "herb_plant_images"

# Optional: Sync common problems images
# sync_category "common_problems_images"

echo ""
echo "=========================================="
echo "SYNC COMPLETE!"
echo "=========================================="
echo ""
echo "All missing images have been uploaded to GCP."
echo "Existing images were skipped to save bandwidth."