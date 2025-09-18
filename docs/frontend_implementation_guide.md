# Frontend Implementation Guide - Markdown Content API

This guide provides comprehensive documentation for integrating the new Markdown Content API endpoints into the frontend application.

## Overview

The Markdown Content API provides access to educational content organized into 10 categories with a total of 465+ markdown files covering various gardening topics.

## Base Configuration

**API Base URL:** `http://localhost:8000/api/v1` (adjust for production)
**Content Type:** `application/json`
**Authentication:** None required for these endpoints

## Available Categories

| Category | Endpoint Slug | File Count | Description |
|----------|---------------|------------|-------------|
| Beneficial Insects | `beneficial-insects` | 6 | Attracting helpful garden insects |
| Companion Planting | `companion-planting` | 4 | Plant pairing strategies |
| Composting | `composting` | 8 | Composting techniques and tips |
| Craft | `craft` | 8 | DIY garden projects and crafts |
| Fertiliser Soil | `fertiliser-soil` | 22 | Soil management and fertilization |
| Flowers | `flowers` | 36 | Flower growing guides |
| Grow Guide | `grow-guide` | 255 | Comprehensive growing instructions |
| Herbs | `herbs` | 12 | Herb cultivation guides |
| Informational | `informational` | 69 | General gardening information |
| Pests Diseases | `pests-diseases` | 45 | Pest and disease management |

## API Endpoints

### 1. Get All Categories

**Endpoint:** `GET /markdown/categories`

**Description:** Retrieve list of all available content categories

**Response:**
```json
{
  "categories": [
    {
      "name": "Beneficial Insects",
      "slug": "beneficial-insects",
      "file_count": 6
    },
    {
      "name": "Companion Planting",
      "slug": "companion-planting",
      "file_count": 4
    }
  ],
  "total_categories": 10
}
```

**Frontend Usage:**
```javascript
// Fetch all categories for navigation/menu
const fetchCategories = async () => {
  try {
    const response = await fetch('/api/v1/markdown/categories');
    const data = await response.json();
    return data.categories;
  } catch (error) {
    console.error('Error fetching categories:', error);
  }
};
```

### 2. Get Category Content (Specific Endpoints)

**Endpoints:**
- `GET /markdown/beneficial-insects`
- `GET /markdown/companion-planting`
- `GET /markdown/composting`
- `GET /markdown/craft`
- `GET /markdown/fertiliser-soil`
- `GET /markdown/flowers`
- `GET /markdown/grow-guide`
- `GET /markdown/herbs`
- `GET /markdown/informational`
- `GET /markdown/pests-diseases`

**Response Structure:**
```json
{
  "category": "Beneficial Insects",
  "files": [
    {
      "filename": "5 Ways to Attract Aphid-Loving Lacewings to Your Garden.md",
      "title": "5 Ways to Attract Aphid-Loving Lacewings to Your Garden",
      "content": "# 5 Ways to Attract Aphid‑Loving Lacewings to Your Garden\n\nIn the ongoing battle against aphids...",
      "file_size": 3857,
      "file_path": "Beneficial Insects/5 Ways to Attract Aphid-Loving Lacewings to Your Garden.md"
    }
  ]
}
```

**Frontend Usage:**
```javascript
// Fetch specific category content
const fetchBeneficialInsectsContent = async () => {
  try {
    const response = await fetch('/api/v1/markdown/beneficial-insects');
    const data = await response.json();
    return data.files;
  } catch (error) {
    console.error('Error fetching beneficial insects content:', error);
  }
};
```

### 3. Get Category Content (Dynamic Endpoint)

**Endpoint:** `GET /markdown/category/{category_name}`

**Parameters:**
- `category_name`: The category slug (e.g., `beneficial-insects`, `grow-guide`)

**Response:** Same structure as specific endpoints

**Frontend Usage:**
```javascript
// Generic function to fetch any category
const fetchCategoryContent = async (categorySlug) => {
  try {
    const response = await fetch(`/api/v1/markdown/category/${categorySlug}`);
    const data = await response.json();
    return data.files;
  } catch (error) {
    console.error(`Error fetching ${categorySlug} content:`, error);
  }
};

// Usage examples
const growGuideContent = await fetchCategoryContent('grow-guide');
const flowersContent = await fetchCategoryContent('flowers');
```

### 4. Get Specific File

**Endpoint:** `GET /markdown/file/{category_name}/{filename}`

