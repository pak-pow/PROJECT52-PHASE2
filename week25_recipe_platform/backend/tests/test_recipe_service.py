import pytest #type:ignore
from app.services.recipe_service import validate_recipe_data, allowed_file, ValidationError

# --- TEXT VALIDATION TESTS ---

def test_valid_recipe_data_passes():
    """Ensure a perfect payload passes validation and is cleaned."""
    payload = {
        'title': '  Spicy Chicken   ',
        'description': 'A nice dinner.',
        'ingredients': 'Chicken, Spice',
        'instructions': 'Cook it.'
    }
    
    cleaned_data = validate_recipe_data(payload)    
    assert cleaned_data['title'] == 'Spicy Chicken'

def test_missing_field_raises_error():
    """Ensure omitting a required field triggers a ValidationError."""
    payload = {
        'title': 'Spicy Chicken',
        'description': 'A nice dinner.',
    }
    
    with pytest.raises(ValidationError) as excinfo:
        validate_recipe_data(payload)
        
    assert "'ingredients' is required" in str(excinfo.value)

def test_empty_string_raises_error():
    """Ensure sending blank strings triggers a ValidationError."""
    payload = {
        'title': 'Spicy Chicken',
        'description': 'A nice dinner.',
        'ingredients': '   ',
        'instructions': 'Cook it.'
    }
    
    with pytest.raises(ValidationError) as excinfo:
        validate_recipe_data(payload)
        
    assert "'ingredients' is required" in str(excinfo.value) 

# --- FILE EXTENSION TESTS ---

def test_allowed_file_valid_extensions():
    """Ensure whitelisted image extensions pass."""
    whitelist = {'png', 'jpg', 'jpeg', 'webp'}
    assert allowed_file('my_burger.jpg', whitelist) == True # type: ignore
    assert allowed_file('fancy_salad.PNG', whitelist) == True # type: ignore

def test_allowed_file_invalid_extensions():
    """Ensure dangerous or unsupported extensions fail."""
    whitelist = {'png', 'jpg', 'jpeg', 'webp'}
    assert allowed_file('malicious_script.py', whitelist) == False # type: ignore
    assert allowed_file('document.pdf', whitelist) == False # type: ignore
    assert allowed_file('no_extension', whitelist) == False # type: ignore