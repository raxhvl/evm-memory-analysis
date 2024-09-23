# EVM Memory Tracer

A python script that traces usage of evm memory within a range of blocks.

## Prerequisites

- Python 3.11 or higher
- PIP

## Installation

Set up virtual python environment

```bash
python -m venv ./venv && source venv/bin/activate
```

Install project dependencies

```bash
pip install -r requirements.txt
```

Copy the `.env` file from the provided example and add the RPC endpoint:

```bash
cp .env.example .env
```

## Usage

### Command-Line Arguments

The script is executed from the command line and accepts two required arguments:

- `start_block`: The starting block number (integer).
- `end_block`: The ending block number (integer).

The `start_block` should be less than or equal to `end_block`.

### Running the Script

To run the script, use the following command:

```bash
python tracer.py <start_block> <end_block>

```

To view the script's resource consumption, use the following command:

```bash
./run.sh <start_block> <end_block>

```

### Output

The script generates two gzip files in the `data/<start_block>_to_<end_block>` directory:

- `transactions.csv.gzip`: Contains the summary of transactions.
- `callframes.csv.gzip`: Contains the memory usage of each call frames from of the captured transactions.
