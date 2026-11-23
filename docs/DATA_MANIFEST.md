# Public EEG Data Manifest

Raw recordings are stored under `data/external/` and excluded from Git. This manifest records provenance and SHA-256 checksums for the exact files used on 23 November 2026.

## BNCI 2014-008

- Source: `https://lampx.tugraz.at/~bci/database/008-2014/A0N.mat`
- Participants: eight people with ALS
- Recording: eight active Ag/AgCl EEG electrodes, 256 Hz, P300 row/column speller
- License listed by BNCI Horizon: CC BY-NC-ND 4.0
- Primary citation: Riccio et al., *Frontiers in Human Neuroscience* 2013, DOI `10.3389/fnhum.2013.00732`

| File | SHA-256 |
|---|---|
| A01.mat | `CDF9BCA4F48C61EE9C9BA998382A4E84392918C9DBC5A43F45EE0052614E25BD` |
| A02.mat | `0023EE04E4A113231C125BCFDF59780ED95D858A5E5C0BC993701EB6C9652894` |
| A03.mat | `820287459D83E5512E3AC00CDB25D1806B26518DABA14281C61983B230F9DD9F` |
| A04.mat | `65B14803EB38FDA4910CCA1103E4B527BE1624155F106FE8083861BBF3E644E3` |
| A05.mat | `D372AE2C39ECE0C8DDED986307E70EBB7F4BDF2C5C2FA2382C8BA489FB59F200` |
| A06.mat | `8320E78FB0D73BAA03857C4976A4B4D8E605B1C9A7A4CF2E5E80E1BB6FD30337` |
| A07.mat | `444D9DA58332F58E89E7CDD39F9D9E7B0CB8EE4FD01CE03EF3CE57E53068F47C` |
| A08.mat | `7B5D249058DCAC4AD477EA8591256D51C19DF384551EBA82B6C88E3AE6333571` |

## BCI Competition III Dataset II

- Source: `https://www.bbci.de/competition/download/competition_iii/albany/subject_B.zip`
- Recording: 64-channel, 240 Hz Wadsworth P300 speller
- Subject B archive SHA-256: `06109CD2EA564B5A11C6459E31AD961B36BBA544A204B3C06A3CAEFE84CCF7E8`
- Subject A was already present locally and is processed with the same importer.

## bigP3BCI registry

The 2025 bigP3BCI resource is the planned cohort-scale extension: approximately 267 participants across 20 studies, including ALS metadata where available. Its total uncompressed size is approximately 44.6 GB, so it is not silently mirrored by this repository. Download and study selection must be explicit to prevent unnecessary transfer and accidental mixing of incompatible paradigms.

- PhysioNet: `https://physionet.org/content/bigp3bci/1.0.0/`
- DOI: `10.13026/0byy-ry86`
- License: CC BY 4.0
