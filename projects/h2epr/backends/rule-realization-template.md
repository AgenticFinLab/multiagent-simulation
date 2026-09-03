# Rule realization template

Record the exact semantic parents, actor coverage, deterministic policy
implementation, selected backend configuration, source hashes, and policy
version.

For each actor and decision situation, specify observation consumers,
precedence, thresholds or ordered categories, selected intent, parameters,
message behavior, pending-result handling, and justified no-op cases. Exact
values belong to the Rule backend configuration.

Test every permitted intent, required failure branch, generated-ID invariance,
and at least one perturbation per material condition. Permute reducer input and
opaque IDs for every concurrent-write case; Rule selection and environment
admission must remain unchanged. Two same-input runs must be byte-identical
before release.
