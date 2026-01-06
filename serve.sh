SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/output/site"
python3 "$SCRIPT_DIR/serve.py"
