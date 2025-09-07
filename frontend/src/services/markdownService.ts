import { marked } from 'marked'

// Configure marked options for security and styling
marked.setOptions({
  breaks: true,
  gfm: true,
})

/**
 * Safely render markdown text to HTML
 * @param markdown - The markdown text to render
 * @returns Safe HTML string
 */
export function renderMarkdown(markdown: string | undefined): string {
  if (!markdown) {
    return 'No description available.'
  }

  try {
    // Parse and render markdown to HTML
    const html = marked.parse(markdown) as string
    return html
  } catch (error) {
    console.warn('Failed to parse markdown:', error)
    // Fallback to plain text if parsing fails
    return markdown
  }
}

/**
 * Render markdown inline (without wrapping in block elements)
 * Useful for shorter descriptions that should not be wrapped in paragraphs
 * @param markdown - The markdown text to render
 * @returns Safe HTML string without block elements
 */
export function renderMarkdownInline(markdown: string | undefined): string {
  if (!markdown) {
    return 'No description available.'
  }

  try {
    // Use parseInline for inline rendering
    const html = marked.parseInline(markdown) as string
    return html
  } catch (error) {
    console.warn('Failed to parse inline markdown:', error)
    return markdown
  }
}

/**
 * Strip markdown formatting and return plain text
 * Useful for places where we need clean text without any HTML
 * @param markdown - The markdown text to clean
 * @returns Plain text without markdown formatting
 */
export function stripMarkdown(markdown: string | undefined): string {
  if (!markdown) {
    return ''
  }

  try {
    // Parse markdown and then strip HTML tags
    const html = marked.parse(markdown) as string
    // Simple HTML tag removal (for basic cases)
    return html.replace(/<[^>]*>/g, '').trim()
  } catch (error) {
    console.warn('Failed to strip markdown:', error)
    return markdown
  }
}

export default {
  renderMarkdown,
  renderMarkdownInline,
  stripMarkdown
}
