# H2EPR-0551 event package

This directory is the compiled, backend-neutral benchmark package plus its
explicitly attached backend bindings. `manifest.json` is the machine authority
for package identity, component hashes, backend availability, source exposure,
and claim limits.

Rule is attached through the registered backend factory. LLM and RuleLLM remain
planned and fail closed. Backend attachment changes the manifest identity but
cannot change `package_sha256`, which seals the shared event semantics.

`SHA256SUMS` is the exact directory inventory. A schema, parent, path, content,
provenance, implementation, or inventory mismatch rejects admission. The
package supports dataset-conditioned engineering and method verification only;
it establishes no historical fit, calibration, held-out result, causal claim,
scientific validity, or universal generality.
