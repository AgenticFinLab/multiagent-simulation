"""Command-line entrypoint for the current benchmark-simulation pipeline."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from h2epr.backends.registry import BackendRegistryError
from h2epr.benchmark.compiler import compile_event_package
from h2epr.benchmark.compiler import SemanticPackageCompileError
from h2epr.benchmark.package import EventPackageError, load_event_package
from h2epr.canonical import write_json
from h2epr.conformance import ConformanceError, build_identity_invariance_receipt
from h2epr.experiment import (
    ExperimentAdmissionError,
    load_and_admit_experiment_plan,
)
from h2epr.publication import (
    PublicationError,
    publish_cross_event_release,
    publish_rule_run_release,
)
from h2epr.repository import (
    CurrentEventRegistryError,
    load_current_event_registry,
)
from h2epr.runtime.benchmark_runner import BenchmarkRunError, materialize_run
from h2epr.runtime.environment import DeclarativeEnvironmentError
from h2epr.runtime.generated_epg import GeneratedEPGError
from h2epr.semantic.assets import AssetAdmissionError


PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXPECTED_FAILURES = (
    AssetAdmissionError,
    BackendRegistryError,
    BenchmarkRunError,
    ConformanceError,
    CurrentEventRegistryError,
    DeclarativeEnvironmentError,
    EventPackageError,
    ExperimentAdmissionError,
    GeneratedEPGError,
    PublicationError,
    SemanticPackageCompileError,
    FileExistsError,
)


def _print(value: object, *, stream: object | None = None) -> None:
    print(
        json.dumps(value, ensure_ascii=False, sort_keys=True),
        file=sys.stdout if stream is None else stream,
    )


def _build(args: argparse.Namespace) -> None:
    manifest = compile_event_package(
        project_root=PROJECT_ROOT,
        data_root=Path(args.data_root),
        assembly_path=Path(args.assembly),
        output_root=Path(args.output),
    )
    _print(manifest)


def _validate(args: argparse.Namespace) -> None:
    package = load_event_package(
        Path(args.package), Path(args.data_root), args.backend
    )
    _print(
        {
            "event_id": package.manifest["event_id"],
            "package_id": package.manifest["package_id"],
            "package_sha256": package.package_sha256,
            "manifest_sha256": package.manifest["manifest_sha256"],
            "binding_sha256": package.binding_sha256,
            "backend": args.backend,
            "status": "pass",
        }
    )


def _materialize(args: argparse.Namespace) -> None:
    receipt = materialize_run(
        package_root=Path(args.package),
        data_root=Path(args.data_root),
        output_root=Path(args.output),
        backend=args.backend,
        run_seed=args.seed,
        identity_variant=args.identity_variant,
        custody_locator=args.custody_locator,
    )
    _print(receipt)


def _identity(args: argparse.Namespace) -> None:
    receipt = build_identity_invariance_receipt(
        Path(args.canonical), Path(args.probe)
    )
    if args.output:
        write_json(Path(args.output), receipt)
    _print(receipt)


def _admit_experiment(args: argparse.Namespace) -> None:
    receipt = load_and_admit_experiment_plan(
        project_root=PROJECT_ROOT,
        data_root=Path(args.data_root),
        plan_path=Path(args.plan),
    )
    if args.output:
        write_json(Path(args.output), receipt)
    _print(receipt)


def _publish_run(args: argparse.Namespace) -> None:
    summary = publish_rule_run_release(
        package_root=Path(args.package),
        data_root=Path(args.data_root),
        canonical_root=Path(args.canonical),
        repeat_root=Path(args.repeat),
        probe_root=Path(args.probe),
        release_root=Path(args.release),
        event_title=args.title,
        simulation_reading_link=args.simulation_reading_link,
    )
    _print(summary)


def _publish_cross_event(args: argparse.Namespace) -> None:
    summary = publish_cross_event_release(
        cases=[(Path(package), Path(canonical)) for package, canonical in args.case],
        data_root=Path(args.data_root),
        release_root=Path(args.release),
        event_release_links=args.event_release_link,
    )
    _print(summary)


def _validate_registry(args: argparse.Namespace) -> None:
    project_root = Path(args.project_root)
    registry_path = Path(args.registry) if args.registry else None
    registry = load_current_event_registry(project_root, registry_path)
    _print(
        {
            "event_count": len(registry["events"]),
            "event_ids": [row["event_id"] for row in registry["events"]],
            "registry_id": registry["registry_id"],
            "registry_sha256": registry["registry_sha256"],
            "status": "pass",
        }
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m h2epr.cli",
        description=(
            "Compile, validate, materialize, and independently publish the "
            "current H2EPR benchmark-simulation contract."
        ),
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    registry = subparsers.add_parser(
        "validate-registry",
        help="validate the declarative current-event registry and its paths",
    )
    registry.add_argument("--project-root", default=str(PROJECT_ROOT))
    registry.add_argument("--registry")
    registry.set_defaults(handler=_validate_registry)

    build = subparsers.add_parser(
        "build-package",
        help="compile an admitted assembly into an absent package root",
    )
    build.add_argument("--data-root", required=True)
    build.add_argument("--assembly", required=True)
    build.add_argument("--output", required=True)
    build.set_defaults(handler=_build)

    validate = subparsers.add_parser(
        "validate-package",
        help="independently load and validate one attached backend package",
    )
    validate.add_argument("--data-root", required=True)
    validate.add_argument("--package", required=True)
    validate.add_argument("--backend", default="rule")
    validate.set_defaults(handler=_validate)

    materialize = subparsers.add_parser(
        "materialize",
        help="run one admitted package into a fresh raw-custody root",
    )
    materialize.add_argument("--data-root", required=True)
    materialize.add_argument("--package", required=True)
    materialize.add_argument("--output", required=True)
    materialize.add_argument("--backend", default="rule")
    materialize.add_argument("--seed", type=int, default=0)
    materialize.add_argument("--identity-variant", default="canonical")
    materialize.add_argument("--custody-locator")
    materialize.set_defaults(handler=_materialize)

    identity = subparsers.add_parser(
        "identity-conformance",
        help="compare canonical and opaque-ID materializations semantically",
    )
    identity.add_argument("--canonical", required=True)
    identity.add_argument("--probe", required=True)
    identity.add_argument("--output")
    identity.set_defaults(handler=_identity)

    experiment = subparsers.add_parser(
        "admit-experiment",
        help="admit a comparison plan without launching its rows",
    )
    experiment.add_argument("--data-root", required=True)
    experiment.add_argument("--plan", required=True)
    experiment.add_argument("--output")
    experiment.set_defaults(handler=_admit_experiment)

    publish = subparsers.add_parser(
        "publish-run-release",
        help="reverify three Rule custody roots and publish a compact release",
    )
    publish.add_argument("--data-root", required=True)
    publish.add_argument("--package", required=True)
    publish.add_argument("--canonical", required=True)
    publish.add_argument("--repeat", required=True)
    publish.add_argument("--probe", required=True)
    publish.add_argument("--release", required=True)
    publish.add_argument("--title", required=True)
    publish.add_argument("--simulation-reading-link", required=True)
    publish.set_defaults(handler=_publish_run)

    cross_event = subparsers.add_parser(
        "publish-cross-event-release",
        help="verify at least two current event releases on one Rule contract",
    )
    cross_event.add_argument("--data-root", required=True)
    cross_event.add_argument(
        "--case",
        action="append",
        nargs=2,
        metavar=("PACKAGE", "CANONICAL"),
        required=True,
    )
    cross_event.add_argument(
        "--event-release-link",
        action="append",
        required=True,
    )
    cross_event.add_argument("--release", required=True)
    cross_event.set_defaults(handler=_publish_cross_event)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run one command and return a process exit status.

    Expected contract failures are one-line JSON on stderr. Unexpected
    programming defects retain their traceback instead of being mislabeled as
    an admission result.
    """

    args = _parser().parse_args(argv)
    try:
        args.handler(args)
    except EXPECTED_FAILURES as exc:
        _print(
            {
                "command": args.command,
                "error_code": str(exc) or exc.__class__.__name__,
                "error_type": exc.__class__.__name__,
                "status": "fail",
            },
            stream=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
