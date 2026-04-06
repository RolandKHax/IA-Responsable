"""Test script for input filtering"""

from app.utils.security import filter_user_input, detect_pii_patterns, detect_sensitive_keywords

# Test cases
test_cases = [
    # PII - Emails
    {
        "input": "My email is john.doe@example.com, can you help?",
        "description": "Email address detection",
        "should_pass": False
    },
    # PII - Moroccan phone
    {
        "input": "My phone is 0612345678, please call me",
        "description": "Moroccan phone detection",
        "should_pass": False
    },
    # PII - International phone
    {
        "input": "Contact me at +33123456789",
        "description": "International phone detection",
        "should_pass": False
    },
    # PII - CIN
    {
        "input": "My CIN is AB123456",
        "description": "CIN (identity card) detection",
        "should_pass": False
    },
    # PII - Credit card
    {
        "input": "Use card 1234-5678-9012-3456",
        "description": "Credit card detection",
        "should_pass": False
    },
    # Sensitive keywords - Health
    {
        "input": "I have a medical diagnostic and I need treatment",
        "description": "Medical/health keywords",
        "should_pass": False
    },
    # Sensitive keywords - Religion
    {
        "input": "My religion is important to me in politics",
        "description": "Religion/politics keywords",
        "should_pass": False
    },
    # Sensitive keywords - Financial
    {
        "input": "What's my salary and how much debt do I have?",
        "description": "Financial keywords",
        "should_pass": False
    },
    # Sensitive keywords - Confidential
    {
        "input": "Can you help me with my password reset?",
        "description": "Password/confidential keyword",
        "should_pass": False
    },
    # Legitimate content
    {
        "input": "Can you explain machine learning concepts?",
        "description": "Legitimate educational question",
        "should_pass": True
    },
    # Legitimate content
    {
        "input": "What is the capital of France?",
        "description": "Legitimate geography question",
        "should_pass": True
    },
]

print("=" * 80)
print("INPUT FILTERING TEST SUITE")
print("=" * 80)

passed = 0
failed = 0

for i, test in enumerate(test_cases, 1):
    is_safe, error_msg, details = filter_user_input(test["input"])
    
    # Check if result matches expectation
    test_passed = is_safe == test["should_pass"]
    
    if test_passed:
        passed += 1
        status = "✓ PASS"
    else:
        failed += 1
        status = "✗ FAIL"
    
    print(f"\nTest {i}: {test['description']}")
    print(f"Status: {status}")
    print(f"Input: {test['input'][:60]}...")
    print(f"Safe: {is_safe} (expected: {test['should_pass']})")
    if not is_safe and details:
        print(f"Details: {', '.join(details[:2])}")

print("\n" + "=" * 80)
print(f"RESULTS: {passed} passed, {failed} failed out of {len(test_cases)} tests")
print("=" * 80)
