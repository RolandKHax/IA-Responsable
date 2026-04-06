"""Test with French keywords"""

from app.utils.security import filter_user_input

# Test with French keywords for financial data
test = "Quel est mon salaire et combien de dette j'ai?"

is_safe, error_msg, details = filter_user_input(test)

print("Testing French financial keywords:")
print(f"Input: {test}")
print(f"Safe: {is_safe}")
print(f"Error Message: {error_msg}")
print(f"Details: {details}")
