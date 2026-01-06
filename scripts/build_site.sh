cd assets/website
cp -r ../../source/*  ./
mv README.md index.md
# Rename README.md files in subdirectories to index.md so Quarto renders them as index pages
find . -type f -name "README.md" -not -path "./README.md" | while read -r readme_file; do
    dir=$(dirname "$readme_file")
    mv "$readme_file" "$dir/index.md"
done
quarto render --to html
# Remove all copied source files, but keep _quarto.yml, _site/, site_libs/, and the PDF
find . -mindepth 1 -maxdepth 1 ! -name _metadata.yml ! -name 'header.html' ! -name 'prompts.txt' ! -name 'logo.svg' ! -name 'icon.png' ! -name '_quarto.yml' ! -name '_site' ! -name 'site_libs' ! -name '.quarto' ! -name 'index.qmd' ! -name 'about.qmd' ! -name 'theme.scss' ! -name 'theme-dark.scss' ! -exec rm -rf {} +
rm -rf ../../output/site/*
mv _site/* ../../output/site
# Copy images directory so images are accessible from the website
mkdir -p ../../output/site/assets
cp -r ../../assets/images ../../output/site/assets/
# Copy audio files (MP3, etc.) from source to output, preserving directory structure
find ../../source -type f \( -name "*.mp3" -o -name "*.wav" -o -name "*.ogg" -o -name "*.m4a" \) | while read audio_file; do
  rel_path="${audio_file#../../source/}"
  target_dir="../../output/site/$(dirname "$rel_path")"
  mkdir -p "$target_dir"
  cp "$audio_file" "$target_dir/"
done
# Copy PDF files (slides.pdf, etc.) from source to output, preserving directory structure
find ../../source -type f -name "*.pdf" | while read pdf_file; do
  rel_path="${pdf_file#../../source/}"
  target_dir="../../output/site/$(dirname "$rel_path")"
  mkdir -p "$target_dir"
  cp "$pdf_file" "$target_dir/"
done
# Copy the generated PDF to output/site as Nadastan-Ba-Ryan.pdf (to match website configuration)
if [ -f "../../output/Chista.pdf" ]; then
  cp "../../output/Chista.pdf" "../../output/site/Chista.pdf"
fi
# Convert dates in HTML files to Jalali (Persian) format
if [ -d "../../output/site" ] && [ -d "../../source" ]; then
  uv run python3 ../../scripts/convert_dates_to_jalali.py ../../source ../../output/site
fi
rm -rf .quarto
rm -rf _site
