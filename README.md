# نویسا

سیستم انتشار محتوای ایستا به زبان فارسی

## Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/ryanxai/chista.ryanxai.com.git
   ```

2. **Install Quarto**:
   ```bash
   brew install --cask quarto
   ```

3. **Install XeLaTeX**:
   ```bash
   brew install --cask basictex
   ```
4. **Set up Python virtual environment**
   ```bash
   uv sync
   ```

5. **Install Vazirmatn font**:
   ```bash
   brew install --cask font-vazirmatn
   ```

## How to use

### Build All
```bash
./build.sh
```
It builds all the documentation files including the book (PDF) and creates the website in the `output/site/` directory.

### Serve Website Locally
```bash
./serve.sh
```
Starts a local web server for the documentation website in the [http://localhost:8000/](http://localhost:8000/) address.
