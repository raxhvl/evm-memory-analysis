import os

import pandas as pd

from tracer.fs import FileType, get_output_dir


def get_frame(start_block, end_block):

    output_dir = get_output_dir(start_block, end_block)
    transactions_file = os.path.join(output_dir, f"{FileType.TRANSACTION.value}.csv.gz")
    call_frames_file = os.path.join(output_dir, f"{FileType.CALL_FRAME.value}.csv.gz")

    transactions = pd.read_csv(transactions_file)
    call_frames = pd.read_csv(call_frames_file)

    # Merge the data on the transaction_id
    merged_data = pd.merge(call_frames, transactions, left_on="transaction_id", right_on="id")

    # Drop the 'id' column from the merged data as it's redundant
    merged_data.drop(columns=["id"], inplace=True)

    # Convert columns to appropriate types
    merged_data["block"] = merged_data["block"].astype(int)
    merged_data["tx_gas"] = merged_data["tx_gas"].astype(int)
    merged_data["memory_gas_cost"] = merged_data["memory_gas_cost"].astype(int)
    merged_data["pre_active_memory_size"] = merged_data["pre_active_memory_size"].astype(int)
    merged_data["post_active_memory_size"] = merged_data["post_active_memory_size"].astype(int)
    merged_data["memory_expansion"] = merged_data["memory_expansion"].astype(int)

    return merged_data
