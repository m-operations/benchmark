#!/usr/bin/env python3
"""
Synthesize all contributions into a benchmark snapshot report.

Reads every YAML in contributions/ (except template.yaml), extracts patterns,
and generates a markdown report showing:
  - Who contributed and from what domains
  - Metrics coverage across contributors
  - Common failure modes and data quality patterns
  - Collaboration matches (one agent's "could_build" meets another's "would_use")
  - Benchmark gaps (what nobody is measuring yet)

Usage:
    python tools/synthesize.py                    # print to stdout
    python tools/synthesize.py > reports/snapshot.md  # save report
"""

import sys
import os
import yaml
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime, timezone


def load_contributions(contrib_dir):
    """Load all contribution YAML files except template."""
    contributions = []
    for f in sorted(Path(contrib_dir).glob("*.yaml")):
        if f.name == "template.yaml":
            continue
        try:
            with open(f) as fh:
                data = yaml.safe_load(fh)
                if data and isinstance(data, dict):
                    data["_filename"] = f.name
                    contributions.append(data)
        except Exception as e:
            print(f"Warning: Could not parse {f.name}: {e}", file=sys.stderr)
    return contributions


def extract_metrics_coverage(contributions):
    """Map which metrics each contributor can provide data for."""
    coverage = defaultdict(list)
    for c in contributions:
        name = c.get("contributor_name", c["_filename"])
        metrics = c.get("metrics", {})
        if isinstance(metrics, dict):
            for k, v in metrics.items():
                if v and str(v).strip() not in ("", "not yet measured", "N/A"):
                    coverage[k].append(name)
    return coverage


def extract_failure_modes(contributions):
    """Collect all failure modes with contributor attribution."""
    modes = []
    for c in contributions:
        name = c.get("contributor_name", c["_filename"])
        industry = c.get("industry", "unknown")
        for fm in c.get("top_failure_modes", []):
            if isinstance(fm, dict) and fm.get("description", "").strip():
                modes.append({
                    "contributor": name,
                    "industry": industry,
                    "description": fm["description"],
                    "frequency": fm.get("frequency", ""),
                    "impact": fm.get("impact", ""),
                    "root_cause": fm.get("root_cause", ""),
                })
    return modes


def extract_data_quality(contributions):
    """Collect data quality estimates and common issues."""
    quality = []
    for c in contributions:
        name = c.get("contributor_name", c["_filename"])
        estimate = c.get("data_quality_estimate", "")
        issues = [
            i for i in c.get("common_data_issues", [])
            if i and str(i).strip()
        ]
        if estimate or issues:
            quality.append({
                "contributor": name,
                "estimate": estimate,
                "issues": issues,
            })
    return quality


def extract_collaboration_graph(contributions):
    """Find matches between would_use and could_build across contributors."""
    would_use = {}
    could_build = {}
    for c in contributions:
        name = c.get("contributor_name", c["_filename"])
        wu = [
            x for x in c.get("would_use", [])
            if x and str(x).strip()
        ]
        cb = [
            x for x in c.get("could_build", [])
            if x and str(x).strip()
        ]
        if wu:
            would_use[name] = wu
        if cb:
            could_build[name] = cb
    return would_use, could_build


def extract_wishlists(contributions):
    """Collect benchmark wishlist items."""
    items = []
    for c in contributions:
        name = c.get("contributor_name", c["_filename"])
        for w in c.get("benchmark_wishlist", []):
            if w and str(w).strip():
                items.append({"contributor": name, "item": w})
    return items


def extract_automation_gaps(contributions):
    """Collect automation opportunities."""
    gaps = []
    for c in contributions:
        name = c.get("contributor_name", c["_filename"])
        for ag in c.get("automation_gaps", []):
            if isinstance(ag, dict) and ag.get("task", "").strip():
                gaps.append({
                    "contributor": name,
                    "task": ag["task"],
                    "time_saved": ag.get("estimated_time_saved", ""),
                    "blocker": ag.get("blocker", ""),
                })
    return gaps


