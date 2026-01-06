# Clean up previous build outputs
echo "Cleaning up previous build outputs..."
rm -f output/Chista.md
rm -f output/Chista.pdf

# Build process
./scripts/build_meta_markdowns.sh
./scripts/build_merged_markdown.sh
./scripts/build_book.sh
./scripts/build_site.sh
