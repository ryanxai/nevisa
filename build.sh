# Clean up previous build outputs
echo "Cleaning up previous build outputs..."
rm -f output/Chista.md
rm -f output/Chista.pdf

# Build process
./scripts/build_meta_markdowns.sh
./scripts/build_merged_markdown.sh
./scripts/build_book.sh
./scripts/build_site.sh

# Clean up README.md files from source directory after build
echo "Cleaning up README.md files from source directory..."
rm -f source/README.md
find source -type f -name "README.md" -delete