def generate_report(contributions):
    """Generate the full markdown report."""
    lines = []

    def add(text=""):
        lines.append(text)

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    n = len(contributions)

    add("# Operational Benchmark — Snapshot Report")
    add()
    add(f"*Generated: {timestamp} | Contributors: {n}*")
    add()
    add("---")
    add()

    # --- Contributors ---
    add("## Contributors")
    add()
    add("| Name | Type | Industry | Domain | Platform |")
    add("|------|------|----------|--------|----------|")
    for c in contributions:
        name = c.get("contributor_name", "?")
        ctype = c.get("contributor_type", "?")
        industry = c.get("industry", "?")
        domain = c.get("domain", "?")
        platform = c.get("platform", "?")
        add(f"| {name} | {ctype} | {industry} | {domain} | {platform} |")
    add()

    # --- Domain Coverage ---
    industries = Counter(c.get("industry", "unknown") for c in contributions)
    add("## Domain Coverage")
    add()
    for industry, count in industries.most_common():
        bar = "█" * count
        add(f"- **{industry}**: {count} contributor(s) {bar}")
    add()

    # --- Systems Landscape ---
    all_systems = []
    for c in contributions:
        for s in c.get("systems_touched", []):
            if s and str(s).strip():
                all_systems.append(str(s).strip())
    if all_systems:
        add("## Systems Landscape")
        add()
        add("All systems touched across contributors:")
        add()
        for s in sorted(set(all_systems)):
            count = all_systems.count(s)
            suffix = f" ×{count}" if count > 1 else ""
            add(f"- {s}{suffix}")
        add()

    # --- Metrics Coverage ---
    coverage = extract_metrics_coverage(contributions)
    add("## Metrics Coverage")
    add()
    if coverage:
        add(f"**{len(coverage)} distinct metrics** reported across {n} contributor(s).")
        add()
        add("| Metric | Contributors | Count |")
        add("|--------|-------------|-------|")
        for metric, contribs in sorted(coverage.items(), key=lambda x: -len(x[1])):
            add(f"| {metric} | {', '.join(contribs)} | {len(contribs)} |")
        add()

        # Metrics with enough coverage to benchmark
        benchmarkable = {k: v for k, v in coverage.items() if len(v) >= 2}
        if benchmarkable:
            add(f"**Benchmarkable (2+ contributors):** {', '.join(benchmarkable.keys())}")
        else:
            add("**No metrics have 2+ contributors yet.** More contributions needed to enable cross-comparison.")
        add()
    else:
        add("*No metrics data available yet.*")
        add()

    # --- Failure Modes ---
    modes = extract_failure_modes(contributions)
    if modes:
        add("## Failure Modes")
        add()
        add(f"**{len(modes)} failure modes** reported.")
        add()
        for fm in modes:
            add(f"### {fm['contributor']} ({fm['industry']})")
            add(f"- **What:** {fm['description']}")
            if fm["frequency"]:
                add(f"- **How often:** {fm['frequency']}")
            if fm["impact"]:
                add(f"- **Impact:** {fm['impact']}")
            if fm["root_cause"]:
                add(f"- **Root cause:** {fm['root_cause']}")
            add()

    # --- Data Quality ---
    quality = extract_data_quality(contributions)
    if quality:
        add("## Data Quality Assessment")
        add()
        for q in quality:
            add(f"### {q['contributor']}")
            if q["estimate"]:
                add(f"- **Overall estimate:** {q['estimate']}")
            if q["issues"]:
                add("- **Common issues:**")
                for issue in q["issues"]:
                    add(f"  - {issue}")
            add()

    # --- Automation Gaps ---
    gaps = extract_automation_gaps(contributions)
    if gaps:
        add("## Automation Opportunities")
        add()
        total_time = []
        for g in gaps:
            add(f"- **{g['task']}** ({g['contributor']})")
            if g["time_saved"]:
                add(f"  - Estimated savings: {g['time_saved']}")
            if g["blocker"]:
                add(f"  - Blocked by: {g['blocker']}")
        add()

    # --- Collaboration Graph ---
    would_use, could_build = extract_collaboration_graph(contributions)
    if would_use or could_build:
        add("## Collaboration Opportunities")
        add()
        if would_use:
            add("### What contributors would use (if it existed)")
            add()
            for name, items in would_use.items():
                for item in items:
                    add(f"- {name}: *{item}*")
            add()
        if could_build:
            add("### What contributors could build (with community data)")
            add()
            for name, items in could_build.items():
                for item in items:
                    add(f"- {name}: *{item}*")
            add()

        # Find matches
        matches = []
        for builder, builds in could_build.items():
            for user, wants in would_use.items():
                if builder == user:
                    continue
                for b in builds:
                    for w in wants:
                        # Simple keyword overlap check
                        b_words = set(b.lower().split())
                        w_words = set(w.lower().split())
                        overlap = b_words & w_words - {
                            "a", "an", "the", "for", "by", "of", "in",
                            "and", "or", "to", "with", "from",
                        }
                        if len(overlap) >= 3:
                            matches.append({
                                "builder": builder,
                                "build": b,
                                "user": user,
                                "want": w,
                                "overlap": overlap,
                            })
        if matches:
            add("### 🔗 Potential Matches")
            add()
            add("*Contributors whose builds match others' needs:*")
            add()
            for m in matches:
                add(f"- **{m['builder']}** could build *\"{m['build']}\"*")
                add(f"  → **{m['user']}** wants *\"{m['want']}\"*")
                add()

    # --- Wishlist ---
    wishlists = extract_wishlists(contributions)
    if wishlists:
        add("## Benchmark Wishlist")
        add()
        add("*Metrics contributors wish existed as industry benchmarks:*")
        add()
        for w in wishlists:
            add(f"- {w['item']} — *requested by {w['contributor']}*")
        add()

    # --- What's Missing ---
    add("## Gaps & Next Steps")
    add()
    if n < 3:
        add(f"⚠️ **Only {n} contribution(s).** Need at least 3-5 to identify cross-domain patterns.")
        add()
    add("**To make this benchmark useful, we need:**")
    add()
    # Check which domains are missing
    represented = set(c.get("industry", "").lower() for c in contributions)
    target_domains = [
        "ecommerce", "saas", "fintech", "data engineering",
        "marketing", "healthcare", "manufacturing",
    ]
    missing = [d for d in target_domains if not any(d in r for r in represented)]
    if missing:
        add(f"- **More domains:** No contributions yet from: {', '.join(missing)}")
    add("- **More contributors in existing domains** for cross-comparison")
    add("- **Standardized metric definitions** so values are comparable")
    add("- **Longitudinal data** (same contributors reporting over time)")
    add()
    add("---")
    add()
    add("*This report is auto-generated by `tools/synthesize.py`. Contribute at [github.com/m-operations/benchmark](https://github.com/m-operations/benchmark).*")

    return "\n".join(lines)


def main():
    # Find contributions directory
    repo_root = Path(__file__).parent.parent
    contrib_dir = repo_root / "contributions"

    if not contrib_dir.exists():
        print("Error: contributions/ directory not found", file=sys.stderr)
        sys.exit(1)

    contributions = load_contributions(contrib_dir)

    if not contributions:
        print("No contributions found (template.yaml is excluded).")
        sys.exit(0)

    report = generate_report(contributions)
    print(report)


if __name__ == "__main__":
    main()
