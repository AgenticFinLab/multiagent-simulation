"""Command-line entrypoint for the current benchmark-simulation pipeline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from h2epr.benchmark.compiler import compile_event_package
from h2epr.benchmark.package import load_event_package
from h2epr.canonical import write_json
from h2epr.conformance import build_identity_invariance_receipt
from h2epr.experiment import load_and_admit_experiment_plan
from h2epr.publication import (
    publish_cross_event_release,
    publish_rule_run_release,
)
from h2epr.runtime.benchmark_runner import materialize_run


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _build(args: argparse.Namespace) -> None:
    manifest = compile_event_package(
        project_root=PROJECT_ROOT,
        data_root=Path(args.data_root),
        assembly_path=Path(args.assembly),
        output_root=Path(args.output),
    )
    print(json.dumps(manifest, ensure_ascii=False, sort_keys=True))


def _validate(args: argparse.Namespace) -> None:
    package = load_event_package(
        Path(args.package), Path(args.data_root), args.backend
    )
    print(
        json.dumps(
            {
                "event_id": package.manifest["event_id"],
                "package_id": package.manifest["package_id"],
                "package_sha256": package.package_sha256,
                "manifest_sha256": package.manifest["manifest_sha256"],
                "binding_sha256": package.binding_sha256,
                "backend": args.backend,
                "status": "pass",
            },
            ensure_ascii=False,
            sort_keys=True,
        )
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
    print(json.dumps(receipt, ensure_ascii=False, sort_keys=True))


def _identity(args: argparse.Namespace) -> None:
    receipt = build_identity_invariance_receipt(
        Path(args.canonical), Path(args.probe)
    )
    if args.output:
        write_json(Path(args.output), receipt)
    print(json.dumps(receipt, ensure_ascii=False, sort_keys=True))


def _admit_experiment(args: argparse.Namespace) -> None:
    receipt = load_and_admit_experiment_plan(
        project_root=PROJECT_ROOT,
        data_root=Path(args.data_root),
        plan_path=Path(args.plan),
    )
    if args.output:
        write_json(Path(args.output), receipt)
    print(json.dumps(receipt, ensure_ascii=False, sort_keys=True))


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
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))


def _publish_cross_event(args: argparse.Namespace) -> None:
    summary = publish_cross_event_release(
        cases=[(Path(package), Path(canonical)) for package, canonical in args.case],
        data_root=Path(args.data_root),
        release_root=Path(args.release),
        event_release_links=args.event_release_link,
    )
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m h2epr.cli")
    subparsers = parser.add_subparsers(dest="command", required=True)

    build = subparsers.add_parser("build-package")
    build.add_argument("--data-root", required=True)
    build.add_argument("--assembly", required=True)
    build.add_argument("--output", required=True)
    build.set_defaults(handler=_build)

    validate = subparsers.add_parser("validate-package")
    validate.add_argument("--data-root", required=True)
    validate.add_argument("--package", required=True)
    validate.add_argument("--backend", default="rule")
    validate.set_defaults(handler=_validate)

    materialize = subparsers.add_parser("materialize")
    materialize.add_argument("--data-root", required=True)
    materialize.add_argument("--package", required=True)
    materialize.add_argument("--output", required=True)
    materialize.add_argument("--backend", default="rule")
    materialize.add_argument("--seed", type=int, default=0)
    materialize.add_argument("--identity-variant", default="canonical")
    materialize.add_argument("--custody-locator")
    materialize.set_defaults(handler=_materialize)

    identity = subparsers.add_parser("identity-conformance")
    identity.add_argument("--canonical", required=True)
    identity.add_argument("--probe", required=True)
    identity.add_argument("--output")
    identity.set_defaults(handler=_identity)

    experiment = subparsers.add_parser("admit-experiment")
    experiment.add_argument("--data-root", required=True)
    experiment.add_argument("--plan", required=True)
    experiment.add_argument("--output")
    experiment.set_defaults(handler=_admit_experiment)

    publish = subparsers.add_parser("publish-run-release")
    publish.add_argument("--data-root", required=True)
    publish.add_argument("--package", required=True)
    publish.add_argument("--canonical", required=True)
    publish.add_argument("--repeat", required=True)
    publish.add_argument("--probe", required=True)
    publish.add_argument("--release", required=True)
    publish.add_argument("--title", required=True)
    publish.add_argument("--simulation-reading-link", required=True)
    publish.set_defaults(handler=_publish_run)

    cross_event = subparsers.add_parser("publish-cross-event-release")
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


def main() -> None:
    args = _parser().parse_args()
    args.handler(args)


if __name__ == "__main__":
    main()
