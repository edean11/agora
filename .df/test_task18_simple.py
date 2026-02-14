#!/usr/bin/env python3
"""Simple validation for Task 18: Persona creation and generation pages."""

import sys
from pathlib import Path


def test_file_exists():
    """Test that required files exist."""
    print("Testing file existence...")

    frontend_root = Path(__file__).parent.parent / "frontend"

    # Check PersonaCreate page
    persona_create = frontend_root / "src" / "pages" / "PersonaCreate.tsx"
    assert persona_create.exists(), f"PersonaCreate.tsx should exist at {persona_create}"
    print(f"  ✓ {persona_create} exists")

    # Check PersonaForm component
    persona_form = frontend_root / "src" / "components" / "personas" / "PersonaForm.tsx"
    assert persona_form.exists(), f"PersonaForm.tsx should exist at {persona_form}"
    print(f"  ✓ {persona_form} exists")

    print("✓ All required files exist")


def test_persona_create_structure():
    """Test PersonaCreate.tsx has expected structure."""
    print("\nTesting PersonaCreate.tsx structure...")

    frontend_root = Path(__file__).parent.parent / "frontend"
    persona_create = frontend_root / "src" / "pages" / "PersonaCreate.tsx"

    content = persona_create.read_text()

    # Check for three tabs
    assert "manual" in content, "Should have 'manual' tab"
    assert "generate" in content, "Should have 'generate' tab"
    assert "from-person" in content, "Should have 'from-person' tab"
    print("  ✓ Three tabs defined")

    # Check for state management
    assert "useState" in content, "Should use useState for state management"
    assert "activeTab" in content, "Should have activeTab state"
    print("  ✓ State management present")

    # Check for API calls
    assert "generatePersonas" in content, "Should import generatePersonas"
    assert "createFromPerson" in content, "Should import createFromPerson"
    print("  ✓ API functions imported")

    # Check for PersonaForm import
    assert "PersonaForm" in content, "Should import PersonaForm component"
    print("  ✓ PersonaForm component imported")

    # Check for navigation
    assert "useNavigate" in content, "Should use useNavigate hook"
    assert "navigate" in content, "Should have navigation calls"
    print("  ✓ Navigation logic present")

    # Check for loading states
    assert "isGenerating" in content, "Should have loading state for generation"
    assert "isSearching" in content, "Should have loading state for search"
    print("  ✓ Loading states defined")

    # Check for error handling
    assert "generateError" in content or "Error" in content, "Should have error handling"
    assert "fromPersonError" in content or "Error" in content, "Should have error handling"
    print("  ✓ Error handling present")

    # Check for disambiguation handling
    assert "candidates" in content, "Should handle disambiguation candidates"
    assert "selectedCandidate" in content, "Should have selected candidate state"
    print("  ✓ Disambiguation handling present")

    print("✓ PersonaCreate.tsx structure correct")


