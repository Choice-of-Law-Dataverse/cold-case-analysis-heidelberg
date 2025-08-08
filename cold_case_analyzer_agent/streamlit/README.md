# CoLD Case Analyzer in Streamlit

## Structure

`App.py` is a minimal orchestration script that handles: page config, authentication initialization, model selection, CSS/sidebar loading, and main workflow rendering.

The core workflow logic is distributed across the following components:

### Components (`components/`)

#### `auth.py`
- Authentication and model selection functionality
- Functions: `initialize_auth()`, `render_model_selector()`

#### `database.py`  
- Database persistence functionality
- Functions: `save_to_db()`

#### `input_handler.py`
- Input handling for case citation, PDF upload, text input, demo case
- Functions: `render_case_citation_input()`, `render_pdf_uploader()`, `render_text_input()`, `render_demo_button()`, `render_input_phase()`

#### `col_processor.py`
- Choice of Law section processing and feedback
- Functions: `display_jurisdiction_info()`, `display_case_info()`, `display_col_extractions()`, `handle_first_extraction_scoring()`, `handle_col_feedback_phase()`, `render_col_processing()`

#### `theme_classifier.py`
- Theme classification and editing interface
- Functions: `display_theme_classification()`, `handle_theme_scoring()`, `handle_theme_editing()`, `display_final_themes()`, `render_theme_classification()`

#### `analysis_workflow.py`
- Analysis workflow execution and management
- Functions: `display_analysis_history()`, `display_completion_message()`, `get_analysis_steps()`, `execute_analysis_step()`, `handle_step_scoring()`, `handle_step_editing()`, `process_current_analysis_step()`, `render_analysis_workflow()`

#### `main_workflow.py`
- Main workflow orchestration
- Functions: `render_initial_input_phase()`, `render_processing_phases()`, `render_main_workflow()`

Utilities are further specified under:

### Utilities (`utils/`)

#### `state_manager.py`
- Session state management utilities
- Functions: `initialize_col_state()`, `create_initial_analysis_state()`, `update_col_state()`, `get_col_state()`, `load_demo_case()`

#### `data_loaders.py`
- Data loading utilities (themes, demo case)
- Functions: `load_valid_themes()`, `get_demo_case_text()`

## Usage Examples

### Adding a New Phase
```python
# Create components/new_phase.py
def render_new_phase(state):
    # Your phase logic here
    pass

# Add to components/main_workflow.py
from components.new_phase import render_new_phase

def render_processing_phases():
    # ... existing phases
    render_new_phase(col_state)
```

### Modifying Input Handling
```python
# All input-related changes go in components/input_handler.py
def render_new_input_type():
    # New input widget logic
    pass
```

### Testing Individual Components
```python
# Test components in isolation
from components.theme_classifier import handle_theme_scoring

def test_theme_scoring():
    mock_state = {"theme_first_score_submitted": False}
    result = handle_theme_scoring(mock_state)
    assert result == False
```