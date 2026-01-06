set -e

cd source

# Function to extract value from a YAML file
extract_yaml_value() {
    local file="$1"
    local key="$2"
    
    if [ ! -f "$file" ]; then
        return
    fi
    
    # Extract value for the given key from YAML file
    awk -v key="$key" '
        BEGIN { found = 0 }
        /^[^#]*:/ {
            # Extract key name (everything before colon)
            current_key = $0
            sub(/:.*$/, "", current_key)
            gsub(/^[ \t]+|[ \t]+$/, "", current_key)
            
            if (current_key == key) {
                # Extract value (everything after colon)
                value = $0
                sub(/^[^:]*:[ \t]*/, "", value)
                gsub(/^["'\'']|["'\'']$/, "", value)  # Remove quotes
                gsub(/^[ \t]+|[ \t]+$/, "", value)   # Trim whitespace
                print value
                found = 1
                exit
            }
        }
        END { if (!found) exit 1 }
    ' "$file"
}

# Function to extract title from YAML front matter or first heading from a markdown file
extract_heading() {
    local file="$1"
    local heading=""
    
    # First, try to extract title from YAML front matter
    # Check if file starts with --- (YAML front matter)
    if head -n 1 "$file" | grep -q '^---$'; then
        # Extract title field from front matter (between first and second ---)
        heading=$(awk '
            BEGIN { in_frontmatter = 0; frontmatter_count = 0 }
            /^---$/ {
                frontmatter_count++
                if (frontmatter_count == 1) {
                    in_frontmatter = 1
                    next
                } else if (frontmatter_count == 2) {
                    in_frontmatter = 0
                    exit
                }
            }
            in_frontmatter && /^title:/ {
                # Extract value after "title:" and remove quotes
                gsub(/^title:[ \t]*["'\'']?/, "")
                gsub(/["'\'']?[ \t]*$/, "")
                print
                exit
            }
        ' "$file")
    fi
    
    # If no title found in front matter, try to find the first heading
    if [ -z "$heading" ]; then
        # Find the first line starting with #, remove the # and trim whitespace
        heading=$(grep -m 1 '^#' "$file" | sed 's/^#* *//' | sed 's/ *$//')
    fi
    
    # Fallback to filename if no heading found
    if [ -z "$heading" ]; then
        local filename=$(basename "$file")
        # Remove .md or .qmd extension
        filename="${filename%.md}"
        filename="${filename%.qmd}"
        heading=$(echo "$filename" | sed 's/_/ /g' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) tolower(substr($i,2))}1')
    fi
    
    echo "$heading"
}

# Function to extract the order field from filename
# Filenames follow pattern: N-filename.md or N-filename.qmd where N is the order number
extract_order() {
    local file="$1"
    # Get basename without path and extension
    local filename=$(basename "$file")
    filename="${filename%.md}"
    filename="${filename%.qmd}"
    # Extract the number before the first hyphen
    local order=$(echo "$filename" | sed -n 's/^\([0-9]\+\).*/\1/p')
    if [ -z "$order" ]; then
        # Return a large number so files without order come last
        echo "999999"
    else
        echo "$order"
    fi
}

# Function to create README for a subfolder
create_subfolder_readme() {
    local folder="$1"
    local folder_name="$2"

    # Look for metadata.yml file in the episode directory
    episode_yml=""
    if [ -f "$folder/metadata.yml" ]; then
        episode_yml="$folder/metadata.yml"
    fi

    # Extract title, audio, video, and original source from metadata.yml if it exists
    readme_title=""
    audio_url=""
    video_url=""
    original_link=""
    if [ -n "$episode_yml" ] && [ -f "$episode_yml" ]; then
        readme_title=$(extract_yaml_value "$episode_yml" "title")
        audio_url=$(extract_yaml_value "$episode_yml" "audio")
        video_url=$(extract_yaml_value "$episode_yml" "video")
        original_link=$(extract_yaml_value "$episode_yml" "original_link")
    fi
    
    # If no title found from episode yml, use the formatted folder name
    if [ -z "$readme_title" ]; then
        readme_title="$folder_name"
    fi

    echo "# $readme_title" > "$folder/README.md"
    
    # Add infographic image if it exists (above the audio player)
    if [ -f "$folder/infographic.png" ]; then
        echo "" >> "$folder/README.md"
        echo "![](./infographic.png){.infographic}" >> "$folder/README.md"
        echo "" >> "$folder/README.md"
    fi
    
    # Add episode player if audio URL exists
    if [ -n "$audio_url" ]; then
        echo '<div class="episode-player" style="border: none; overflow: hidden; margin: 0 0 1em 0; padding: 0; display: block;">' >> "$folder/README.md"
        echo '<iframe' >> "$folder/README.md"
        echo "  src=\"$audio_url\"" >> "$folder/README.md"
        echo '  width="100%"' >> "$folder/README.md"
        echo '  height="200px"' >> "$folder/README.md"
        echo '  style="border: none; margin: 0; padding: 0; display: block;"' >> "$folder/README.md"
        echo '  allow="autoplay"' >> "$folder/README.md"
        echo '></iframe>' >> "$folder/README.md"
        echo '</div>' >> "$folder/README.md"
    fi
    
    # Add video player if video URL exists
    if [ -n "$video_url" ]; then
        echo '<div class="episode-player" style="border: none; overflow: hidden; margin: 0 0 1em 0; padding: 0; display: block;">' >> "$folder/README.md"
        echo '<iframe' >> "$folder/README.md"
        echo "  src=\"$video_url\"" >> "$folder/README.md"
        echo '  width="100%"' >> "$folder/README.md"
        echo '  height="415px"' >> "$folder/README.md"
        echo '  style="border: none; margin: 0; padding: 0; display: block;"' >> "$folder/README.md"
        echo '  title="YouTube video player"' >> "$folder/README.md"
        echo '  frameborder="0"' >> "$folder/README.md"
        echo '  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"' >> "$folder/README.md"
        echo '  referrerpolicy="strict-origin-when-cross-origin"' >> "$folder/README.md"
        echo '  allowfullscreen' >> "$folder/README.md"
        echo '></iframe>' >> "$folder/README.md"
        echo '</div>' >> "$folder/README.md"
    fi
    
    # Add slides download link
    echo "[اسلایدها](./slides.pdf)" >> "$folder/README.md"
    echo "" >> "$folder/README.md"
    
    # Add mindmap link if mindmap_auto.html exists
    if [ -f "$folder/mindmap_auto.html" ]; then
        echo "[نقشه ذهنی](./mindmap_auto.html)" >> "$folder/README.md"
        echo "" >> "$folder/README.md"
    fi
    
    # Add original source link if it exists
    if [ -n "$original_link" ]; then
        echo "[لینک منبع اصلی]($original_link)" >> "$folder/README.md"
        echo "" >> "$folder/README.md"
    fi

    # Find all .md and .qmd files in the folder (excluding README.md and *-subjects.md)
    # Sort by order first, then alphabetically
    (find "$folder" -maxdepth 1 -name "*.md" ! -name "README.md" ! -name "*-subjects.md"; find "$folder" -maxdepth 1 -name "*.qmd") | while read -r file; do
        order=$(extract_order "$file")
        echo "$order|$file"
    done | sort -t'|' -k1,1n -k2,2 | cut -d'|' -f2- | while read -r file; do
        # Extract the first heading from the file to use as callout title
        title=$(extract_heading "$file")
        
        # Start callout block (collapsible)
        echo "" >> "$folder/README.md"
        echo ":::{.callout-note collapse=\"true\"}" >> "$folder/README.md"
        echo "## $title" >> "$folder/README.md"
        echo "" >> "$folder/README.md"
        
        # Read file content and append to README
        # Skip YAML front matter if present and remove the first heading to avoid duplication
        if head -n 1 "$file" | grep -q '^---$'; then
            # Skip YAML front matter (everything between first and second ---)
            # Also skip the first heading line
            awk -v title="$title" '
                BEGIN { in_frontmatter = 0; frontmatter_count = 0; first_heading_skipped = 0 }
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
                !in_frontmatter {
                    # Skip the first heading line that matches the title
                    if (!first_heading_skipped && /^#+[ \t]*/) {
                        heading_text = $0
                        gsub(/^#+[ \t]*/, "", heading_text)
                        gsub(/[ \t]*$/, "", heading_text)
                        if (heading_text == title) {
                            first_heading_skipped = 1
                            next
                        }
                    }
                    print
                }
            ' "$file" >> "$folder/README.md"
        else
            # No YAML front matter, skip the first heading line
            awk -v title="$title" '
                BEGIN { first_heading_skipped = 0 }
                {
                    # Skip the first heading line that matches the title
                    if (!first_heading_skipped && /^#+[ \t]*/) {
                        heading_text = $0
                        gsub(/^#+[ \t]*/, "", heading_text)
                        gsub(/[ \t]*$/, "", heading_text)
                        if (heading_text == title) {
                            first_heading_skipped = 1
                            next
                        }
                    }
                    print
                }
            ' "$file" >> "$folder/README.md"
        fi
        
        # Close callout block
        echo "" >> "$folder/README.md"
        echo ":::" >> "$folder/README.md"
    done

    echo "" >> "$folder/README.md"
}

# Function to create main README.md
create_main_readme() {
    echo "#  فهرست مطالب" > README.md
    echo "" >> README.md

    # Find all subdirectories and sort them
    find . -maxdepth 1 -type d ! -name "." ! -name "_build" | sort | while read -r dir; do
        # Get directory name without leading ./
        dirname=$(basename "$dir")
        # Convert to readable name (replace hyphens with spaces, capitalize)
        display_name=$(echo "$dirname" | sed 's/-/ /g' | sed 's/\b\w/\U&/g')

        # Check if README.md exists in this subdirectory
        if [ -f "$dir/README.md" ]; then
            # Try to find metadata.yml file to get the title
            episode_yml=""
            if [ -f "$dir/metadata.yml" ]; then
                episode_yml="$dir/metadata.yml"
            fi
            link_text=""
            
            # Extract title from metadata.yml if it exists
            if [ -n "$episode_yml" ] && [ -f "$episode_yml" ]; then
                link_text=$(extract_yaml_value "$episode_yml" "title")
            fi
            
            # If no title found from episode yml, try README.md
            if [ -z "$link_text" ]; then
                link_text=$(extract_heading "$dir/README.md")
            fi
            
            # If still no heading found, use the display name
            if [ -z "$link_text" ]; then
                link_text="$display_name"
            fi
            
            # Add link to the episode's directory (Quarto will render README.md as index)
            echo "  - [$link_text]($dirname/)" >> README.md
        fi
    done
}

# Main execution
echo "Generating README files..."

# Create README.md for each subfolder
for dir in */; do
    if [ -d "$dir" ] && [ "$dir" != "_build/" ]; then
        folder_name=$(basename "$dir")
        display_name=$(echo "$folder_name" | sed 's/-/ /g' | sed 's/\b\w/\U&/g')
        create_subfolder_readme "$folder_name" "$display_name"
        echo "Created README.md for $folder_name/"
    fi
done

# Create main README.md
create_main_readme
