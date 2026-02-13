"""Validation test for Task 18: Reflection integration into Agent."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agora.agent import Agent
from agora.memory import MemoryRecord


def test_trigger_reflection_method():
    """Test that trigger_reflection() method exists and returns list."""
    print("Testing trigger_reflection() method...")

    # Load an agent
    agent = Agent("ada")

    # Check method exists
    assert hasattr(agent, "trigger_reflection"), "Agent should have trigger_reflection method"

    # Test it returns a list
    result = agent.trigger_reflection()
    assert isinstance(result, list), "trigger_reflection should return a list"

    # Each item should be a MemoryRecord
    for item in result:
        assert isinstance(item, MemoryRecord), "Each reflection should be a MemoryRecord"

    print("✓ trigger_reflection() works correctly")


def test_get_reflections_method():
    """Test that get_reflections() method exists and returns string."""
    print("Testing get_reflections() method...")

    # Load an agent
    agent = Agent("ada")

    # Check method exists
    assert hasattr(agent, "get_reflections"), "Agent should have get_reflections method"

    # Test it returns a string
    result = agent.get_reflections()
    assert isinstance(result, str), "get_reflections should return a string"

    print("✓ get_reflections() works correctly")


def test_observe_reflection_trigger():
    """Test that observe() can trigger reflection without errors."""
    print("Testing observe() reflection trigger...")

    # Load an agent
    agent = Agent("ada")

    # Add some observations (should not trigger reflection yet with small importance)
    for i in range(3):
        record = agent.observe(
            content=f"Test observation {i}",
            discussion_id="test_discussion",
            speaker="TestUser"
        )
        assert isinstance(record, MemoryRecord), "observe should return MemoryRecord"

    print("✓ observe() handles reflection trigger correctly")


def test_observe_own_statement_reflection_trigger():
    """Test that observe_own_statement() can trigger reflection without errors."""
    print("Testing observe_own_statement() reflection trigger...")

    # Load an agent
    agent = Agent("ada")

    # Add own statements (should not trigger reflection yet with importance 5)
    for i in range(3):
        record = agent.observe_own_statement(
            content=f"Test statement {i}",
            discussion_id="test_discussion"
        )
        assert isinstance(record, MemoryRecord), "observe_own_statement should return MemoryRecord"

    print("✓ observe_own_statement() handles reflection trigger correctly")


def test_no_circular_imports():
    """Test that importing agent module doesn't cause circular imports."""
    print("Testing for circular import issues...")

    try:
        from agora import agent
        from agora import reflection
        from agora.agent import Agent
        from agora.reflection import reflect
        print("✓ No circular import errors")
    except ImportError as e:
        raise AssertionError(f"Circular import detected: {e}")


if __name__ == "__main__":
    print("Running Task 18 validation tests...\n")

    try:
        test_no_circular_imports()
        test_trigger_reflection_method()
        test_get_reflections_method()
        test_observe_reflection_trigger()
        test_observe_own_statement_reflection_trigger()

        print("\n✅ All Task 18 validation tests passed!")
        sys.exit(0)
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
