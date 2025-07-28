import sys
import os
import csv
import shutil
from pathlib import Path

def test_batch_latam_analysis():
    """
    Batch analysis of LATAM case decision texts through the full pipeline.
    Outputs a CSV file with columns:
      filename, jurisdiction, col_section, theme, abstract,
      relevant_facts, pil_provisions, col_issue, courts_position
    """
    # Ensure streamlit and agent root on sys.path for imports
    STREAMLIT_DIR = Path(__file__).parent.parent
    if str(STREAMLIT_DIR) not in sys.path:
        sys.path.insert(0, str(STREAMLIT_DIR))
    AGENT_ROOT = STREAMLIT_DIR.parent  # cold_case_analyzer_agent
    if str(AGENT_ROOT) not in sys.path:
        sys.path.insert(0, str(AGENT_ROOT))

    # Import analysis steps
    from tools.jurisdiction_detector import detect_jurisdiction
    from tools.col_extractor import extract_col_section
    from tools.themes_classifier import theme_classification_node
    from tools.case_analyzer import (
        abstract, relevant_facts, pil_provisions, col_issue, courts_position
    )

    # 0. Download PDFs and convert to text for Argentina cases
    from latam_case_analysis.pdf_extractor import fetch_records, download_attachment
    from latam_case_analysis.txt_converter import get_dirs, convert_pdf_to_txt
    # prepare directories
    pdf_dir, txt_dir = get_dirs()
    shutil.rmtree(pdf_dir, ignore_errors=True)
    shutil.rmtree(txt_dir, ignore_errors=True)
    os.makedirs(pdf_dir, exist_ok=True)
    os.makedirs(txt_dir, exist_ok=True)
    # fetch and download only Argentina records
    record_map = {}
    offset = None
    while True:
        recs, offset = fetch_records(offset)
        for rec in recs:
            juris = rec.get('fields', {}).get('Jurisdictions') or []
            if isinstance(juris, str): juris = [juris]
            if 'Argentina' in juris:
                for att in rec.get('fields', {}).get('Official Source (PDF)', []) or []:
                    download_attachment(rec['id'], att)
                record_map[rec['id']] = juris
        if not offset:
            break
    # convert PDFs to text
    for fname in os.listdir(pdf_dir):
        if not fname.lower().endswith('.pdf'):
            continue
        src = os.path.join(pdf_dir, fname)
        dst = os.path.join(txt_dir, os.path.splitext(fname)[0] + '.txt')
        convert_pdf_to_txt(src, dst)
    # locate generated text files
    txts_dir = Path(txt_dir)
    txt_files = list(txts_dir.glob('*.txt'))
    assert txt_files, f"No text files found in {txts_dir}"

    # Prepare output CSV
    output_csv = STREAMLIT_DIR / 'latam_analysis_results.csv'
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            'record_id', 'airtable_jurisdiction', 'llm_jurisdiction', 'full_text',
            'col_section', 'theme', 'abstract', 'relevant_facts',
            'pil_provisions', 'col_issue', "court's_position"
        ])

        # Process each text file
        for txt_path in txt_files:
            # identify record and jurisdictions
            rec_id = txt_path.stem.split('_')[0]
            airtable_juris = record_map.get(rec_id, [])
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
                rec_id,
                ','.join(airtable_juris),
                state.get('jurisdiction'),
                text,
                state.get('col_section', [''])[-1],
                state.get('classification', [''])[-1],
                state.get('abstract', [''])[-1],
                state.get('relevant_facts', [''])[-1],
                state.get('pil_provisions', [[]])[-1],
                state.get('col_issue', [''])[-1],
                state.get('courts_position', [''])[-1]
            ]
            writer.writerow(row)

    # Ensure CSV was written
    assert output_csv.exists(), f"Output CSV file was not created at {output_csv}"

if __name__ == "__main__":
    test_batch_latam_analysis()
    print("Batch LATAM analysis test completed successfully.")