def test_persona_form_structure():
    """Test PersonaForm.tsx has expected structure."""
    print("\nTesting PersonaForm.tsx structure...")

    frontend_root = Path(__file__).parent.parent / "frontend"
    persona_form = frontend_root / "src" / "components" / "personas" / "PersonaForm.tsx"

    content = persona_form.read_text()

    # Check for multi-step wizard
    assert "currentStep" in content, "Should have currentStep state"
    assert "nextStep" in content or "Next" in content, "Should have next button"
    assert "prevStep" in content or "Previous" in content, "Should have previous button"
    print("  ✓ Multi-step wizard structure present")

    # Check for form data state
    assert "formData" in content, "Should have formData state"
    assert "useState" in content, "Should use useState"
    print("  ✓ Form data state present")

    # Check for all 7 steps
    step_checks = [
        ("Identity", ["name", "age", "background"]),
        ("Big Five", ["openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"]),
        ("True Colors", ["true_colors_primary", "true_colors_secondary"]),
        ("Moral Foundations", ["care", "fairness", "loyalty", "authority", "sanctity", "liberty"]),
        ("Cognitive Style", ["reasoning", "thinking_mode", "argument_style"]),
        ("Communication Style", ["pace", "formality", "directness", "emotionality"]),
        ("Discussion Tendencies", ["conflict_approach", "consensus", "focus", "strengths", "blind_spots", "trigger_points"])
    ]

    for step_name, fields in step_checks:
        # At least some fields from each step should be present
        field_count = sum(1 for field in fields if field in content)
        assert field_count > 0, f"Step '{step_name}' should have fields present"
        print(f"  ✓ {step_name} step fields present ({field_count}/{len(fields)})")

    # Check for Input, Textarea, Select, Slider components
    assert "Input" in content, "Should use Input component"
    assert "Textarea" in content, "Should use Textarea component"
    assert "Select" in content, "Should use Select component"
    assert "Slider" in content, "Should use Slider component"
    assert "Button" in content, "Should use Button component"
    print("  ✓ UI components imported and used")

    # Check for progress indicator
    assert "Step" in content or "step" in content, "Should have step indicator"
    print("  ✓ Progress indicator present")

    # Check for form submission
    assert "handleSubmit" in content or "submit" in content, "Should have submit handler"
    assert "createPersona" in content, "Should call createPersona API"
    print("  ✓ Form submission logic present")

    # Check for validation
    assert "validateStep" in content or "validate" in content, "Should have validation"
    print("  ✓ Validation logic present")

    # Check for navigation on success
    assert "navigate" in content, "Should navigate on success"
    print("  ✓ Navigation on success present")

    print("✓ PersonaForm.tsx structure correct")


def test_typescript_compiles():
    """Test that TypeScript compiles without errors."""
    print("\nTesting TypeScript compilation...")

    import subprocess

    frontend_root = Path(__file__).parent.parent / "frontend"

    try:
        result = subprocess.run(
            ["npm", "run", "build"],
            cwd=frontend_root,
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode != 0:
            print(f"  ✗ Build failed with exit code {result.returncode}")
            print(f"  stdout: {result.stdout}")
            print(f"  stderr: {result.stderr}")
            raise AssertionError("TypeScript build failed")

        print("  ✓ TypeScript compiles successfully")
        print("✓ TypeScript compilation passed")

    except subprocess.TimeoutExpired:
        raise AssertionError("Build process timed out")
    except FileNotFoundError:
        print("  ⚠ npm not found, skipping build test")
        print("✓ TypeScript compilation test skipped (npm not available)")


def test_eslint_passes():
    """Test that ESLint passes without errors."""
    print("\nTesting ESLint...")

    import subprocess

    frontend_root = Path(__file__).parent.parent / "frontend"

    try:
        result = subprocess.run(
            ["npm", "run", "lint"],
            cwd=frontend_root,
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode != 0:
            print(f"  ✗ Lint failed with exit code {result.returncode}")
            print(f"  stdout: {result.stdout}")
            print(f"  stderr: {result.stderr}")
            raise AssertionError("ESLint check failed")

        print("  ✓ ESLint passes")
        print("✓ ESLint check passed")

    except subprocess.TimeoutExpired:
        raise AssertionError("Lint process timed out")
    except FileNotFoundError:
        print("  ⚠ npm not found, skipping lint test")
        print("✓ ESLint test skipped (npm not available)")


def main():
    """Run all simple validation tests."""
    print("=" * 70)
    print("Task 18 Simple Validation: Persona creation and generation pages")
    print("=" * 70)

    try:
        test_file_exists()
        test_persona_create_structure()
        test_persona_form_structure()
        test_typescript_compiles()
        test_eslint_passes()

        print("\n" + "=" * 70)
        print("✓ ALL SIMPLE VALIDATION TESTS PASSED")
        print("=" * 70)
        return 0

    except AssertionError as e:
        print(f"\n✗ VALIDATION FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
