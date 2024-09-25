import argparse

import pandas as pd

from analysis.data import get_frame
from analysis.plot import plot_normal_distribution, plot_top_values

# Command-line arguments parsing
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace EVM memory usage.")
    parser.add_argument("start_block", type=int, help="Start block number")
    parser.add_argument("end_block", type=int, help="End block number")

    args = parser.parse_args()
    start_block = args.start_block
    end_block = args.end_block

    if start_block > end_block:
        raise ValueError("Start block should be less than or equal to end block number")

    frame = get_frame(start_block, end_block)
    opcodes = frame.loc[(frame["memory_access_size"] == 0) & (frame["opcode"] == "5e")]

    print(len(opcodes))

    # Split the 'stack' column and extract the 5th and 7th values
    stack_values = opcodes["stack"].str.split(",", expand=True)
    opcodes["offset"] = stack_values[0]
    opcodes["size"] = stack_values[2]

    opcodes = opcodes.loc[opcodes["size"] == "0"]
    print(len(opcodes))

    # Set display options
    pd.set_option("display.max_colwidth", None)
    print(opcodes[["tx_hash", "call_depth", "size"]])
    # plot_top_values(frame, "opcode", "charts/memory_access_offset.png")
