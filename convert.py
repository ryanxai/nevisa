#!/usr/bin/env python3
"""
Convert mindmap.html to mindmap_auto.html with:
1. Font-family changed to Vazirmatn
2. Auto-fit functionality on node expand/collapse
3. Automatic Quarto theme detection (light/dark mode)
"""

import re
from pathlib import Path


def convert_mindmap_to_auto_fit(input_file: str, output_file: str):
    """
    Convert mindmap.html to mindmap_auto.html with:
    - Font-family changed to Vazirmatn
    - Auto-fit on expand/collapse
    - Automatic Quarto theme detection
    
    Args:
        input_file: Path to input mindmap.html file
        output_file: Path to output mindmap_auto.html file
    """
    # Read the input file
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace font-family with Vazirmatn
    font_family_pattern = r'html \{\s+font-family:[^;]+;\s+\}'
    vazirmatn_font = '''html {
  font-family: 'Vazirmatn', ui-sans-serif, system-ui, sans-serif;
}'''
    content = re.sub(font_family_pattern, vazirmatn_font, content, flags=re.DOTALL)
    
    # Replace the original dark mode check with Quarto theme detection
    # Original: if (window.matchMedia("(prefers-color-scheme: dark)").matches) { ... }
    dark_mode_pattern = r'if \(window\.matchMedia\("\(prefers-color-scheme: dark\)"\)\.matches\) \{[^}]+\}'
    
    # New theme detection code that works with Quarto sites
    quarto_theme_code = '''// Quarto theme detection - automatically match parent site's theme
              const detectQuartoTheme = () => {
                // Get the target document (parent if in iframe, otherwise current)
                let targetDoc = document;
                let targetWin = window;
                try {
                  if (window.parent && window.parent !== window && window.parent.document) {
                    targetDoc = window.parent.document;
                    targetWin = window.parent;
                  }
                } catch (e) {
                  // Cross-origin - use current document
                }
                
                const bodyEl = targetDoc.body;
                
                // Method 1: Check Quarto's active Bootstrap stylesheet (most reliable)
                // Quarto uses link#quarto-bootstrap with data-mode="dark" or "light"
                try {
                  const activeSheet = targetDoc.querySelector('link#quarto-bootstrap:not([rel=disabled-stylesheet])');
                  if (activeSheet) {
                    const mode = activeSheet.getAttribute('data-mode');
                    if (mode === 'dark') return true;
                    if (mode === 'light') return false;
                  }
                } catch (e) {}
                
                // Method 2: Check body classes (quarto-dark / quarto-light)
                if (bodyEl) {
                  if (bodyEl.classList.contains('quarto-dark')) return true;
                  if (bodyEl.classList.contains('quarto-light')) return false;
                }
                
                // Method 3: Check localStorage for Quarto's theme preference
                try {
                  const storageValue = targetWin.localStorage.getItem('quarto-color-scheme');
                  if (storageValue === 'alternate') return true;  // dark mode
                  if (storageValue === 'default') return false;   // light mode
                } catch (e) {}
                
                // Method 4: Check computed background color
                if (bodyEl) {
                  try {
                    const bgColor = targetWin.getComputedStyle(bodyEl).backgroundColor;
                    const rgbMatch = bgColor.match(/[0-9]+/g);
                    if (rgbMatch && rgbMatch.length >= 3) {
                      const r = parseInt(rgbMatch[0], 10);
                      const g = parseInt(rgbMatch[1], 10);
                      const b = parseInt(rgbMatch[2], 10);
                      const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
                      if (luminance < 0.4) return true;
                      if (luminance > 0.6) return false;
                    }
                  } catch (e) {}
                }
                
                // Fallback to system preference
                return window.matchMedia('(prefers-color-scheme: dark)').matches;
              };
              
              const applyTheme = (isDark) => {
                if (isDark) {
                  document.documentElement.classList.add('markmap-dark');
                } else {
                  document.documentElement.classList.remove('markmap-dark');
                }
              };
              
              // Wait a bit for Quarto to initialize, then apply theme
              setTimeout(() => {
                applyTheme(detectQuartoTheme());
              }, 100);
              
              // Poll frequently to catch theme changes
              setInterval(() => {
                applyTheme(detectQuartoTheme());
              }, 150);
              
              // Also observe parent body class changes directly
              try {
                let targetDoc = document;
                try {
                  if (window.parent && window.parent !== window && window.parent.document) {
                    targetDoc = window.parent.document;
                  }
                } catch (e) {}
                
                if (targetDoc.body) {
                  new MutationObserver(() => {
                    applyTheme(detectQuartoTheme());
                  }).observe(targetDoc.body, {
                    attributes: true,
                    attributeFilter: ['class']
                  });
                }
              } catch (e) {}
              
              // Listen for system preference changes
              window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
                applyTheme(detectQuartoTheme());
              });'''
    
    # Auto-fit code to insert
    auto_fit_code = '''
              // Auto-fit functionality on node expand/collapse - fast and responsive
              setTimeout(() => {
                if (!window.mm) return;
                
                const svg = d3.select("svg#mindmap");
                let fitTimer = null;
                let isFitting = false;
                
                // Fast fit with debouncing
                const autoFit = () => {
                  if (isFitting) return; // Prevent overlapping fits
                  if (fitTimer) clearTimeout(fitTimer);
                  
                  fitTimer = setTimeout(() => {
                    if (window.mm && !isFitting) {
                      isFitting = true;
                      window.mm.fit();
                      // Reset flag quickly
                      setTimeout(() => { isFitting = false; }, 50);
                    }
                  }, 100); // Minimal delay - just wait for expand/collapse to start
                };
                
                // Listen for clicks on expand/collapse circles
                svg.selectAll("circle").on("click.autoFit", autoFit);
                
                // Watch for structural changes (nodes expanding/collapsing)
                const observer = new MutationObserver((mutations) => {
                  const hasNodeChange = mutations.some(m => 
                    m.type === 'childList' && 
                    (m.addedNodes.length > 0 || m.removedNodes.length > 0)
                  );
                  if (hasNodeChange) {
                    autoFit();
                  }
                });
                
                const mainGroup = svg.select("g").node();
                if (mainGroup) {
                  observer.observe(mainGroup, {
                    childList: true,
                    subtree: true
                  });
                }
              }, 50);'''
    
    # Combined replacement code
    full_replacement = quarto_theme_code + '\n' + auto_fit_code
    
    # Replace the dark mode check with our Quarto theme detection + auto-fit
    modified_content = re.sub(dark_mode_pattern, full_replacement, content, flags=re.DOTALL)
    
    # If pattern wasn't found, try alternative insertion
    if modified_content == content:
        # Find the pattern: })(() => window.markmap,null,{...})
        pattern2 = r'(\}\)\(\(\) => window\.markmap,null,\{)'
        modified_content = re.sub(pattern2, full_replacement + r'\n            \1', content, flags=re.DOTALL)
    
    # If still no match, insert before the last </script>
    if modified_content == content:
        last_script_pos = content.rfind('</script>')
        if last_script_pos != -1:
            modified_content = content[:last_script_pos] + full_replacement + '\n            ' + content[last_script_pos:]
        else:
            print("Warning: Could not find insertion point. Output may be incorrect.")
            modified_content = content
    
    # Write the output file
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(modified_content)
    
    print(f"Successfully converted {input_file} to {output_file}")
    print("Font-family has been changed to Vazirmatn.")
    print("Auto-fit functionality has been added for node expand/collapse events.")


if __name__ == "__main__":
    # Get the script directory
    script_dir = Path(__file__).parent
    
    # Define input and output paths
    input_file = script_dir / "source" / "Episode-02" / "mindmap.html"
    output_file = script_dir / "source" / "Episode-02" / "mindmap_auto.html"
    
    # Convert the file
    convert_mindmap_to_auto_fit(str(input_file), str(output_file))