**Parameters:**
- `category_name`: The category slug
- `filename`: The filename (with or without .md extension)

**Response:**
```json
{
  "category": "Beneficial Insects",
  "file": {
    "filename": "5 Ways to Attract Aphid-Loving Lacewings to Your Garden.md",
    "title": "5 Ways to Attract Aphid-Loving Lacewings to Your Garden",
    "content": "# 5 Ways to Attract Aphid‑Loving Lacewings to Your Garden\n\nIn the ongoing battle against aphids...",
    "file_size": 3857,
    "file_path": "Beneficial Insects/5 Ways to Attract Aphid-Loving Lacewings to Your Garden.md"
  }
}
```

**Frontend Usage:**
```javascript
// Fetch specific file
const fetchSpecificFile = async (categorySlug, filename) => {
  try {
    const response = await fetch(`/api/v1/markdown/file/${categorySlug}/${filename}`);
    const data = await response.json();
    return data.file;
  } catch (error) {
    console.error(`Error fetching file ${filename}:`, error);
  }
};

// Usage
const lacewingArticle = await fetchSpecificFile(
  'beneficial-insects',
  '5 Ways to Attract Aphid-Loving Lacewings to Your Garden'
);
```

## Frontend Implementation Examples

### React Component Example

```jsx
import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';

const MarkdownContentViewer = () => {
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [categoryContent, setCategoryContent] = useState([]);
  const [selectedArticle, setSelectedArticle] = useState(null);
  const [loading, setLoading] = useState(false);

  // Load categories on component mount
  useEffect(() => {
    const loadCategories = async () => {
      try {
        const response = await fetch('/api/v1/markdown/categories');
        const data = await response.json();
        setCategories(data.categories);
      } catch (error) {
        console.error('Error loading categories:', error);
      }
    };
    loadCategories();
  }, []);

  // Load category content when category is selected
  const handleCategorySelect = async (categorySlug) => {
    setLoading(true);
    try {
      const response = await fetch(`/api/v1/markdown/category/${categorySlug}`);
      const data = await response.json();
      setSelectedCategory(categorySlug);
      setCategoryContent(data.files);
      setSelectedArticle(null);
    } catch (error) {
      console.error('Error loading category content:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="markdown-content-viewer">
      {/* Category Navigation */}
      <div className="categories-nav">
        <h2>Content Categories</h2>
        {categories.map(category => (
          <button
            key={category.slug}
            onClick={() => handleCategorySelect(category.slug)}
            className={selectedCategory === category.slug ? 'active' : ''}
          >
            {category.name} ({category.file_count})
          </button>
        ))}
      </div>

      {/* Article List */}
      {selectedCategory && (
        <div className="articles-list">
          <h3>Articles in {selectedCategory}</h3>
          {loading ? (
            <p>Loading...</p>
          ) : (
            categoryContent.map((article, index) => (
              <div key={index} className="article-item">
                <button onClick={() => setSelectedArticle(article)}>
                  {article.title}
                </button>
                <small>({article.file_size} chars)</small>
              </div>
            ))
          )}
        </div>
      )}

      {/* Article Content */}
      {selectedArticle && (
        <div className="article-content">
          <h2>{selectedArticle.title}</h2>
          <ReactMarkdown>{selectedArticle.content}</ReactMarkdown>
        </div>
      )}
    </div>
  );
};

export default MarkdownContentViewer;
```

### Vue.js Implementation

```vue
<template>
  <div class="markdown-content">
    <!-- Category selector -->
    <select @change="loadCategory($event.target.value)">
      <option value="">Select a category</option>
      <option
        v-for="category in categories"
        :key="category.slug"
        :value="category.slug"
      >
        {{ category.name }} ({{ category.file_count }} articles)
      </option>
    </select>

    <!-- Articles grid -->
    <div v-if="articles.length" class="articles-grid">
      <div
        v-for="article in articles"
        :key="article.filename"
        class="article-card"
        @click="viewArticle(article)"
      >
        <h3>{{ article.title }}</h3>
        <p>{{ article.file_size }} characters</p>
      </div>
    </div>

    <!-- Article modal/viewer -->
    <div v-if="selectedArticle" class="article-modal">
      <button @click="selectedArticle = null">Close</button>
      <div v-html="renderMarkdown(selectedArticle.content)"></div>
    </div>
  </div>
</template>

<script>
import { marked } from 'marked';

export default {
  data() {
    return {
      categories: [],
      articles: [],
      selectedArticle: null
    };
  },
  async mounted() {
    await this.loadCategories();
  },
  methods: {
    async loadCategories() {
      try {
        const response = await fetch('/api/v1/markdown/categories');
        const data = await response.json();
        this.categories = data.categories;
      } catch (error) {
        console.error('Error loading categories:', error);
      }
    },
    async loadCategory(categorySlug) {
      if (!categorySlug) return;

      try {
        const response = await fetch(`/api/v1/markdown/category/${categorySlug}`);
        const data = await response.json();
        this.articles = data.files;
      } catch (error) {
        console.error('Error loading category:', error);
      }
    },
    viewArticle(article) {
      this.selectedArticle = article;
    },
    renderMarkdown(content) {
      return marked(content);
    }
  }
};
</script>
```

