# External Full Resource Pack

The complete resource-pack is intentionally not tracked in normal Git because
it contains full logs, analysis figures, and raw runtime directories for 180
samples.

## GitHub Release

Release tag:

```text
simulation-results-v1
```

Release URL:

```text
https://github.com/AgenticFinLab/multiagent-simulation/releases/tag/simulation-results-v1
```

Archive asset:

```text
simulation-180-standardized-resource-pack.tar.zst
```

Archive SHA256:

```text
327a4c55d5e03ad338b5009f7a380b8ba7e12fa522ae07f7502d6ab47b5c05a7
```

Archive size at packaging time:

```text
256642382 bytes
```

Do not commit the `.tar.zst` archive to normal Git history.

## Verification

After downloading:

```bash
sha256sum -c simulation-180-standardized-resource-pack.tar.zst.sha256
tar --zstd -xf simulation-180-standardized-resource-pack.tar.zst
python simulation-results/scripts/verify_full_resource_pack.py \
  --resource-pack resource-pack
```
