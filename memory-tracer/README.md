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
