import argparse

from analysis.data import get_frame

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
    print(frame)
