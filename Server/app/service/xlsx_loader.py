from __future__ import annotations
from typing import List, Tuple
from unstructured.documents.elements import Element, ElementMetadata, Table
import pandas as pd
from pandas.core.frame import DataFrame
from pandas import Series
import lxml.html
from pathlib import Path


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


def xlsx_loader(
    file_path: str,
    header_row_included: bool = True,
    tag_headers: List[str] = ["分类", "标签"],
    revision: int = 0,
) -> List[Element | UnstructuredTable]:
    if revision == 0:
        return deprecated_loader(file_path)

    result: List[UnstructuredTable] = []
    path = Path(file_path)
    data: dict[int | str, DataFrame] = pd.read_excel(
        file_path,
        sheet_name=None,
        header=0 if header_row_included else None,
    )

    page_number = 1
    for sheet_name, df in data.items():
        df.dropna(axis=0, how="all", inplace=True)
        df.dropna(axis=1, how="all", inplace=True)
        table = UnstructuredTable.from_pandas(
            df,
            tag_headers=tag_headers or [],
            filename=path.name,
            file_directory=path.parent.as_posix() if path.parent != "" else None,
            page_name=sheet_name,
            page_number=page_number,
        )
        result.append(table)
    return result


def csv_loader(
    file_path: str,
    header_row_included: bool = True,
    tag_headers: List[str] = ["分类", "标签"],
    revision: int = 0,
) -> List[Element | UnstructuredTable]:
    if revision == 0:
        return deprecated_loader(file_path)

    path = Path(file_path)
    data: dict[int | str, DataFrame] = pd.read_csv(
        file_path,
        header=0 if header_row_included else None,
    )

    data.dropna(axis=0, how="all", inplace=True)
    data.dropna(axis=1, how="all", inplace=True)
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


def xlsx_to_list(file_path: str):
    df = pd.read_excel(file_path, engine="openpyxl")
    # 将dataframe转化为二维列表
    data = df.values.tolist()
    return data

import typer

app = typer.Typer()


@app.command()
def main(
    file_path: str = typer.Argument(..., help="File path to the xlsx file"),
):
    elements: List[UnstructuredTable] = xlsx_loader(
        file_path,
        revision=1,
        header_row_included=True,
    )
    for element in elements:
        print(element.data[0])


if __name__ == "__main__":
    app()
