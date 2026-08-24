import re
from jinja2 import Template, Environment, meta, StrictUndefined

class TemplateEngine:
    """
    Template Rendering Engine for Email, SMS, and Webhook content.
    Supports Jinja2 variable replacement {{ variable_name }} with safety fallbacks.
    """

    @staticmethod
    def render(template_str: str, variables: dict = None) -> str:
        if not template_str:
            return ""

        if not variables:
            variables = {}

        try:
            # Use Jinja2 Template rendering
            env = Environment()
            template = env.from_string(template_str)
            return template.render(**variables)
        except Exception:
            # Fallback simple string format replacement
            result = template_str
            for key, val in variables.items():
                pattern = r"\{\{\s*" + re.escape(key) + r"\s*\}\}"
                result = re.sub(pattern, str(val), result)
            return result

    @staticmethod
    def extract_variables(template_str: str) -> list[str]:
        if not template_str:
            return []
        try:
            env = Environment()
            parsed_content = env.parse(template_str)
            return list(meta.find_undeclared_variables(parsed_content))
        except Exception:
            # Regex fallback
            return re.findall(r"\{\{\s*([a-zA-Z0-9_]+)\s*\}\}", template_str)
