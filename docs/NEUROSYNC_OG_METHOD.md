# NeuroSync-OG Method Specification

## Research contribution

NeuroSync-OG is a **geometry-constrained, contact-adaptive selective P300 decoder**. Its hypothesis is that a sparse montage should be selected and trusted only when three independent conditions agree:

1. held-out training-fold evidence supports P300 discrimination;
2. measured channel reliability remains adequate;
3. an externally generated EEG forward model indicates that target and nuisance source signatures remain distinguishable.

This converts electrode reduction from a fixed montage choice into a measurable reliability problem.

## Geometry-constrained montage objective

For candidate channel subset `S`, the implementation maximizes

```text
J(S) = BA_cv(S)
     + beta_o * O(S)
     - beta_a * A(S)
     - beta_s * SD_cv(S)
     - beta_q * (1 - Q(S))
```

where `BA_cv` is trial-fold balanced accuracy, `O` is the observability diagnostic, `A` is worst target–artifact topographic ambiguity, `SD_cv` is performance instability between folds, and `Q` is median calibration reliability. All empirical terms are calculated from training data only.

The built-in coefficient table is available for software tests and exploratory notebooks. A research result must supply a forward model exported from an anatomical BEM/FEM workflow. The loader refuses missing channels instead of silently interpolating them.

## Geometry- and quality-weighted evidence

For symbol `c` after repetition `t`, evidence is accumulated as

```text
E_c(t) = sum_r w_r * f_c(x_r)
w_r    = max(w_min, q_r^gamma_q * o_r^gamma_o)
```

where `f_c` is the classifier evidence, `q_r` is calibration-relative signal quality, and `o_r` is the forward-model observability diagnostic. Geometry regulates the reliability of evidence; it does not create class evidence. An acceptance also requires calibrated confidence, top-two margin, prediction stability, minimum quality, and minimum observability.

## Forward-model interchange

The optional NPZ file contains:

| Array | Shape | Required |
|---|---|---|
| `leadfield` | channels × sources | yes |
| `channel_names` | channels | yes |
| `source_labels` | sources | no |
| `target_indices` | target-source column indices | recommended |
| `artifact_indices` | nuisance-source column indices | recommended |
| `provenance_model` | scalar string | recommended |
| `provenance_subject` | scalar string | recommended |
| `provenance_tool` | scalar string | recommended |

Example execution:

```powershell
python scripts/run_session.py `
  --train data/train.npz `
  --test data/held_out.npz `
  --forward-model data/forward_model.npz `
  --output results/neurosync_og.json
```

## Required ablations

Every study must compare identical locked splits:

1. empirical channel selection + fixed stopping;
2. empirical selection + selective CASP;
3. geometry/contact-constrained selection without evidence weighting;
4. full NeuroSync-OG;
5. 8-channel wet reference;
6. full-montage published baseline where supported by the dataset.

Report character-level CAOR, WAOR, coverage, accepted-output accuracy, repetitions, calibration error, and confidence intervals. Also report montage stability and observability under every single-electrode dropout.

The dropout audit is executable with:

```powershell
python scripts/run_geometry_audit.py --calibration data/train.npz --forward-model data/forward_model.npz
```

## Claim boundary

This implementation establishes a testable algorithm and a reproducible interface. It does not establish anatomical validity unless the supplied forward model is valid, or communication efficacy until the pre-registered held-out evaluation passes.
