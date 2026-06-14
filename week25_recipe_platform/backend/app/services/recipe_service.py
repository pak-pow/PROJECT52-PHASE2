import os 

class ValidationError(Exception): pass

def validate_recipe_data(data: dict) -> dict: # type: ignore
    
    # makes sure that the incoming payload has all the required fields
    required_fields = [
        'title',
        'description',
        'ingredients',
        'instructions'
        ]
    
    for field in required_fields:
        if field not in data or not str(data[field]).strip():
            raise ValidationError(f"{field} is required and cannot be empty")
        
    return {
        'title': data['title'].strip(),
        'description': data['description'].strip(),
        'ingredients': data['ingredients'].strip(),
        'instruction': data['instruction'].strip()
    }
    
def allowed_file(filename: str, allowed_extensions: str) -> bool: #type:ignore
    pass
    