## Error Handling

### Common Error Responses

**404 - Category Not Found:**
```json
{
  "detail": "Category 'invalid-category' not found"
}
```

**404 - File Not Found:**
```json
{
  "detail": "File 'nonexistent.md' not found in category 'beneficial-insects'"
}
```

**500 - Server Error:**
```json
{
  "detail": "Error reading file: [error details]"
}
```

### Frontend Error Handling Example

```javascript
const fetchWithErrorHandling = async (url) => {
  try {
    const response = await fetch(url);

    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('Content not found');
      } else if (response.status >= 500) {
        throw new Error('Server error - please try again later');
      } else {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
    }

    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
};
```

## Performance Considerations

### Recommended Practices

1. **Lazy Loading**: Load category content only when selected
2. **Caching**: Cache frequently accessed content in localStorage
3. **Pagination**: For large categories (like grow-guide with 255 files), implement pagination
4. **Search**: Implement client-side search for better UX

### Caching Example

```javascript
class MarkdownContentService {
  constructor() {
    this.cache = new Map();
    this.cacheExpiry = 5 * 60 * 1000; // 5 minutes
  }

  async getCategoryContent(categorySlug) {
    const cacheKey = `category-${categorySlug}`;
    const cached = this.cache.get(cacheKey);

    if (cached && Date.now() - cached.timestamp < this.cacheExpiry) {
      return cached.data;
    }

    const response = await fetch(`/api/v1/markdown/category/${categorySlug}`);
    const data = await response.json();

    this.cache.set(cacheKey, {
      data,
      timestamp: Date.now()
    });

    return data;
  }
}
```

## Styling Recommendations

### CSS Classes for Markdown Content

```css
.markdown-content {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  line-height: 1.6;
  color: #333;
}

.markdown-content h1 {
  border-bottom: 2px solid #4CAF50;
  padding-bottom: 0.3em;
  color: #2E7D32;
}

.markdown-content h2 {
  color: #388E3C;
  margin-top: 2em;
}

.markdown-content code {
  background-color: #f5f5f5;
  padding: 2px 4px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
}

.markdown-content blockquote {
  border-left: 4px solid #4CAF50;
  padding-left: 1em;
  margin-left: 0;
  background-color: #f9f9f9;
}

.markdown-content ul {
  list-style-type: none;
  padding-left: 1.5em;
}

.markdown-content ul li:before {
  content: "🌱";
  margin-right: 0.5em;
}
```

## Testing the API

### Quick Test Commands

```bash
# Get all categories
curl http://localhost:8000/api/v1/markdown/categories

# Get beneficial insects content
curl http://localhost:8000/api/v1/markdown/beneficial-insects

# Get specific file
curl http://localhost:8000/api/v1/markdown/file/beneficial-insects/5%20Ways%20to%20Attract%20Aphid-Loving%20Lacewings%20to%20Your%20Garden

# Dynamic category endpoint
curl http://localhost:8000/api/v1/markdown/category/grow-guide
```

## Integration Checklist

- [ ] Set up markdown rendering library (marked.js, react-markdown, etc.)
- [ ] Implement category navigation component
- [ ] Create article list/grid component
- [ ] Build article viewer component
- [ ] Add error handling for API calls
- [ ] Implement loading states
- [ ] Add search functionality (client-side)
- [ ] Set up caching mechanism
- [ ] Style markdown content appropriately
- [ ] Test with different screen sizes
- [ ] Add accessibility features
- [ ] Test API endpoints

## Support

For questions about the API endpoints or backend implementation, contact the backend team. For frontend-specific questions, refer to your project's frontend documentation.

---

**Last Updated:** September 2024
**API Version:** v1
**Total Content Files:** 465+ across 10 categories