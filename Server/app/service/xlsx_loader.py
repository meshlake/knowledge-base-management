from typing import List
from unstructured.documents.elements import Element, ElementMetadata, Table
import pandas as pd
import lxml.html


def xlsx_loader(file_path: str):
    elements: List[Element] = []
    sheets = pd.read_excel(file_path, sheet_name=None)
    page_number = 0   
    for sheet_name, table in sheets.items():
        page_number += 1
        html_text = table.to_html(index=False, header=False, na_rep="")
        text = lxml.html.document_fromstring(html_text).text_content()
        metadata_filename = file_path or metadata_filename
        metadata = ElementMetadata(
            text_as_html=html_text,
            page_name=sheet_name,
            page_number=page_number,
            filename=metadata_filename,
        )
        table = Table(text=text, metadata=metadata)
        elements.append(table)
    return elements
