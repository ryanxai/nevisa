cd assets/book
# Generate Persian date file before Quarto compilation
cd ../..
uv run python scripts/get_persian_date.py > assets/book/persian-date.tex
cd assets/book
quarto render --to pdf
# Find the PDF file (it may have a Persian filename) and copy it
PDF_FILE=$(find _book -name "*.pdf" -type f | head -1)
if [ -n "$PDF_FILE" ]; then
  cp "$PDF_FILE" ../../output/Chista.pdf
else
  echo "Error: PDF file not found in _book directory"
  exit 1
fi
rm -rf _book
rm -rf .gitignore
rm -rf .quarto
rm -rf output
rm -f persian-date.tex
