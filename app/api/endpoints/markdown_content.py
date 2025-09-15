from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import os
import glob
from pathlib import Path

router = APIRouter(tags=["markdown-content"])

# Base path for markdown files
MARKDOWN_BASE_PATH = Path("data/MARKDOWN_FILES")

def read_markdown_file(file_path: Path) -> Dict[str, Any]:
    """Read a markdown file and return its content with metadata"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        return {
            "filename": file_path.name,
            "title": file_path.stem,
            "content": content,
            "file_size": len(content),
            "file_path": str(file_path.relative_to(MARKDOWN_BASE_PATH))
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file {file_path}: {str(e)}")

def get_category_files(category: str) -> List[Dict[str, Any]]:
    """Get all markdown files in a specific category"""
    category_path = MARKDOWN_BASE_PATH / category

    if not category_path.exists():
        raise HTTPException(status_code=404, detail=f"Category '{category}' not found")

    markdown_files = []
    for file_path in category_path.glob("*.md"):
        markdown_files.append(read_markdown_file(file_path))

    return markdown_files

@router.get("/markdown/categories")
async def get_available_categories():
    """Get list of all available markdown categories"""
    try:
        categories = []
        if MARKDOWN_BASE_PATH.exists():
            for item in MARKDOWN_BASE_PATH.iterdir():
                if item.is_dir():
                    # Count files in category
                    file_count = len(list(item.glob("*.md")))
                    categories.append({
                        "name": item.name,
                        "slug": item.name.lower().replace(" ", "-"),
                        "file_count": file_count
                    })

        return {
            "categories": categories,
            "total_categories": len(categories)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching categories: {str(e)}")

@router.get("/markdown/beneficial-insects")
async def get_beneficial_insects_content():
    """Get all markdown files from Beneficial Insects category"""
    try:
        return {
            "category": "Beneficial Insects",
            "files": get_category_files("Beneficial Insects")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/markdown/companion-planting")
async def get_companion_planting_content():
    """Get all markdown files from Companion Planting category"""
    try:
        return {
            "category": "Companion Planting",
            "files": get_category_files("Companion Planting")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/markdown/composting")
async def get_composting_content():
    """Get all markdown files from Composting category"""
    try:
        return {
            "category": "Composting",
            "files": get_category_files("Composting")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/markdown/craft")
async def get_craft_content():
    """Get all markdown files from Craft category"""
    try:
        return {
            "category": "Craft",
            "files": get_category_files("Craft")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/markdown/fertiliser-soil")
async def get_fertiliser_soil_content():
    """Get all markdown files from Fertiliser Soil category"""
    try:
        return {
            "category": "Fertiliser Soil",
            "files": get_category_files("Fertiliser Soil")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/markdown/flowers")
async def get_flowers_content():
    """Get all markdown files from flowers category"""
    try:
        return {
            "category": "flowers",
            "files": get_category_files("flowers")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/markdown/grow-guide")
async def get_grow_guide_content():
    """Get all markdown files from grow_guide category"""
    try:
        return {
            "category": "grow_guide",
            "files": get_category_files("grow_guide")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/markdown/herbs")
async def get_herbs_content():
    """Get all markdown files from herbs category"""
    try:
        return {
            "category": "herbs",
            "files": get_category_files("herbs")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/markdown/informational")
async def get_informational_content():
    """Get all markdown files from informational category"""
    try:
        return {
            "category": "informational",
            "files": get_category_files("informational")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/markdown/pests-diseases")
async def get_pests_diseases_content():
    """Get all markdown files from pests-diseases category"""
    try:
        return {
            "category": "pests-diseases",
            "files": get_category_files("pests-diseases")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/markdown/category/{category_name}")
async def get_category_content(category_name: str):
    """Get all markdown files from a specific category (dynamic endpoint)"""
    try:
        # Convert slug back to directory name if needed
        category_map = {
            "beneficial-insects": "Beneficial Insects",
            "companion-planting": "Companion Planting",
            "composting": "Composting",
            "craft": "Craft",
            "fertiliser-soil": "Fertiliser Soil",
            "flowers": "flowers",
            "grow-guide": "grow_guide",
            "herbs": "herbs",
            "informational": "informational",
            "pests-diseases": "pests-diseases"
        }

        actual_category = category_map.get(category_name, category_name)

        return {
            "category": actual_category,
            "files": get_category_files(actual_category)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/markdown/file/{category_name}/{filename}")
async def get_specific_file(category_name: str, filename: str):
    """Get a specific markdown file from a category"""
    try:
        # Convert slug back to directory name if needed
        category_map = {
            "beneficial-insects": "Beneficial Insects",
            "companion-planting": "Companion Planting",
            "composting": "Composting",
            "craft": "Craft",
            "fertiliser-soil": "Fertiliser Soil",
            "flowers": "flowers",
            "grow-guide": "grow_guide",
            "herbs": "herbs",
            "informational": "informational",
            "pests-diseases": "pests-diseases"
        }

        actual_category = category_map.get(category_name, category_name)
        category_path = MARKDOWN_BASE_PATH / actual_category

        if not category_path.exists():
            raise HTTPException(status_code=404, detail=f"Category '{actual_category}' not found")

        # Look for the file (with or without .md extension)
        if not filename.endswith('.md'):
            filename += '.md'

        file_path = category_path / filename

        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"File '{filename}' not found in category '{actual_category}'")

        return {
            "category": actual_category,
            "file": read_markdown_file(file_path)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))