# =====================================================================
# FILE: src/teamdynamix/tools/csv_utils.py
#
# Design goals:
# - Local-only helper utilities for one-time scripts (no HTTP / no endpoints).
# - Read-focused API: load CSV -> query/search -> optionally write output CSV.
# - Requires pandas (acceptable per project requirement).
# - Optional Logger support (uses .log(message, level=?, context=?)).
#
# Key decisions:
# - Separator is controlled by a module-global default separator ord (int).
# - Callers may override per function call, OR set the global separator for the
#   duration of the script via set_separator_ord()/set_separator().
# - CsvTable is intentionally "stateless" with respect to separator; we avoid
#   storing separator state on the object.
# - Search APIs return CellMatch objects (row/column/value, plus x/y aliases).
# =====================================================================

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Union

import os
import pandas as pd


# ---------------------------------------------------------------------
# Separator defaults (module-global)
# ---------------------------------------------------------------------
# NOTE: Comma is ASCII code 44. (46 is '.' period.)
DEFAULT_SEPARATOR_ORD: int = 44

# Module-global separator state (in-memory override for the script duration)
_SEPARATOR_ORD: int = DEFAULT_SEPARATOR_ORD


def get_separator_ord() -> int:
    """Return the current module-global separator character code (ord)."""
    return int(_SEPARATOR_ORD)


def get_separator() -> str:
    """Return the current module-global separator as a string."""
    return chr(get_separator_ord())


def set_separator_ord(separator_ord: int) -> None:
    """
    Set the module-global separator ord for the duration of the script.

    Example:
      set_separator_ord(9)  # tab-delimited
    """
    global _SEPARATOR_ORD
    if not isinstance(separator_ord, int):
        raise TypeError("separator_ord must be an int.")
    if separator_ord < 0 or separator_ord > 0x10FFFF:
        raise ValueError("separator_ord must be a valid Unicode code point.")
    _SEPARATOR_ORD = int(separator_ord)


def set_separator(separator: str) -> None:
    """
    Set the module-global separator using a literal string.

    If a multi-character separator is provided, it will be accepted, but most CSV
    use cases expect a single character delimiter.
    """
    if not isinstance(separator, str) or len(separator) == 0:
        raise ValueError("separator must be a non-empty string.")
    # Store as ord of first character for compatibility with CHR-style global.
    set_separator_ord(ord(separator[0]))


def reset_separator_default() -> None:
    """Reset the module-global separator to the library default (comma)."""
    set_separator_ord(DEFAULT_SEPARATOR_ORD)


def _sep_from(
    *,
    separator_ord: Optional[int] = None,
    separator: Optional[str] = None,
) -> str:
    """
    Resolve separator string.

    Precedence:
      1) explicit separator (string)
      2) explicit separator_ord (int)
      3) module-global separator (get_separator())
    """
    if separator is not None:
        if not isinstance(separator, str) or len(separator) == 0:
            raise ValueError("separator must be a non-empty string when provided.")
        return separator
    if separator_ord is not None:
        if not isinstance(separator_ord, int):
            raise TypeError("separator_ord must be an int when provided.")
        if separator_ord < 0 or separator_ord > 0x10FFFF:
            raise ValueError("separator_ord must be a valid Unicode code point.")
        return chr(separator_ord)
    return get_separator()


def _maybe_log(logger: Any, message: str, *, level: int = 20, context: Optional[dict] = None) -> None:
    """
    Logger is optional; if provided, it must expose .log(message, level=?, context=?).
    Tools must not fail because logging failed.
    """
    if logger is None:
        return
    try:
        logger.log(message, level=level, context=context)
    except Exception:
        pass


# ---------------------------------------------------------------------
# Standard data path helpers (unopinionated)
# ---------------------------------------------------------------------
def resolve_data_path(
    relative_or_absolute: Union[str, Path],
    *,
    base_dir: Optional[Union[str, Path]] = None,
    env_var: str = "TDX_DATA_DIR",
) -> Path:
    """
    Resolve a data path in an unopinionated way.

    Rules:
      - If input is absolute -> return as Path
      - Else if base_dir provided -> base_dir / input
      - Else if env var set (default: TDX_DATA_DIR) -> $TDX_DATA_DIR / input
      - Else -> current working directory / input

    This avoids hard-coding a data folder into the library while still supporting
    standard script workflows.
    """
    p = Path(relative_or_absolute)
    if p.is_absolute():
        return p

    if base_dir is not None:
        return Path(base_dir) / p

    env_base = os.getenv(env_var)
    if env_base:
        return Path(env_base) / p

    return Path.cwd() / p


