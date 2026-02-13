"""Simple validation test for Task 18: Reflection integration into Agent."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_no_circular_imports():
    """Test that importing modules doesn't cause circular imports."""
    print("Testing for circular import issues...")

    try:
        from agora import agent
        from agora import reflection
        from agora.agent import Agent
        from agora.reflection import reflect
        print("✓ No circular import errors")
    except ImportError as e:
        raise AssertionError(f"Circular import detected: {e}")


def test_methods_exist():
    """Test that new methods exist on Agent class."""
    print("Testing that new methods exist...")

    from agora.agent import Agent

    # Check methods exist
    assert hasattr(Agent, "trigger_reflection"), "Agent should have trigger_reflection method"
    assert hasattr(Agent, "get_reflections"), "Agent should have get_reflections method"

    print("✓ trigger_reflection() and get_reflections() methods exist")


def test_reflection_module_edge_cases():
    """Test that reflection module has edge case handling."""
    print("Testing reflection module edge case handling...")

    from agora import reflection
    import inspect

    # Check that reflect() function exists
    assert hasattr(reflection, "reflect"), "reflection module should have reflect function"

    # Check the source code contains edge case handling
    source = inspect.getsource(reflection.reflect)
    assert "if not recent_memories" in source, "reflect() should handle empty memories"
    assert "if not evidence_memories" in source, "reflect() should handle missing evidence"

    print("✓ reflection.reflect() has edge case handling")


def test_observe_has_reflection_trigger():
    """Test that observe() methods have reflection trigger logic."""
    print("Testing observe methods have reflection trigger...")

    from agora.agent import Agent
    import inspect

    # Check observe() has reflection trigger
    observe_source = inspect.getsource(Agent.observe)
    assert "reflection.reflect" in observe_source, "observe() should call reflection.reflect"
    assert "is reflecting" in observe_source, "observe() should print reflection indicator"
    assert "_reflection_needed = False" in observe_source, "observe() should reset flag"

    # Check observe_own_statement() has reflection trigger
    own_statement_source = inspect.getsource(Agent.observe_own_statement)
    assert "reflection.reflect" in own_statement_source, "observe_own_statement() should call reflection.reflect"
    assert "is reflecting" in own_statement_source, "observe_own_statement() should print reflection indicator"
    assert "_reflection_needed = False" in own_statement_source, "observe_own_statement() should reset flag"

    print("✓ observe() and observe_own_statement() have reflection trigger logic")


if __name__ == "__main__":
    print("Running Task 18 simple validation tests...\n")

    try:
        test_no_circular_imports()
        test_methods_exist()
        test_reflection_module_edge_cases()
        test_observe_has_reflection_trigger()

        print("\n✅ All Task 18 simple validation tests passed!")
        sys.exit(0)
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
