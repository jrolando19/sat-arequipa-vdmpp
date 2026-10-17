"""Verify final execution evidence without changing the model or its tests."""
from pathlib import Path
import collections
import hashlib
import json
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
MODEL = ROOT / "model"
EVIDENCE = ROOT / "evidence"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    primary = json.loads((EVIDENCE / "results.json").read_text(encoding="utf-8-sig"))
    audit = json.loads((HERE / "execution_final/audit_results.json").read_text(encoding="utf-8-sig"))
    verified_cases = []
    for case in primary["results"]:
        log_file = EVIDENCE / case["log"]
        log = log_file.read_text(encoding="utf-8-sig")
        if case["kind"] == "behaviour":
            okay = case["exit_code"] == 0 and bool(re.search(r"(?m)^true\s*$", log))
        else:
            expected_code = "4079" if case["id"] == "N09" else "4071"
            okay = case["exit_code"] == 1 and f"Error {expected_code}:" in log
            okay = okay and case["observed"] in log
        verified_cases.append({"id": case["id"], "kind": case["kind"],
                               "log": f"evidence/{case['log']}", "verified": okay,
                               "log_sha256": sha(log_file)})
    agreement = []
    audit_hashes = audit["results"][0]["source_sha256"]
    for entry in primary["source_hashes"]:
        current = sha(MODEL / entry["file"])
        primary_agrees = current.lower() == entry["Hash"].lower()
        audit_agrees = entry["file"] == "TestSAT.vdmpp" or current == audit_hashes[entry["file"]]
        agreement.append({"file": entry["file"], "current_sha256": current,
                          "primary_agrees": primary_agrees, "audit_agrees": audit_agrees})
    coverage_text = (EVIDENCE / "coverage_execution.log").read_text(encoding="utf-8-sig")
    coverage = []
    current = None
    for line in coverage_text.splitlines():
        header = re.search(r"Test coverage for .*[/\\]([^/\\]+\.vdmpp):$", line)
        if header:
            current = {"file": header[1], "hit_lines": 0, "miss_lines": 0}
            coverage.append(current)
        elif current is not None and line.startswith("+"):
            current["hit_lines"] += 1
        elif current is not None and line.startswith("-"):
            current["miss_lines"] += 1
        elif current is not None and line.startswith("Coverage = "):
            current["native_percent"] = float(line.split("=")[1].strip().rstrip("%"))
            total = current["hit_lines"] + current["miss_lines"]
            current["total_executable_lines"] = total
            current["calculated_truncated_percent"] = (1000 * current["hit_lines"] // total) / 10
            current["native_agrees"] = current["native_percent"] == current["calculated_truncated_percent"]
            current = None
    proof_text = (EVIDENCE / "proof_obligations.log").read_text(encoding="utf-8-sig")
    statuses = collections.Counter(re.findall(r"Proof Obligation \d+: \(([^)]+)\)", proof_text))
    final = {
        "scope": "Independent review of frozen v2.0.0 sequential abstract VDM++ model",
        "primary_cases": {"behavioural": 40, "expected_contract_rejections": 9,
                           "verified_logs": sum(c["verified"] for c in verified_cases),
                           "total": len(verified_cases), "cases": verified_cases},
        "independent_checks": {"count": len(audit["results"][0]["observed_true"]),
                               "keys": audit["results"][0]["observed_true"],
                               "all_true": audit["all_passed"],
                               "log": "review/execution_final/positive_suite.log",
                               "details": "review/execution_final/audit_results.json"},
        "source_agreement": agreement,
        "coverage": {"metric": "Native VDMJ executable SOURCE LINES, not expressions/branches/states",
                     "cases": "40 behavioural cases only; negative cases excluded",
                     "warning": ".cov default export omits unhit locations; do not use row count as denominator",
                     "log": "evidence/coverage_execution.log", "files": coverage},
        "proof_obligations": {"total": sum(statuses.values()), "statuses": dict(statuses),
                              "discharged_by_this_project": 0,
                              "log": "evidence/proof_obligations.log"},
        "separate_known_boundary_diagnostic": {
            "included_in_24_positive_checks": False,
            "log": "review/execution_final/token_boundary_diagnostic.log",
            "details": "review/execution_final/token_boundary_diagnostic.json",
            "required_assumption": "Incoming token identities are stable and built from immutable/materialized values",
        },
        "limits": ["Synthetic data; no field or geotechnical validation",
                   "No real communication or authenticated physical receipt",
                   "No distributed concurrency, restart persistence or workload benchmark",
                   "Additive inventory; no sensor retirement/relocation",
                   "Manual retries; fixed incidence threshold three, no scheduler",
                   "Finite tests and undischarged proof obligations are not universal correctness"],
    }
    final["verified_for_reported_scope"] = (
        len(verified_cases) == 49 and all(c["verified"] for c in verified_cases)
        and audit["all_passed"] and len(audit["results"][0]["observed_true"]) == 24
        and all(c["primary_agrees"] and c["audit_agrees"] for c in agreement)
        and len(coverage) == 6 and all(c["native_agrees"] for c in coverage))
    output = HERE / "final_review_summary.json"
    output.write_text(json.dumps(final, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"path": str(output),
                      "verified_for_reported_scope": final["verified_for_reported_scope"],
                      "primary_verified": final["primary_cases"]["verified_logs"],
                      "independent_true": final["independent_checks"]["count"],
                      "proof_statuses": final["proof_obligations"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
