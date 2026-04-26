"""Property-based tests for prompt templates."""

import pytest
from hypothesis import given, settings, strategies as st

from app.adapters.prompts import (
    InputSanitizer,
    PromptInjectionDetected,
    PromptTemplate,
)


# ============================================================================
# Property 11: Prompt Template Input Validation
# ============================================================================


@given(
    injection_pattern=st.sampled_from(
        [
            "<|im_start|>",
            "<|im_end|>",
            "### System:",
            "### Assistant:",
            "Human:",
            "AI:",
            "[INST]",
            "[/INST]",
            "<s>",
            "</s>",
        ]
    )
)
@settings(max_examples=100, deadline=None)
def test_property_11_prompt_injection_detection(injection_pattern):
    """
    Feature: llm-langgraph-integration, Property 11: Prompt Template Input Validation
    For any input containing injection patterns, validator rejects it.

    Validates: Requirements 9.5
    """
    # Create input with injection pattern
    malicious_input = f"Normal text {injection_pattern} more text"

    # Should raise PromptInjectionDetected
    with pytest.raises(PromptInjectionDetected):
        InputSanitizer.sanitize(malicious_input)


@given(
    safe_text=st.text(
        alphabet=st.characters(
            blacklist_categories=("Cs",), blacklist_characters="<>[]|"
        ),
        min_size=1,
        max_size=100,
    )
)
@settings(max_examples=100, deadline=None)
def test_property_11_safe_input_accepted(safe_text):
    """
    Feature: llm-langgraph-integration, Property 11: Prompt Template Input Validation
    For any safe input without injection patterns, validator accepts it.

    Validates: Requirements 9.5
    """
    # Filter out any text that might accidentally contain injection patterns
    injection_keywords = [
        "im_start",
        "im_end",
        "System:",
        "Assistant:",
        "Human:",
        "AI:",
        "INST",
    ]

    if any(keyword in safe_text for keyword in injection_keywords):
        # Skip this example
        return

    # Should not raise exception
    try:
        sanitized = InputSanitizer.sanitize(safe_text)
        assert isinstance(sanitized, str)
    except PromptInjectionDetected:
        pytest.fail(f"Safe text rejected: {safe_text}")


# ============================================================================
# Property 12: Template Version Tracking
# ============================================================================


@given(
    template_id=st.text(
        alphabet=st.characters(whitelist_categories=("Ll", "Nd"), min_codepoint=97),
        min_size=5,
        max_size=20,
    ),
    version=st.text(
        alphabet=st.characters(whitelist_categories=("Nd",), min_codepoint=48),
        min_size=5,
        max_size=10,
    ).map(lambda v: f"{v[0]}.{v[1]}.{v[2:]}"),
)
@settings(max_examples=50, deadline=None)
def test_property_12_template_version_tracking(template_id, version):
    """
    Feature: llm-langgraph-integration, Property 12: Template Version Tracking
    For any template rendering, version metadata is preserved.

    Validates: Requirements 9.4, 9.7
    """
    # Create template
    template = PromptTemplate(
        template_id=template_id,
        version=version,
        agent_name="Test Agent",
        system_prompt="System prompt",
        user_prompt_template="User prompt with {{variable}}",
        few_shot_examples=[],
    )

    # Render template
    rendered = template.render({"variable": "test value"})

    # Version should be tracked
    assert rendered.template_id == template_id
    assert rendered.template_version == version


# ============================================================================
# Helper: Test template variable extraction
# ============================================================================


@given(
    num_variables=st.integers(min_value=1, max_value=5),
    var_names=st.lists(
        st.text(
            alphabet=st.characters(whitelist_categories=("Ll",), min_codepoint=97),
            min_size=3,
            max_size=10,
        ),
        min_size=1,
        max_size=5,
        unique=True,
    ),
)
@settings(max_examples=50, deadline=None)
def test_template_variable_extraction(num_variables, var_names):
    """Test that template correctly extracts variable names."""
    # Take only the number of variables we need
    var_names = var_names[:num_variables]

    # Create template with variables
    template_str = " ".join([f"{{{{{var}}}}}" for var in var_names])

    template = PromptTemplate(
        template_id="test",
        version="1.0.0",
        agent_name="Test",
        system_prompt="System",
        user_prompt_template=template_str,
        few_shot_examples=[],
    )

    # Extract variables
    extracted = template._extract_template_variables(template_str)

    # Should extract all variables
    assert set(extracted) == set(var_names)