# ---------------------------------------------------------------------
# Search match object
# ---------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class CellMatch:
    """
    Represents a single matching cell in a CSV table.

    - row: 0-based row index
    - column: column name
    - value: cell value (as stored in the dataframe)

    Aliases:
    - x: column (name)
    - y: row (index)
    """
    row: int
    column: str
    value: Any

    @property
    def x(self) -> str:
        return self.column

    @property
    def y(self) -> int:
        return self.row


# ---------------------------------------------------------------------
# CSV container object
# ---------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class CsvTable:
    """
    Read-focused CSV table wrapper.

    Internally stores a pandas DataFrame (all values kept as strings by default).
    The wrapper provides convenient query/search operations for one-time scripts.

    This object is immutable (frozen); methods do not mutate the underlying data.
    """
    df: pd.DataFrame
    source_path: Optional[Path] = None

    # ---- Introspection ----
    def row_count(self) -> int:
        return int(self.df.shape[0])

    def column_count(self) -> int:
        return int(self.df.shape[1])

    def columns(self) -> List[str]:
        return [str(c) for c in self.df.columns.tolist()]
		
    # ---- Column helpers ----
    def get_column_index(self, name: str) -> int:
        """
        Return the 0-based index of a column by name.

        Raises:
          KeyError if the column does not exist.
        """
        if name not in self.df.columns:
            raise KeyError(f"Column not found: {name}")
        return int(self.df.columns.get_loc(name))

    def get_column_name(self, index: int) -> str:
        """
        Return the column name for a 0-based column index.

        Raises:
          IndexError if the index is out of range.
        """
        if index < 0 or index >= self.column_count():
            raise IndexError(f"Column index out of range: {index}")
        return str(self.df.columns[int(index)])

    # ---- Accessors ----
    def get_row(self, index: int) -> Dict[str, Any]:
        """
        Return a single row as a dict keyed by column name.
        Index is 0-based.
        """
        if index < 0 or index >= self.row_count():
            raise IndexError(f"Row index out of range: {index}")
        row = self.df.iloc[int(index)]
        return {str(k): row[k] for k in self.df.columns}

    def get_cell(self, row_index: int, column: Union[int, str]) -> Any:
        """
        Return a specific cell.
          - column can be an int index (0-based) or a column name string.
        """
        if row_index < 0 or row_index >= self.row_count():
            raise IndexError(f"Row index out of range: {row_index}")

        if isinstance(column, int):
            if column < 0 or column >= self.column_count():
                raise IndexError(f"Column index out of range: {column}")
            return self.df.iat[int(row_index), int(column)]

        if isinstance(column, str):
            if column not in self.df.columns:
                raise KeyError(f"Column not found: {column}")
            return self.df.at[self.df.index[int(row_index)], column]

        raise TypeError("column must be an int (index) or str (column name).")

    def column_values(self, column: Union[int, str]) -> List[Any]:
        """
        Return all values for a column (in row order).
        """
        if isinstance(column, int):
            if column < 0 or column >= self.column_count():
                raise IndexError(f"Column index out of range: {column}")
            col_name = self.df.columns[int(column)]
            return self.df[col_name].tolist()

        if isinstance(column, str):
            if column not in self.df.columns:
                raise KeyError(f"Column not found: {column}")
            return self.df[column].tolist()

        raise TypeError("column must be an int (index) or str (column name).")

    # ---- Searching ----
    def search_contains(
        self,
        needle: str,
        *,
        case_sensitive: bool = False,
        columns: Optional[Sequence[Union[int, str]]] = None,
    ) -> List[CellMatch]:
        """
        Substring search across the specified columns (or all columns if None).

        Returns a list of CellMatch objects, one per matching cell.

        - case_sensitive=False performs case-insensitive matching.
        - Treats NaN/None as non-matching.
        """
        if needle is None:
            raise ValueError("needle must be a string.")
        needle_s = str(needle)

        col_names = _resolve_columns(self.df, columns)
        if not col_names:
            return []

        subset = self.df[col_names].astype("string")

        results: List[CellMatch] = []
        if case_sensitive:
            mask = subset.apply(lambda s: s.str.contains(needle_s, na=False))
        else:
            mask = subset.apply(lambda s: s.str.contains(needle_s, case=False, na=False))

        # mask is a DataFrame[bool]; emit matches
        for row_idx in mask.index:
            row_mask = mask.loc[row_idx]
            if not bool(row_mask.any()):
                continue
            for col in col_names:
                if bool(row_mask[col]):
                    val = self.df.at[row_idx, col]
                    results.append(CellMatch(row=int(row_idx), column=str(col), value=val))
        return results

    def search_exact(
        self,
        value: str,
        *,
        case_sensitive: bool = False,
        columns: Optional[Sequence[Union[int, str]]] = None,
    ) -> List[CellMatch]:
        """
        Exact match search across the specified columns (or all columns if None).

        Returns a list of CellMatch objects, one per matching cell.

        - case_sensitive=False performs case-insensitive matching.
        - Treats NaN/None as non-matching.
        """
        if value is None:
            raise ValueError("value must be a string.")
        value_s = str(value)

        col_names = _resolve_columns(self.df, columns)
        if not col_names:
            return []

        subset = self.df[col_names].astype("string")

        results: List[CellMatch] = []
        if case_sensitive:
            mask = subset.apply(lambda s: s.fillna(pd.NA).eq(value_s))
        else:
            lower_val = value_s.lower()
            mask = subset.apply(lambda s: s.fillna(pd.NA).str.lower().eq(lower_val))

        for row_idx in mask.index:
            row_mask = mask.loc[row_idx]
            if not bool(row_mask.any()):
                continue
            for col in col_names:
                if bool(row_mask[col]):
                    val = self.df.at[row_idx, col]
                    results.append(CellMatch(row=int(row_idx), column=str(col), value=val))
        return results

    def search_contains_rows(
        self,
        needle: str,
        *,
        case_sensitive: bool = False,
        columns: Optional[Sequence[Union[int, str]]] = None,
    ) -> List[int]:
        """Convenience: return only distinct row indices matching a substring search."""
        matches = self.search_contains(needle, case_sensitive=case_sensitive, columns=columns)
        return sorted({m.row for m in matches})

    def search_exact_rows(
        self,
        value: str,
        *,
        case_sensitive: bool = False,
        columns: Optional[Sequence[Union[int, str]]] = None,
    ) -> List[int]:
        """Convenience: return only distinct row indices matching an exact search."""
        matches = self.search_exact(value, case_sensitive=case_sensitive, columns=columns)
        return sorted({m.row for m in matches})

    # ---- Output (non-mutating) ----
    def to_csv(
        self,
        path: Union[str, Path],
        *,
        separator_ord: Optional[int] = None,
        separator: Optional[str] = None,
        index: bool = False,
        encoding: str = "utf-8",
    ) -> Path:
        """
        Write the current table to a CSV file without modifying this object.

        Separator behavior:
          - If separator/separator_ord provided -> use it
          - Else -> use the current module-global separator (default comma unless changed)

        Returns the resolved output path.
        """
        out_path = Path(path)
        sep = _sep_from(separator_ord=separator_ord, separator=separator)
        self.df.to_csv(out_path, sep=sep, index=index, encoding=encoding)
        return out_path


