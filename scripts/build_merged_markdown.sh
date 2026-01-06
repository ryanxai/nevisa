# Function to strip YAML frontmatter from markdown content
strip_yaml_frontmatter() {
    awk '
    BEGIN { in_frontmatter = 0; frontmatter_count = 0 }
    /^---$/ {
        frontmatter_count++
        if (frontmatter_count == 1) {
            in_frontmatter = 1
            next
        } else if (frontmatter_count == 2) {
            in_frontmatter = 0
            next
        }
    }
    !in_frontmatter { print }
    '
}

# Function to increase heading levels in markdown content
increase_headings() {
    sed 's/^##### /###### /g; s/^#### /##### /g; s/^### /#### /g; s/^## /### /g; s/^# /## /g'
}

# Function to extract order value from filename
# Filenames follow pattern: N-filename.md or N-filename.qmd where N is the order number
get_markdown_order() {
    local file="$1"
    # Get basename without path and extension
    local filename=$(basename "$file")
    filename="${filename%.md}"
    filename="${filename%.qmd}"
    # Extract the number before the first hyphen
    local order=$(echo "$filename" | sed -n 's/^\([0-9]\+\).*/\1/p')
    if [ -z "$order" ]; then
        # Return a large number so files without order come last
        echo "999"
    else
        echo "$order"
    fi
}

# Function to extract title from metadata.yml file
# Returns the title if found, otherwise returns the folder name
get_episode_title() {
    local subdir="$1"
    local metadata_file="$subdir/metadata.yml"
    local folder_name=$(basename "$subdir")
    
    # Check if metadata.yml exists
    if [ -f "$metadata_file" ]; then
        # Extract title from metadata.yml (handles "title: value" format)
        # Remove leading/trailing whitespace and quotes if present
        local title=$(grep "^title:" "$metadata_file" | sed 's/^title:[[:space:]]*//' | sed 's/^["'\'']//' | sed 's/["'\'']$//' | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//')
        
        # If title was found and is not empty, return it
        if [ -n "$title" ]; then
            echo "$title"
            return
        fi
    fi
    
    # Fall back to folder name (convert hyphens to spaces for readability)
    echo "$folder_name" | sed 's/-/ /g'
}

