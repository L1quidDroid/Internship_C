#!/usr/bin/env python3
"""
Convert Triskele SVG logos to PNG for PDF reports.

ReportLab doesn't natively support SVG, so we convert to PNG using cairosvg or Pillow.
"""

import sys
from pathlib import Path

def convert_svg_to_png():
    """Convert SVG logos to PNG format."""
    
    # Source SVG
    svg_path = Path('static/img/triskele_logo.svg')
    
    # Destination PNG
    png_path = Path('plugins/reporting/static/assets/triskele_logo.png')
    
    if not svg_path.exists():
        print(f"❌ SVG logo not found: {svg_path}")
        return False
    
    print(f"🔄 Converting {svg_path} to PNG...")
    
    # Try different conversion methods
    
    # Method 1: cairosvg (best quality)
    try:
        import cairosvg
        cairosvg.svg2png(
            url=str(svg_path),
            write_to=str(png_path),
            output_width=400,  # 400px width (will scale to 120px in PDF)
            output_height=133  # Maintain aspect ratio (3:1)
        )
        print(f"✅ Converted using cairosvg: {png_path}")
        print(f"   Size: {png_path.stat().st_size / 1024:.1f} KB")
        return True
    except ImportError:
        print("⚠️  cairosvg not installed, trying alternative method...")
    except Exception as e:
        print(f"⚠️  cairosvg failed: {e}, trying alternative...")
    
    # Method 2: svglib + reportlab (fallback)
    try:
        from svglib.svglib import svg2rlg
        from reportlab.graphics import renderPM
        
        drawing = svg2rlg(str(svg_path))
        
        # Scale to desired size
        drawing.width = 400
        drawing.height = 133
        drawing.scale(400/drawing.width, 133/drawing.height)
        
        renderPM.drawToFile(drawing, str(png_path), fmt='PNG')
        print(f"✅ Converted using svglib: {png_path}")
        print(f"   Size: {png_path.stat().st_size / 1024:.1f} KB")
        return True
    except ImportError:
        print("⚠️  svglib not installed, trying manual conversion...")
    except Exception as e:
        print(f"⚠️  svglib failed: {e}")
    
    # Method 3: Manual instructions
    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("❌ Automatic conversion failed")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("\nManual conversion options:")
    print("\n1. Install conversion tool:")
    print("   pip install cairosvg")
    print("   Then run this script again")
    print("\n2. Convert manually using ImageMagick:")
    print(f"   convert -density 300 -background none {svg_path} {png_path}")
    print("\n3. Convert online:")
    print("   - Open: https://cloudconvert.com/svg-to-png")
    print(f"   - Upload: {svg_path}")
    print("   - Download and save to: {png_path}")
    print("\n4. Use macOS Preview:")
    print(f"   - Open {svg_path} in Preview")
    print("   - File → Export → Format: PNG")
    print("   - Width: 400px")
    print(f"   - Save to: {png_path}")
    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    return False

if __name__ == '__main__':
    success = convert_svg_to_png()
    sys.exit(0 if success else 1)