def _resolve_columns(df: pd.DataFrame, columns: Optional[Sequence[Union[int, str]]]) -> List[str]:
    if columns is None:
        return [str(c) for c in df.columns.tolist()]

    resolved: List[str] = []
    for c in columns:
        if isinstance(c, int):
            if c < 0 or c >= len(df.columns):
                raise IndexError(f"Column index out of range: {c}")
            resolved.append(str(df.columns[int(c)]))
        elif isinstance(c, str):
            if c not in df.columns:
                raise KeyError(f"Column not found: {c}")
            resolved.append(c)
        else:
            raise TypeError("columns entries must be int indices or str column names.")
    return resolved


# ---------------------------------------------------------------------
# Public loader
# ---------------------------------------------------------------------
def load_csv(
    path: Union[str, Path],
    *,
    separator_ord: Optional[int] = None,
    separator: Optional[str] = None,
    encoding: str = "utf-8",
    keep_default_na: bool = False,
    logger: Any = None,
) -> CsvTable:
    """
    Load a CSV file into a CsvTable.

    - Uses pandas.read_csv
    - Keeps values as strings by default (dtype=str)
    - Separator is controlled by either:
        separator_ord (character code) or separator (string)
      If neither provided, uses the module-global separator (default comma).

    Parameters
    ----------
    path:
      File path (relative or absolute).
    separator_ord:
      Integer character code for separator (e.g., 44 for comma, 9 for tab).
    separator:
      Literal separator string override (takes precedence over separator_ord).
    encoding:
      File encoding (default utf-8).
    keep_default_na:
      If False, pandas will not automatically convert certain strings to NaN.
      This tends to be friendlier for scripting and string-based matching.
    logger:
      Optional SDK Logger-like object.

    Returns
    -------
    CsvTable
    """
    p = Path(path)
    sep = _sep_from(separator_ord=separator_ord, separator=separator)

    _maybe_log(logger, "csv_utils.load_csv", context={"path": str(p), "sep_ord": ord(sep)})

    df = pd.read_csv(
        p,
        sep=sep,
        encoding=encoding,
        dtype=str,  # keep everything as strings (script-friendly)
        keep_default_na=keep_default_na,
    )

    return CsvTable(df=df, source_path=p)
