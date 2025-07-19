import sys
import os
import csv
from pathlib import Path

def test_batch_latam_analysis():
    """
    Batch analysis of LATAM case decision texts through the full pipeline.
    Outputs a CSV file with columns:
      filename, jurisdiction, col_section, theme, abstract,
      relevant_facts, pil_provisions, col_issue, courts_position
    """
    # Ensure streamlit directory on path to import tools
    STREAMLIT_DIR = Path(__file__).parent.parent
    if str(STREAMLIT_DIR) not in sys.path:
        sys.path.insert(0, str(STREAMLIT_DIR))

    # Import analysis steps
    from tools.jurisdiction_detector import detect_jurisdiction
    from tools.col_extractor import extract_col_section
    from tools.themes_classifier import theme_classification_node
    from tools.case_analyzer import (
        abstract, relevant_facts, pil_provisions, col_issue, courts_position
    )

    # Locate LATAM text inputs
    base_dir = STREAMLIT_DIR.parent  # cold_case_analyzer_agent
    txts_dir = base_dir / 'latam_case_analysis' / 'txts'
    txt_files = list(txts_dir.glob('*.txt'))
    assert txt_files, f"No text files found in {txts_dir}"

    # Prepare output CSV
    output_csv = STREAMLIT_DIR / 'latam_analysis_results.csv'
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            'filename', 'jurisdiction', 'col_section', 'theme', 'abstract',
            'relevant_facts', 'pil_provisions', 'col_issue', "court's_position"
        ])

        # Process each text file
        for txt_path in txt_files:
            text = txt_path.read_text(encoding='utf-8')
            state = {'full_text': text}

            # 1. Jurisdiction detection
            jurisdiction = detect_jurisdiction(text)
            state['jurisdiction'] = jurisdiction

            # 2. Choice of Law section extraction
            res_col = extract_col_section(state)
            state.update(res_col)

            # 3. Theme classification
            res_theme = theme_classification_node(state)
            state.update(res_theme)

            # 4. Abstract extraction
            res_abs = abstract(state)
            state.update(res_abs)

            # 5. Relevant facts extraction
            res_facts = relevant_facts(state)
            state.update(res_facts)

            # 6. PIL provisions extraction
            res_pil = pil_provisions(state)
            state.update(res_pil)

            # 7. Choice of Law issue identification
            res_issue = col_issue(state)
            state.update(res_issue)

            # 8. Court's position summarization
            res_pos = courts_position(state)
            state.update(res_pos)

            # Gather latest outputs
            row = [
                txt_path.name,
                state.get('jurisdiction'),
                state.get('col_section', [''])[ -1 ],
                state.get('classification', [''])[ -1 ],
                state.get('abstract', [''])[ -1 ],
                state.get('relevant_facts', [''])[ -1 ],
                state.get('pil_provisions', [[]])[ -1 ],
                state.get('col_issue', [''])[ -1 ],
                state.get('courts_position', [''])[ -1 ]
            ]
            writer.writerow(row)

    # Ensure CSV was written
    assert output_csv.exists(), f"Output CSV file was not created at {output_csv}"

if __name__ == "__main__":
    test_batch_latam_analysis()
    print("Batch LATAM analysis test completed successfully.")