"""Extract and audit a bigP3BCI EDF file without making decoder claims."""

from __future__ import annotations

import argparse
import json

from neurosync_p300.bigp3bci_data import load_bigp3bci_edf


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--edf", required=True)
    args = parser.parse_args()
    dataset = load_bigp3bci_edf(args.edf)
    print(json.dumps({
        "shape": list(dataset.epochs.shape),
        "sampling_rate": dataset.sampling_rate,
        "channels": dataset.channel_names,
        "audit": dataset.metadata["event_table_audit"],
        "claim_boundary": dataset.metadata["paradigm_boundary"],
    }, indent=2))


if __name__ == "__main__":
    main()
