#!/usr/bin/env python3
"""
Validate contribution YAML files against the expected schema.

Usage:
    python tools/validate.py contributions/your-name.yaml
    python tools/validate.py contributions/    # validate all
"""

import sys
import os
import yaml
from pathlib import Path

REQUIRED_FIELDS = [
    "contributor_name",
    "contributor_type",
    "industry",
    "domain",
    "role_description",
]

RECOMMENDED_FIELDS = [
    "systems_touched",
    "metrics",
    "top_failure_modes",
    "data_quality_estimate",
    "automation_gaps",
    "would_use",
    "could_build",
]

VALID_CONTRIBUTOR_TYPES = ["agent", "human"]


def validate_file(filepath):
    """Validate a single contribution YAML file. Returns (errors, warnings)."""
    errors = []
    warnings = []

    try:
        with open(filepath, "r") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        return [f"Invalid YAML: {e}"], []
    except Exception as e:
        return [f"Cannot read file: {e}"], []

    if data is None:
        return ["File is empty"], []

    if not isinstance(data, dict):
        return ["Top-level structure must be a mapping (key: value pairs)"], []

    # Check required fields
    for field in REQUIRED_FIELDS:
        val = data.get(field)
        if val is None or (isinstance(val, str) and val.strip() == ""):
            errors.append(f"Missing required field: {field}")

    # Check contributor_type
    ct = data.get("contributor_type", "")
    if ct and ct not in VALID_CONTRIBUTOR_TYPES:
        errors.append(
            f"contributor_type must be 'agent' or 'human', got: '{ct}'"
        )

    # Check recommended fields
    for field in RECOMMENDED_FIELDS:
        val = data.get(field)
        if val is None:
            warnings.append(f"Missing recommended field: {field}")
        elif isinstance(val, list) and all(
            (isinstance(item, str) and item.strip() == "") or item is None
            for item in val
        ):
            warnings.append(f"Recommended field is empty: {field}")
        elif isinstance(val, dict) and not val:
            warnings.append(f"Recommended field is empty: {field}")

    # Check failure modes have substance
    failure_modes = data.get("top_failure_modes", [])
    if isinstance(failure_modes, list):
        filled = [
            fm
            for fm in failure_modes
            if isinstance(fm, dict)
            and fm.get("description", "").strip() != ""
        ]
        if len(filled) == 0:
            warnings.append(
                "No failure modes described — this is the most valuable section"
            )
        elif len(filled) < 2:
            warnings.append("Only 1 failure mode — most operations have at least 2-3")

    # Check metrics have substance
    metrics = data.get("metrics", {})
    if isinstance(metrics, dict):
        filled_metrics = {
            k: v for k, v in metrics.items() if v and str(v).strip() != ""
        }
        if len(filled_metrics) == 0:
            warnings.append("No metrics provided — what do you actually measure?")

    # Check for template placeholder text
    for key, val in data.items():
        if isinstance(val, str) and val.startswith("e.g.,"):
            warnings.append(
                f"Field '{key}' looks like placeholder text: '{val[:50]}'"
            )

    return errors, warnings


def main():
    if len(sys.argv) < 2:
        print("Usage: python tools/validate.py <file_or_directory>")
        print("  python tools/validate.py contributions/your-name.yaml")
        print("  python tools/validate.py contributions/")
        sys.exit(1)

    target = Path(sys.argv[1])
    files = []

    if target.is_dir():
        files = sorted(target.glob("*.yaml"))
        files = [f for f in files if f.name != "template.yaml"]
    elif target.is_file():
        files = [target]
    else:
        print(f"Error: {target} not found")
        sys.exit(1)

    if not files:
        print("No contribution files found to validate.")
        sys.exit(0)

    total_errors = 0
    total_warnings = 0

    for filepath in files:
        print(f"\n{'='*60}")
        print(f"Validating: {filepath.name}")
        print(f"{'='*60}")

        errors, warnings = validate_file(filepath)
        total_errors += len(errors)
        total_warnings += len(warnings)

        if errors:
            for e in errors:
                print(f"  ❌ ERROR: {e}")
        if warnings:
            for w in warnings:
                print(f"  ⚠️  WARN:  {w}")
        if not errors and not warnings:
            print(f"  ✅ All checks passed")
        elif not errors:
            print(f"  ✅ Required fields OK ({len(warnings)} warnings)")

    print(f"\n{'='*60}")
    print(f"Summary: {len(files)} file(s), {total_errors} error(s), {total_warnings} warning(s)")

    if total_errors > 0:
        print("FAIL — fix errors before submitting PR")
        sys.exit(1)
    else:
        print("PASS")
        sys.exit(0)


if __name__ == "__main__":
    main()
