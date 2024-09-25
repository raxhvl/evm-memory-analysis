import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from analysis.data import get_frame


def analyze_memory_trends(start_block, end_block):
    merged_data = get_frame(start_block, end_block)
    # 1. What opcodes consume most memory?
    memory_by_opcode = (
        merged_data.groupby("opcode")["memory_access_size"].sum().sort_values(ascending=False)
    )
    memory_by_opcode.plot(kind="bar", title="Memory Consumption by Opcode")
    plt.ylabel("Memory Access Size")
    plt.savefig("memory_consumption_by_opcode.png")
    plt.clf()

    # 2. Most common offsets
    common_offsets = merged_data["memory_access_offset"].value_counts().head(10)
    common_offsets.plot(kind="bar", title="Most Common Memory Access Offsets")
    plt.ylabel("Frequency")
    plt.savefig("common_memory_access_offsets.png")
    plt.clf()

    # 3. % gas spent on memory
    total_gas = merged_data["tx_gas"].sum()
    gas_memory = merged_data["opcode_gas_cost"].sum()
    gas_memory_percentage = (gas_memory / total_gas) * 100
    plt.bar(["Gas Spent on Memory", "Total Gas"], [gas_memory, total_gas - gas_memory])
    plt.title("Gas Spent on Memory vs Total Gas")
    plt.ylabel("Gas")
    plt.xticks(rotation=45)
    plt.savefig("gas_spent_on_memory.png")
    plt.clf()

    # 4. Frequency of opcodes
    opcode_frequency = merged_data["opcode"].value_counts()
    opcode_frequency.plot(kind="bar", title="Frequency of Opcodes")
    plt.ylabel("Frequency")
    plt.savefig("opcode_frequency.png")
    plt.clf()

    # 5. Distribution of offsets
    plt.hist(merged_data["memory_access_offset"], bins=50, alpha=0.7)
    plt.title("Distribution of Memory Access Offsets")
    plt.xlabel("Memory Access Offset")
    plt.ylabel("Frequency")
    plt.savefig("distribution_of_offsets.png")
    plt.clf()

    # 6. Distribution of sizes
    plt.hist(merged_data["memory_access_size"], bins=50, alpha=0.7)
    plt.title("Distribution of Memory Access Sizes")
    plt.xlabel("Memory Access Size")
    plt.ylabel("Frequency")
    plt.savefig("distribution_of_sizes.png")
    plt.clf()

    # 7. Distribution of call frames
    call_depth_distribution = merged_data["call_depth"].value_counts().sort_index()
    call_depth_distribution.plot(kind="bar", title="Distribution of Call Frames")
    plt.ylabel("Frequency")
    plt.savefig("distribution_of_call_frames.png")
    plt.clf()

    # 8. Distribution of memory across opcodes
    memory_distribution = merged_data.groupby("opcode")["memory_access_size"].sum()
    memory_distribution.plot(kind="bar", title="Memory Distribution Across Opcodes")
    plt.ylabel("Total Memory Access Size")
    plt.savefig("memory_distribution_across_opcodes.png")
    plt.clf()

    # 9. Block wise trends
    block_trends = merged_data.groupby("block")["memory_access_size"].sum()
    block_trends.plot(title="Block Wise Memory Access Size Trends")
    plt.ylabel("Memory Access Size")
    plt.xlabel("Block")
    plt.savefig("block_wise_trends.png")
    plt.clf()
