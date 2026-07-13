import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Set

from loguru import logger


def analyze_csv_schema(file_path: Path) -> Dict[str, Set[str]]:
    """
    Analyzes the structural shape and columns of a CSV file.
    
    Args:
        file_path (Path): Path to the CSV file.
        
    Returns:
        Dict[str, Set[str]]: A dictionary mapping column names to sets of their observed data types (as strings).
    """
    schema: Dict[str, Set[str]] = {}
    try:
        with file_path.open(mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames:
                for field in reader.fieldnames:
                    schema[field] = set()
            
            for row in reader:
                for key, value in row.items():
                    # For CSV, values are initially strings, but we can try to infer basic types
                    inferred_type = _infer_type(value)
                    if key in schema:
                        schema[key].add(inferred_type)
                    else:
                        schema[key] = {inferred_type}
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
    except Exception as e:
        logger.error(f"Error reading CSV {file_path}: {e}")
        
    return schema


def analyze_jsonl_schema(file_path: Path) -> Dict[str, Set[str]]:
    """
    Analyzes the structural shape and embedded key-value data types of a JSONL file.
    
    Args:
        file_path (Path): Path to the JSONL file.
        
    Returns:
        Dict[str, Set[str]]: A dictionary mapping keys to sets of their observed data types (as strings).
    """
    schema: Dict[str, Set[str]] = {}
    try:
        with file_path.open(mode="r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    if isinstance(data, dict):
                        _extract_schema_from_dict(data, schema)
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse JSON on line {line_num} in {file_path}: {e}. Skipping.")
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
    except Exception as e:
        logger.error(f"Error reading JSONL {file_path}: {e}")
  
    return schema


def _extract_schema_from_dict(data: Dict[str, Any], schema: Dict[str, Set[str]], prefix: str = "") -> None:
    """
    Recursively extracts schema information from a dictionary.
    
    Args:
        data (Dict[str, Any]): The dictionary to analyze.
        schema (Dict[str, Set[str]]): The schema dictionary to update.
        prefix (str): Prefix for nested keys.
    """
    for key, value in data.items():
        full_key = f"{prefix}{key}" if not prefix else f"{prefix}.{key}"
        value_type = type(value).__name__
        
        if full_key not in schema:
            schema[full_key] = set()
        schema[full_key].add(value_type)
        
        if isinstance(value, dict):
            _extract_schema_from_dict(value, schema, f"{full_key}")


def _infer_type(value: str) -> str:
    """
    Infers a basic Python type from a string representation.
    
    Args:
        value (str): The string value to infer.
        
    Returns:
        str: The name of the inferred type.
    """
    if not value:
        return "NoneType"
    if value.lower() in ("true", "false"):
        return "bool"
    try:
        int(value)
        return "int"
    except ValueError:
        pass
    try:
        float(value)
        return "float"
    except ValueError:
        pass
    return "str"


def format_schema_summary(name: str, schema: Dict[str, Set[str]]) -> str:
    """
    Formats a schema dictionary into a readable summary string.
    
    Args:
        name (str): Name of the dataset.
        schema (Dict[str, Set[str]]): The schema dictionary.
        
    Returns:
        str: Formatted summary.
    """
    lines: List[str] = [f"--- Schema Summary for {name} ---"]
    if not schema:
        lines.append("No schema data found.")
    else:
        for key, types in sorted(schema.items()):
            types_str = ", ".join(sorted(types))
            lines.append(f"  - {key}: [{types_str}]")
    lines.append("-" * (len(lines[0])))
    return "\n".join(lines)


def main() -> None:
    """Main execution function to analyze schemas."""
    # Define file paths
    base_dir = Path("data/output")
    telemetry_file = base_dir / "telemetry_logs.jsonl"
    employees_file = base_dir / "employees.csv"

    logger.info("Starting schema analysis...")

    # Analyze CSV
    logger.info(f"Analyzing {employees_file}...")
    csv_schema = analyze_csv_schema(employees_file)
    csv_summary = format_schema_summary("Employees CSV", csv_schema)
    logger.info(f"\n{csv_summary}")

    # Analyze JSONL
    logger.info(f"Analyzing {telemetry_file}...")
    jsonl_schema = analyze_jsonl_schema(telemetry_file)
    jsonl_summary = format_schema_summary("Telemetry JSONL", jsonl_schema)
    logger.info(f"\n{jsonl_summary}")

    logger.info("Schema analysis complete.")


if __name__ == "__main__":
    main()
