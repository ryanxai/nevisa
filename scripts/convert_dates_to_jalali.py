#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to convert Gregorian dates in HTML files to Jalali (Persian) dates.
Reads dates from metadata.yml files in source directory and updates corresponding HTML files.
"""
import sys
import re
import os
from datetime import datetime
from pathlib import Path

try:
    from khayyam import JalaliDatetime
    
    def convert_to_jalali(gregorian_date_str):
        """
        Convert a Gregorian date string to Jalali format.
        Handles formats like: "Jan 15, 2024", "January 15, 2024", "2024-01-15"
        """
        # Try different date formats
        date_formats = [
            "%Y-%m-%d",       # 2024-01-15 (ISO format - most common in metadata.yml)
            "%b %d, %Y",      # Jan 15, 2024
            "%B %d, %Y",      # January 15, 2024
            "%d %b %Y",       # 15 Jan 2024
            "%d %B %Y",       # 15 January 2024
        ]
        
        gregorian_date = None
        for fmt in date_formats:
            try:
                gregorian_date = datetime.strptime(gregorian_date_str.strip(), fmt)
                break
            except ValueError:
                continue
        
        if gregorian_date is None:
            return None  # Return None if can't parse
        
        # Convert to Jalali
        jalali_date = JalaliDatetime(gregorian_date)
        
        # Format: Persian date with month name (e.g., "۱۶ دی ۱۴۰۴")
        persian_date = jalali_date.strftime('%d %B %Y')
        
        # Convert English numerals to Persian numerals
        persian_digits = {
            '0': '۰', '1': '۱', '2': '۲', '3': '۳', '4': '۴',
            '5': '۵', '6': '۶', '7': '۷', '8': '۸', '9': '۹'
        }
        
        # Replace each English digit with Persian digit
        persian_date_converted = ''.join(persian_digits.get(char, char) for char in persian_date)
        
        return persian_date_converted
    
    def read_metadata_dates(source_dir):
        """
        Read dates from all metadata.yml files in source directory.
        Returns a dict mapping folder names to dates.
        """
        date_map = {}
        source_path = Path(source_dir)
        
        if not source_path.exists():
            return date_map
        
        # Find all metadata.yml files
        for metadata_file in source_path.rglob('metadata.yml'):
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Parse YAML (handle both YAML and simple key:value format)
                    metadata = {}
                    for line in content.split('\n'):
                        if ':' in line and not line.strip().startswith('#'):
                            key, value = line.split(':', 1)
                            key = key.strip()
                            value = value.strip().strip('"').strip("'")
                            metadata[key] = value
                    
                    if 'date' in metadata:
                        folder_name = metadata_file.parent.name
                        date_map[folder_name] = metadata['date']
            except Exception as e:
                print(f"Warning: Could not read {metadata_file}: {e}")
                continue
        
        return date_map
    
    def update_html_with_jalali_date(html_content, jalali_date):
        """
        Update HTML content to replace dates in listing-date divs with Jalali date.
        """
        # Pattern to match content inside listing-date divs
        # This will match any text between <div class="listing-date"> and </div>
        pattern = r'(<div class="listing-date">\s*)(.*?)(\s*</div>)'
        
        def replace_date(match):
            return match.group(1) + jalali_date + match.group(3)
        
        modified_content = re.sub(pattern, replace_date, html_content, flags=re.DOTALL)
        
        return modified_content
    
    def convert_html_dates(html_content, date_map, html_file_path):
        """
        Find and convert date strings in HTML content based on metadata dates.
        """
        # Extract folder name from HTML file path (e.g., "001-Mind-Body-Unity" from "output/site/001-Mind-Body-Unity/index.html")
        html_path = Path(html_file_path)
        
        # For index.html, we need to find dates in listing-date divs and match them to metadata
        # For other HTML files, we can use the folder name
        
        # If this is index.html, we need to handle multiple listings
        if html_path.name == 'index.html':
            # Find all listing-date divs and match them to folder names from nearby hrefs
            modified_content = html_content
            
            # Find all listing-date divs
            date_div_pattern = r'<div class="listing-date">\s*(.*?)\s*</div>'
            date_matches = list(re.finditer(date_div_pattern, modified_content, flags=re.DOTALL))
            
            # Process each date div
            replacements = []
            for date_match in date_matches:
                date_start = date_match.start()
                date_end = date_match.end()
                current_date = date_match.group(1).strip()
                full_div = date_match.group(0)
                
                # Look backwards in the content to find the nearest href with folder name
                # Search up to 500 characters before the date div
                search_start = max(0, date_start - 500)
                context_before = modified_content[search_start:date_start]
                
                # Find all hrefs in the context before this date div
                href_matches = list(re.finditer(r'<a href="\./([^/]+)/', context_before))
                
                if href_matches:
                    # Use the last (closest) href match
                    folder_name = href_matches[-1].group(1)
                    
                    # Check if we have a date for this folder in metadata
                    if folder_name in date_map:
                        gregorian_date = date_map[folder_name]
                        jalali_date = convert_to_jalali(gregorian_date)
                        if jalali_date and jalali_date != current_date:
                            # Replace the date content within the div, preserving whitespace
                            new_div = re.sub(
                                r'(<div class="listing-date">\s*)(.*?)(\s*</div>)',
                                r'\1' + jalali_date + r'\3',
                                full_div,
                                flags=re.DOTALL
                            )
                            replacements.append((date_start, date_end, new_div))
            
            # Apply replacements from end to start to preserve indices
            for start, end, new_div in reversed(replacements):
                modified_content = modified_content[:start] + new_div + modified_content[end:]
            
            return modified_content
        else:
            # For other HTML files, find the folder name and update dates
            folder_name = html_path.parent.name if html_path.parent.name != 'site' else html_path.stem
            
            if folder_name in date_map:
                gregorian_date = date_map[folder_name]
                jalali_date = convert_to_jalali(gregorian_date)
                if jalali_date:
                    # Update listing-date divs
                    modified_content = update_html_with_jalali_date(html_content, jalali_date)
                    return modified_content
            
            return html_content
    
    if __name__ == "__main__":
        import glob
        
        if len(sys.argv) < 3:
            print("Usage: convert_dates_to_jalali.py <source_directory> <html_output_directory>")
            print("Example: convert_dates_to_jalali.py source output/site")
            sys.exit(1)
        
        source_dir = sys.argv[1]
        html_output_dir = sys.argv[2]
        
        if not os.path.isdir(source_dir):
            print(f"Error: Source directory {source_dir} does not exist")
            sys.exit(1)
        
        if not os.path.isdir(html_output_dir):
            print(f"Error: HTML output directory {html_output_dir} does not exist")
            sys.exit(1)
        
        # Read dates from metadata.yml files
        print(f"Reading dates from metadata.yml files in {source_dir}...")
        date_map = read_metadata_dates(source_dir)
        
        if not date_map:
            print("Warning: No dates found in metadata.yml files")
            sys.exit(0)
        
        print(f"Found dates for {len(date_map)} folders:")
        for folder, date in date_map.items():
            jalali_date = convert_to_jalali(date)
            print(f"  {folder}: {date} -> {jalali_date}")
        
        # Find all HTML files recursively
        html_files = glob.glob(os.path.join(html_output_dir, '**/*.html'), recursive=True)
        
        if not html_files:
            print(f"No HTML files found in {html_output_dir}")
            sys.exit(0)
        
        converted_count = 0
        for html_file in html_files:
            try:
                # Read HTML file
                with open(html_file, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                # Convert dates based on metadata
                converted_content = convert_html_dates(html_content, date_map, html_file)
                
                # Only write if content changed
                if converted_content != html_content:
                    # Write back
                    with open(html_file, 'w', encoding='utf-8') as f:
                        f.write(converted_content)
                    converted_count += 1
                    print(f"Converted dates in {html_file}")
            
            except Exception as e:
                print(f"Error processing {html_file}: {e}")
        
        print(f"Successfully converted dates in {converted_count} file(s)")

except ImportError:
    print("Error: khayyam library not installed. Install it with: pip install khayyam")
    sys.exit(1)

