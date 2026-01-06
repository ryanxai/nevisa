#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix bidirectional text issues with parentheses containing English text.
When English text appears in parentheses after Farsi text, LaTeX bidi package
reverses the parentheses. This script wraps English text in parentheses
with \LR{} to force LTR direction.
"""

import re
import sys
from pathlib import Path


def contains_english(text):
    """Check if text contains English characters."""
    return bool(re.search(r'[A-Za-z]', text))


def contains_farsi(text):
    """Check if text contains Farsi/Persian characters."""
    # Farsi Unicode range: \u0600-\u06FF
    return bool(re.search(r'[\u0600-\u06FF]', text))


def fix_parentheses(text):
    """
    Fix parentheses containing English text that appears after Farsi text.
    
    Pattern: Farsi text followed by (English Text)
    Solution: Wrap with \LR{(English Text)} to force LTR direction
    """
    # First, protect markdown syntax and already-wrapped text
    protected_placeholders = {}
    placeholder_counter = 0
    
    # Protect markdown links: [text](url) or [text](url "title")
    markdown_link_pattern = r'\[([^\]]*)\]\(([^)]+)\)'
    for match in re.finditer(markdown_link_pattern, text):
        placeholder = f"__PROTECTED_{placeholder_counter}__"
        protected_placeholders[placeholder] = match.group(0)
        text = text.replace(match.group(0), placeholder, 1)
        placeholder_counter += 1
    
    # Protect markdown images: ![alt](url) or ![](url)
    markdown_image_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
    for match in re.finditer(markdown_image_pattern, text):
        placeholder = f"__PROTECTED_{placeholder_counter}__"
        protected_placeholders[placeholder] = match.group(0)
        text = text.replace(match.group(0), placeholder, 1)
        placeholder_counter += 1
    
    # Protect code blocks: ```code``` (multiline)
    code_block_pattern = r'```[^`]*```'
    for match in re.finditer(code_block_pattern, text, re.DOTALL):
        placeholder = f"__PROTECTED_{placeholder_counter}__"
        protected_placeholders[placeholder] = match.group(0)
        text = text.replace(match.group(0), placeholder, 1)
        placeholder_counter += 1
    
    # Protect inline code: `code`
    inline_code_pattern = r'`[^`]+`'
    for match in re.finditer(inline_code_pattern, text):
        placeholder = f"__PROTECTED_{placeholder_counter}__"
        protected_placeholders[placeholder] = match.group(0)
        text = text.replace(match.group(0), placeholder, 1)
        placeholder_counter += 1
    
    # Protect LaTeX blocks: ```{=latex}...```
    latex_block_pattern = r'```\{=latex\}.*?```'
    for match in re.finditer(latex_block_pattern, text, re.DOTALL):
        placeholder = f"__PROTECTED_{placeholder_counter}__"
        protected_placeholders[placeholder] = match.group(0)
        text = text.replace(match.group(0), placeholder, 1)
        placeholder_counter += 1
    
    # Find and protect already-wrapped \LR{...} blocks
    protected_pattern = r'\\LR\{[^}]*\([^)]*[A-Za-z][^)]*\)[^}]*\}'
    for match in re.finditer(protected_pattern, text):
        placeholder = f"__PROTECTED_{placeholder_counter}__"
        protected_placeholders[placeholder] = match.group(0)
        text = text.replace(match.group(0), placeholder, 1)
        placeholder_counter += 1
    
    # Also protect \textenglish{...} blocks if they exist
    protected_pattern2 = r'\\textenglish\{[^}]*\([^)]*[A-Za-z][^)]*\)[^}]*\}'
    for match in re.finditer(protected_pattern2, text):
        placeholder = f"__PROTECTED_{placeholder_counter}__"
        protected_placeholders[placeholder] = match.group(0)
        text = text.replace(match.group(0), placeholder, 1)
        placeholder_counter += 1
    
    # Pattern to match: ( followed by English text, then )
    # This matches parentheses that contain at least one English letter
    # Exclude URLs (containing :// or starting with http)
    pattern = r'\(([^)]*[A-Za-z][^)]*)\)'
    
    def replace_func(match):
        content = match.group(1)
        # Skip if it's a URL (contains :// or starts with http)
        if '://' in content or content.strip().startswith('http'):
            return match.group(0)
        # Only wrap if it contains English characters
        if content and contains_english(content):
            # Wrap with \LR{} to force LTR direction - LaTeX will handle the content as-is
            return r'\LR{(' + content + r')}'
        return match.group(0)  # Return unchanged if no English
    
    # Replace all occurrences
    fixed_text = re.sub(pattern, replace_func, text)
    
    # Restore protected blocks
    for placeholder, original in protected_placeholders.items():
        fixed_text = fixed_text.replace(placeholder, original)
    
    return fixed_text


def process_file(input_file, output_file):
    """Process a markdown file to fix bidirectional parentheses issues."""
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fix parentheses issues
        fixed_content = fix_parentheses(content)
        
        # Write the fixed content
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        print(f"Fixed bidirectional parentheses in: {input_file}")
        return True
    except Exception as e:
        print(f"Error processing {input_file}: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: fix_bidi_parentheses.py <input_file> [output_file]")
        print("If output_file is not provided, input_file will be modified in place.")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    if len(sys.argv) >= 3:
        output_file = Path(sys.argv[2])
    else:
        output_file = input_file
    
    if not input_file.exists():
        print(f"Error: Input file not found: {input_file}", file=sys.stderr)
        sys.exit(1)
    
    success = process_file(input_file, output_file)
    sys.exit(0 if success else 1)

