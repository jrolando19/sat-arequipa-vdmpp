"""Execute VDMJ independently and preserve complete output plus source hashes.

This runner does not edit the model. Runtime checks remain enabled: do not add
-pre, -post, -inv or -dtc (those VDMJ switches disable checks).
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess
import sys

HERE = Path(__file__).resolve().parent
MODEL = HERE.parent / "model"
DEFAULT_JAVA = Path("java")
DEFAULT_JAR = MODEL / "tools/vdmj-suite-4.7.0/vdmj-4.7.0.jar"
SOURCES = [MODEL / f"{name}.vdmpp" for name in
           ("TiposSAT", "Sensor", "Quebrada", "Alarma", "Sistema")]
AUDIT = HERE / "AuditSAT.vdmpp"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def execute(name, expression, expected, java, jar, extra_source=AUDIT):
    command = [str(java), "-jar", str(jar), "-vdmpp", "-c", "UTF-8",
               "-e", expression, *map(str, SOURCES), str(extra_source)]
    hashes = {p.name: digest(p) for p in [*SOURCES, extra_source]}
    result = subprocess.run(command, capture_output=True, text=True,
                            encoding="utf-8", errors="replace", timeout=120)
    combined = result.stdout + result.stderr
    if expected == "true_map":
        observed_true = re.findall(r'"(A\d\d_[^"\n]+)"\s*\|->\s*true', combined)
        observed_false = re.findall(r'"(A\d\d_[^"\n]+)"\s*\|->\s*false', combined)
        passed = result.returncode == 0 and len(observed_true) == 24 and not observed_false
    else:
        observed_true, observed_false = [], []
        passed = result.returncode != 0 and re.search(expected, combined) is not None
    return {
        "name": name, "expression": expression, "expected": expected,
        "command": command, "exit_code": result.returncode, "pass": passed,
        "source_sha256": hashes, "checks_disabled": [],
        "observed_true": observed_true, "observed_false": observed_false,
        "output": combined,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_folder", nargs="?", default="execution_reproduced",
                        help="Output folder, relative to review/ unless absolute")
    parser.add_argument("--java", type=Path, default=DEFAULT_JAVA,
                        help="Path to the Java executable (Java 18.0.1 used for original evidence)")
    parser.add_argument("--jar", type=Path, default=DEFAULT_JAR,
                        help="Path to VDMJ jar (4.7.0 used for original evidence)")
    parser.add_argument("--include-boundary-diagnostic", action="store_true",
                        help="Also reproduce known mutable-token-payload limitation, separately")
    args = parser.parse_args()
    output_folder = HERE / args.output_folder
    output_folder.mkdir(parents=True, exist_ok=True)
    cases = [("positive_suite", "AuditSAT`Ejecutar()", "true_map")]
    results = []
    for name, expression, expected in cases:
        record = execute(name, expression, expected, args.java, args.jar)
        (output_folder / f"{name}.log").write_text(record.pop("output"), encoding="utf-8")
        results.append(record)
    summary = {
        "purpose": "Independent bounded scenario validation, not exhaustive formal proof",
        "java_version_expected": "18.0.1", "vdmj_version_expected": "4.7.0",
        "jar_sha256": digest(args.jar), "results": results,
        "all_passed": all(r["pass"] for r in results),
    }
    if args.include_boundary_diagnostic:
        diagnostic = execute("known_mutable_token_payload", "TokenBoundaryAudit`Ejecutar()",
                             r"Error 4061: No such key value in map", args.java, args.jar,
                             HERE / "TokenBoundaryAudit.vdmpp")
        (output_folder / "token_boundary_diagnostic.log").write_text(
            diagnostic.pop("output"), encoding="utf-8")
        diagnostic["interpretation"] = (
            "Expected reproduction of a known interpreter boundary limitation; "
            "not one of the 24 positive model checks. Incoming token identities "
            "must be stable and built from immutable/materialized payload values.")
        (output_folder / "token_boundary_diagnostic.json").write_text(
            json.dumps(diagnostic, ensure_ascii=False, indent=2), encoding="utf-8")
        summary["separate_known_diagnostic_reproduced"] = diagnostic["pass"]
    (output_folder / "audit_results.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"folder": str(output_folder), "all_passed": summary["all_passed"],
                      "checks": [{"name": r["name"], "exit": r["exit_code"],
                                  "pass": r["pass"],
                                  "true": len(r["observed_true"]),
                                  "false": r["observed_false"]} for r in results]}, indent=2))


if __name__ == "__main__":
    main()
