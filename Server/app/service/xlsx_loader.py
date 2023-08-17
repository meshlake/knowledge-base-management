from __future__ import annotations
from typing import List, Tuple
from unstructured.documents.elements import Element, ElementMetadata, Table
import pandas as pd
from pandas.core.frame import DataFrame
from pandas import Series
import lxml.html
from pathlib import Path
import logging


class UnstructuredRow:
    def __init__(
        self,
        data: List[Tuple[str | int, str]] = None,
        tags: dict[str, List[str]] = None,
    ) -> None:
        self.data: List[Tuple[str | int, str]] = data or []
        self.tags: dict[str, List[str]] = tags or {}

    def __str__(self) -> str:
        return "\n".join(
            [str(content) for _, content in self.data if content is not None]
        )

    @classmethod
    def from_pandas(
        cls,
        data: Series,
        tag_headers: List[str] = [],
    ) -> UnstructuredRow:
        cells: List[Tuple[str | int, str]] = []
        tags: dict[str, List[str]] = {}
        for name, value in data.items():
            if name in tag_headers:
                tags[name] = [value] if not pd.isna(value) else []
            else:
                cells.append((name, value if not pd.isna(value) else None))
        return cls(data=cells, tags=tags)


class UnstructuredTable(Table):
    def __init__(self, data: List[UnstructuredRow] = None, **kwargs):
        self.data = data or []
        super().__init__(self.__textify__(), **kwargs)

    def __textify__(self) -> str:
        """Converts the table to a string for abstract class <unstructured.documents.elements.Table>."""
        return "\n".join([str(row) for row in self.data])

    @classmethod
    def from_pandas(
        cls, data: DataFrame, tag_headers: List[str] = None, **kwargs
    ) -> UnstructuredTable:
        """Converts a pandas DataFrame to an UnstructuredTable."""
        rows: List[UnstructuredRow] = []
        for _, row in data.iterrows():
            rows.append(UnstructuredRow.from_pandas(row, tag_headers=tag_headers))

        metadata = kwargs.pop("metadata", None)
        if metadata is None:
            metadata = ElementMetadata(
                filename=kwargs.pop("filename", None),
                file_directory=kwargs.pop("file_directory", None),
                page_name=kwargs.pop(
                    "page_name", data.Name if hasattr(data, "Name") else None
                ),
                page_number=kwargs.pop("page_number", None),
            )
        return cls(data=rows, metadata=metadata, **kwargs)

    def __repr__(self) -> str:
        return f"UnstructuredTable({self.id}, {self.metadata.page_name})"

    def __str__(self) -> str:
        return self.__textify__()

def is_first_row_header(
    df: DataFrame,
    headers:  List[str] = []
) -> bool: 
    headers = [h for h in headers if not pd.isna(h)]
    if len(headers) == 0: 
        return False
    row: Series = df.iloc[0]
    header_candidates = set(row.values)
    for header in headers: 
        if header not in header_candidates: 
            return False
    return True

def xlsx_loader(
    file_path: str,
    tag_headers: List[str] = ["分类", "标签"],
    header_row_auto_detected: bool = True,
    header_row_included: bool = False,
    revision: int = 0, # 0: deprecated (reserved for existing logic), 1: new
) -> List[Element | UnstructuredTable]:
    if revision == 0:
        return deprecated_loader(file_path)

    result: List[UnstructuredTable] = []
    path = Path(file_path)
    data: dict[int | str, DataFrame] = pd.read_excel(
        file_path,
        sheet_name=None,
        header=None,
        keep_default_na=False
    )

    page_number = 1
    for sheet_name, df in data.items():
        df = trim_and_drop_na(df)
        if df.shape[0] == 0:
            page_number += 1
            continue
        _setup_header(df, tag_headers, header_row_auto_detected, header_row_included)
        table = UnstructuredTable.from_pandas(
            df,
            tag_headers=tag_headers or [],
            filename=path.name,
            file_directory=path.parent.as_posix() if path.parent != "" else None,
            page_name=sheet_name,
            page_number=page_number,
        )
        result.append(table)
        page_number += 1
    return result

def _setup_header(
    data: DataFrame,
    headers: List[str], 
    header_row_auto_detected: bool, 
    header_row_included: bool, 
) -> None:
    if (not header_row_included) and (not (header_row_auto_detected and is_first_row_header(data, headers))): 
        return
    data.columns = Series(
        name=data.iloc[0].name, 
        dtype=data.iloc[0].dtype, 
        data=[col if not pd.isna(col) else f"Unamed: {i}" for i, col in enumerate(data.iloc[0])]
    )
    data.drop(data.index[0], inplace=True)
    logging.info(f"Header row has been set: [{', '.join(data.columns.values)}]")

def trim_and_drop_na(df: DataFrame):
    df = (
            df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
                .applymap(lambda x: x if (isinstance(x, str) and x != "") else pd.NA)
        )
    df.dropna(axis=0, how="all", inplace=True)
    df.dropna(axis=1, how="all", inplace=True)
    return df

def csv_loader(
    file_path: str,
    tag_headers: List[str] = ["分类", "标签"],
    header_row_auto_detected: bool = True,
    header_row_included: bool = False,
    revision: int = 0,
) -> List[Element | UnstructuredTable]:
    if revision == 0:
        return deprecated_loader(file_path)

    path = Path(file_path)
    data: DataFrame = pd.read_csv(
        file_path,
        header=None,
        keep_default_na=False
    )
    data = trim_and_drop_na(data)
    if data.shape[0] > 0:
        _setup_header(data, tag_headers, header_row_auto_detected, header_row_included)
    table = UnstructuredTable.from_pandas(
        data,
        tag_headers=tag_headers or [],
        filename=path.name,
        file_directory=path.parent.as_posix() if path.parent != "" else None,
        page_name=None,
        page_number=None,
    )
    return [table]


def deprecated_loader(file_path):
    elements: List[Element] = []
    sheets: dict[int | str, DataFrame] = pd.read_excel(file_path, sheet_name=None)
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

import typer

app = typer.Typer()


@app.command()
def main(
    file_path: str = typer.Argument(..., help="File path to the xlsx file"),
):
    elements: List[UnstructuredTable] = []

    if file_path.endswith(".xlsx"): 
        elements = xlsx_loader(
            file_path,
            revision=1, 
            tag_headers=["项目"]
        )
    elif file_path.endswith(".csv"): 
        elements = csv_loader(
            file_path, 
            revision=1,
            tag_headers=["Access key ID"]
        )
    print(f"Total tables: {len(elements)}")
    for table in elements:
        print(f"Table: {table.id}, {len(table.data)} rows")

if __name__ == "__main__":
    app()
