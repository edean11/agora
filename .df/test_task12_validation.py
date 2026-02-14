#!/usr/bin/env python3
"""
Validation test for Task 12: Vite + React + TypeScript + Tailwind setup
"""
import json
import os
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"


def test_frontend_exists():
    """Verify frontend directory exists"""
    assert FRONTEND_DIR.exists(), "frontend/ directory should exist"
    print("✓ frontend/ directory exists")


def test_package_json():
    """Verify package.json has required dependencies"""
    package_json = FRONTEND_DIR / "package.json"
    assert package_json.exists(), "package.json should exist"

    with open(package_json) as f:
        data = json.load(f)

    # Check dependencies
    deps = data.get("dependencies", {})
    assert "react-router-dom" in deps, "react-router-dom should be in dependencies"
    assert "@tanstack/react-query" in deps, "@tanstack/react-query should be in dependencies"

    # Check dev dependencies
    dev_deps = data.get("devDependencies", {})
    assert "tailwindcss" in dev_deps, "tailwindcss should be in devDependencies"
    assert "@tailwindcss/vite" in dev_deps, "@tailwindcss/vite should be in devDependencies"

    print("✓ package.json has required dependencies")


def test_vite_config():
    """Verify vite.config.ts has Tailwind plugin and proxy"""
    vite_config = FRONTEND_DIR / "vite.config.ts"
    assert vite_config.exists(), "vite.config.ts should exist"

    content = vite_config.read_text()
    assert "@tailwindcss/vite" in content, "Should import @tailwindcss/vite"
    assert "tailwindcss()" in content, "Should use tailwindcss() plugin"
    assert "port: 5173" in content, "Should configure port 5173"
    assert "'/api'" in content or '"/api"' in content, "Should have /api proxy"
    assert "localhost:8000" in content, "Should proxy to localhost:8000"
    assert "ws: true" in content, "Should enable WebSocket proxying"

    print("✓ vite.config.ts configured correctly")


def test_index_css():
    """Verify index.css has Tailwind and theme colors"""
    index_css = FRONTEND_DIR / "src" / "index.css"
    assert index_css.exists(), "src/index.css should exist"

    content = index_css.read_text()
    assert '@import "tailwindcss"' in content, "Should import tailwindcss"
    assert "@theme" in content, "Should have @theme directive"
    assert "--color-parchment" in content, "Should define parchment color"
    assert "--color-gold" in content, "Should define gold color"
    assert "--color-charcoal" in content, "Should define charcoal color"
    assert "--font-display" in content, "Should define display font"
    assert "Cinzel" in content, "Should use Cinzel font"
    assert "Cormorant Garamond" in content, "Should use Cormorant Garamond font"

    print("✓ index.css configured with theme")


def test_index_html():
    """Verify index.html has Google Fonts and correct title"""
    index_html = FRONTEND_DIR / "index.html"
    assert index_html.exists(), "index.html should exist"

    content = index_html.read_text()
    assert "<title>Agora</title>" in content, "Title should be 'Agora'"
    assert "fonts.googleapis.com" in content, "Should load Google Fonts"
    assert "Cinzel" in content, "Should load Cinzel font"
    assert "Cormorant+Garamond" in content, "Should load Cormorant Garamond font"

    print("✓ index.html configured correctly")


def test_app_tsx():
    """Verify App.tsx has Greek theme classes"""
    app_tsx = FRONTEND_DIR / "src" / "App.tsx"
    assert app_tsx.exists(), "src/App.tsx should exist"

    content = app_tsx.read_text()
    assert "bg-parchment" in content, "Should use parchment background"
    assert "text-charcoal" in content, "Should use charcoal text color"
    assert "font-display" in content, "Should use display font"
    assert "font-body" in content, "Should use body font"
    assert "Agora" in content, "Should display 'Agora' heading"

    # Should NOT have default boilerplate
    assert "Vite + React" not in content, "Should not have default Vite boilerplate"
    assert "count" not in content, "Should not have counter example"

    print("✓ App.tsx cleaned up with Greek theme")


def test_typescript_compiles():
    """Verify TypeScript compiles with no errors"""
    result = subprocess.run(
        ["npx", "tsc", "--noEmit"],
        cwd=FRONTEND_DIR,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"TypeScript should compile with no errors:\n{result.stderr}"
    print("✓ TypeScript compiles successfully")


def test_build_succeeds():
    """Verify npm run build succeeds"""
    result = subprocess.run(
        ["npm", "run", "build"],
        cwd=FRONTEND_DIR,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"Build should succeed:\n{result.stderr}"

    # Check that dist/ was created
    dist_dir = FRONTEND_DIR / "dist"
    assert dist_dir.exists(), "dist/ directory should be created"
    assert (dist_dir / "index.html").exists(), "dist/index.html should exist"

    print("✓ Build succeeds")


def test_custom_colors_in_build():
    """Verify custom theme colors are in the build output"""
    dist_dir = FRONTEND_DIR / "dist"
    css_files = list(dist_dir.glob("assets/*.css"))
    assert len(css_files) > 0, "Should have CSS files in dist/assets/"

    css_content = css_files[0].read_text()
    assert "--color-parchment" in css_content or "parchment" in css_content, "Should include parchment color"
    assert "--color-charcoal" in css_content or "charcoal" in css_content, "Should include charcoal color"

    print("✓ Custom colors present in build output")


if __name__ == "__main__":
    print("Running Task 12 validation tests...\n")

    test_frontend_exists()
    test_package_json()
    test_vite_config()
    test_index_css()
    test_index_html()
    test_app_tsx()
    test_typescript_compiles()
    test_build_succeeds()
    test_custom_colors_in_build()

    print("\n✅ All Task 12 validation tests passed!")
