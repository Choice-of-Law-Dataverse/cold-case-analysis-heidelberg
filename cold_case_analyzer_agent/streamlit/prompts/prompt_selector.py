import importlib

PROMPT_MODULES = {
    'civil-law': {
        'col_section': 'prompts.civil_law.col_section_prompt',
        'theme': 'prompts.civil_law.pil_theme_prompt',
        'analysis': 'prompts.civil_law.analysis_prompts',
        'jurisdiction_detection': 'prompts.civil_law.jurisdiction_detection_prompt',
    },
    'common-law': {
        'col_section': 'prompts.common_law.col_section_prompt',
        'theme': 'prompts.common_law.pil_theme_prompt',
        'analysis': 'prompts.common_law.analysis_prompts',
        'jurisdiction_detection': 'prompts.common_law.jurisdiction_detection_prompt',
    },
}

# Map user-facing jurisdiction to key
JURISDICTION_MAP = {
    'Civil-law jurisdiction': 'civil-law',
    'Common-law jurisdiction': 'common-law',
}

def get_prompt_module(jurisdiction, prompt_type):
    key = JURISDICTION_MAP.get(jurisdiction, 'civil-law')
    module_path = PROMPT_MODULES[key][prompt_type]
    return importlib.import_module(module_path)

# Usage:
# get_prompt_module(jurisdiction, 'col_section').COL_SECTION_PROMPT
# get_prompt_module(jurisdiction, 'theme').PIL_THEME_PROMPT
# get_prompt_module(jurisdiction, 'analysis').ABSTRACT_PROMPT