# Function to extract audio URL from metadata.yml file
get_episode_audio() {
    local subdir="$1"
    local metadata_file="$subdir/metadata.yml"
    
    if [ -f "$metadata_file" ]; then
        local audio=$(grep "^original_audio:" "$metadata_file" | sed 's/^original_audio:[[:space:]]*//' | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//')
        if [ -n "$audio" ]; then
            echo "$audio"
        fi
    fi
}

# Function to extract video URL from metadata.yml file
get_episode_video() {
    local subdir="$1"
    local metadata_file="$subdir/metadata.yml"
    
    if [ -f "$metadata_file" ]; then
        local video=$(grep "^original_video:" "$metadata_file" | sed 's/^original_video:[[:space:]]*//' | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//')
        if [ -n "$video" ]; then
            echo "$video"
        fi
    fi
}

# Function to extract site URL from website _quarto.yml file
get_site_url() {
    local quarto_file="assets/website/_quarto.yml"
    
    if [ -f "$quarto_file" ]; then
        local site_url=$(grep "^[[:space:]]*site-url:" "$quarto_file" | sed 's/^[[:space:]]*site-url:[[:space:]]*//' | sed 's/^["'\'']//' | sed 's/["'\'']$//' | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//')
        if [ -n "$site_url" ]; then
            echo "$site_url"
        fi
    fi
}

# Function to combine all markdown files from subfolders
combine_markdown_files() {
    local output_file="$1"
    local docs_dir="source"

    # Find all subdirectories in docs/, collect them with their minimum order values, and sort by order
    find "$docs_dir" -type d -mindepth 1 -maxdepth 1 -not -path "*/_build*" -not -path "*/node_modules*" -not -path "*/_site*" -not -path "*/.*" | while read -r subdir; do
        # Find the minimum order value among all markdown and quarto files in this subdirectory
        min_order=999
        (find "$subdir" -name "*.md" -type f -not -path "*/_build*" -not -path "*/node_modules*" -not -path "*/_site*" -not -path "*/.*"; find "$subdir" -name "*.qmd" -type f -not -path "*/_build*" -not -path "*/node_modules*" -not -path "*/_site*" -not -path "*/.*") | while read -r md_file; do
            # Skip README.md files
            if [[ "$(basename "$md_file")" == "README.md" ]]; then
                continue
            fi
            order=$(get_markdown_order "$md_file")
            if (( order < min_order )); then
                min_order=$order
            fi
        done
        # Output in format: "min_order|subdirpath" for sorting
        echo "$min_order|$subdir"
    done | sort -t'|' -k1,1n | while IFS='|' read -r folder_order subdir; do
        # Get the folder name (last part of path)
        folder_name=$(basename "$subdir")

        # Skip if it's not a directory or if it's empty
        if [ ! -d "$subdir" ]; then
            continue
        fi

        # Add chapter header (use title from metadata.yml if available, otherwise use folder name)
        chapter_title=$(get_episode_title "$subdir")
        echo "# $chapter_title" >> "$output_file"
        echo "" >> "$output_file"
        
        # Add links section at the beginning of each chapter
        echo "## لینک ها" >> "$output_file"
        echo "" >> "$output_file"
        # Extract episode folder name (e.g., "001-Mind-Body-Unity")
        episode_folder=$(basename "$subdir")
        
        # Get site URL once for all links
        site_url=$(get_site_url)
        
        # Add transcript link if 3-transcript.md exists
        if [ -f "$subdir/3-transcript.md" ] && [ -n "$site_url" ]; then
            echo "- [ترانوشت]($site_url/$episode_folder/3-transcript.html)" >> "$output_file"
        fi
        
        # Add slides link if slides.pdf exists
        if [ -f "$subdir/slides.pdf" ] && [ -n "$site_url" ]; then
            echo "- [اسلاید ها]($site_url/$episode_folder/slides.pdf)" >> "$output_file"
        fi
        
        # Add mindmap link if mindmap_auto.html exists
        if [ -f "$subdir/mindmap_auto.html" ] && [ -n "$site_url" ]; then
            echo "- [نقشه ذهنی]($site_url/$episode_folder/mindmap_auto.html)" >> "$output_file"
        fi
        
        # Add audio (Castbox) link if available
        audio_url=$(get_episode_audio "$subdir")
        if [ -n "$audio_url" ]; then
            echo "- [پادکست با هوش مصنوعی]($audio_url)" >> "$output_file"
        fi
        
        # Add video (YouTube) link if available
        video_url=$(get_episode_video "$subdir")
        if [ -n "$video_url" ]; then
            echo "- [ویدِئو با هوش مصنوعی]($video_url)" >> "$output_file"
        fi
        
        echo "" >> "$output_file"
        printf '```{=latex}\n\\vspace{1.5em}\n```\n' >> "$output_file"
        echo "" >> "$output_file"
        
        # Add infographic image below the links section
        # First check if this episode has its own infographic, otherwise use Episode-02's infographic
        episode_infographic="$subdir/infographic.png"
        fallback_infographic="source/Episode-02/infographic.png"
        
        if [ -f "$episode_infographic" ]; then
            # Use episode-specific infographic
            # Path in markdown is relative to markdown file location (output/)
            rel_path=$(echo "$subdir" | sed 's|^source/||')
            infographic_markdown_path="../source/$rel_path/infographic.png"
            echo "![]($infographic_markdown_path){.infographic fig-cap=''}" >> "$output_file"
            echo "" >> "$output_file"
        elif [ -f "$fallback_infographic" ]; then
            # Use Episode-02 infographic as fallback
            infographic_markdown_path="../source/Episode-02/infographic.png"
            echo "![]($infographic_markdown_path){.infographic fig-cap=''}" >> "$output_file"
            echo "" >> "$output_file"
        fi

        # Find all .md and .qmd files in this subdirectory, collect them with their order values, and sort by order
        (find "$subdir" -name "*.md" -type f -not -path "*/_build*" -not -path "*/node_modules*" -not -path "*/_site*" -not -path "*/.*"; find "$subdir" -name "*.qmd" -type f -not -path "*/_build*" -not -path "*/node_modules*" -not -path "*/_site*" -not -path "*/.*") | while read -r md_file; do
            # Skip README.md files as they might be duplicates
            if [[ "$(basename "$md_file")" == "README.md" ]]; then
                continue
            fi
            # Skip *-subjects.md files (e.g., 1-subjects.md) from PDF generation
            if [[ "$(basename "$md_file")" == *"-subjects.md" ]]; then
                continue
            fi
            # Skip *-transcript.md files (e.g., 3-transcript.md) from PDF generation
            if [[ "$(basename "$md_file")" == *"-transcript.md" ]]; then
                continue
            fi

            # Get the order value for this file
            order=$(get_markdown_order "$md_file")

            # Output in format: "order|filepath" for sorting
            echo "$order|$md_file"
        done | sort -t'|' -k1,1n | while IFS='|' read -r file_order md_file; do
            # Process the file content: strip YAML frontmatter and increase heading levels
            cat "$md_file" | strip_yaml_frontmatter | increase_headings >> "$output_file"
            echo "" >> "$output_file"
            echo "" >> "$output_file"
        done

        echo "" >> "$output_file"
    done
}

# Combine all markdown files from subfolders
echo "Combining markdown files from subfolders..."
combine_markdown_files "output/Chista.md"

# Fix image paths for PDF compilation
# Change ../../assets/images/ to ../assets/images/ 
# LaTeX resolves paths relative to markdown file location (output/), so ../assets/images/ resolves correctly
# Only replace ../../assets/images/ to avoid partial matches
echo "Fixing image paths for PDF compilation..."
sed -i '' 's|../../assets/images/|../../assets/images/|g' "output/Chista.md"

# Fix bidirectional text issues with parentheses containing English text
echo "Fixing bidirectional parentheses issues..."
uv run python scripts/fix_bidi_parentheses.py "output/Chista.md"
