# git_nem: Proof-of-Stake Validator Node Simulator

This repository contains a Python script that simulates a simplified Proof-of-Stake (PoS) blockchain network. It is designed as an educational tool to demonstrate the core concepts of PoS, including validator selection, block proposal, and network consensus. This is not a production-ready system but an architectural model of a decentralized component.

## Concept

In a Proof-of-Stake consensus mechanism, participants (called "validators") lock up capital (their "stake") in the network. In return, they get the right to participate in the consensus process. The network algorithmically selects a validator to create the next block, and the probability of being chosen is typically proportional to the size of the validator's stake. This approach avoids the high energy consumption of Proof-of-Work (PoW) systems.

This script simulates:
- A network of validator nodes, each with a different amount of stake.
- The generation and propagation of transactions.
- The stake-weighted selection of a validator to propose the next block.
- The creation, broadcasting, and validation of new blocks by all nodes in the network.

## Code Architecture

The simulation is built around several key classes that interact to create the network dynamics:

- `Transaction`: A simple data class representing a transfer of value between two addresses. In a real system, this would be cryptographically signed.

- `Block`: Represents a block in the chain. It contains a list of transactions, a timestamp, its own hash, and the hash of the previous block, linking them together. It also stores the address of the validator who created it.

- `Blockchain`: A class that manages the list of blocks. It handles adding new blocks and provides access to the latest block. In this simulation, it's treated as a shared resource that each node interacts with to maintain their local copy of the chain.

- `ValidatorNode`: The core component of the simulation. Each `ValidatorNode` object represents a participant in the network. It has:
    - A unique `address`.
    - A `stake` value.
    - A `mempool` for storing unconfirmed transactions.
    - Its own copy of the `blockchain`.
    - Methods to `propose_block` and `validate_and_add_block`.

- `NetworkSimulator`: An orchestrator class that sets up the environment, creates the nodes, runs the simulation rounds, and initiates the validator selection process. It drives the entire simulation from a central point.

## How it Works

The simulation proceeds in rounds, with each round resulting in the creation of one new block.

1.  **Initialization**: The `NetworkSimulator` is created. It initializes a global `Blockchain` with a genesis block and creates a specified number of `ValidatorNode` instances, each assigned a random stake.

2.  **Transaction Generation**: In each round, the simulator creates several random `Transaction` objects. These transactions are "broadcast" by sending them to a few random nodes, which add them to their local mempool.

3.  **Validator Selection**: The `NetworkSimulator` calls the `select_validator` method. This method calculates the total stake across the entire network and chooses one `ValidatorNode` to be the block proposer for the current round. The selection is weighted, meaning nodes with a higher stake have a proportionally higher chance of being selected.

4.  **Block Proposal**: The selected validator node creates a new `Block`. It takes a set of transactions from its mempool, bundles them into the block, and calculates the block's hash. 

5.  **Block Broadcasting & Validation**: The newly proposed block is "broadcast" to all other nodes in the network. Each receiving node independently performs validation checks:
    - It verifies that the block's `previous_hash` matches the hash of the last block in its own local chain.
    - It recalculates the block's hash to ensure the content has not been tampered with.
    - If all checks pass, the node adds the new block to its local copy of the blockchain.

6.  **Repeat**: The process repeats for the configured number of rounds, extending the blockchain one block at a time.

## Usage Example

This script is self-contained and does not require any external libraries. You can run it directly using a Python 3 interpreter.

1.  Save the code as `script.py`.
2.  Run the script from your terminal:

    ```bash
    python script.py
    ```

3.  **Expected Output**: The script will print a detailed log of the simulation process to the console. You will see nodes being created, transactions being generated, a validator being selected for each round, and blocks being proposed and validated by the network. At the end, it will print a summary of the final blockchain.

    ```
    Created Node 0 with stake 543
    Created Node 1 with stake 112
    ...

    --- Starting Proof-of-Stake Simulation ---

    ================ ROUND 1 ================

    --- 1. Generating Transactions ---
    Node validator_node_3_... received transaction: validator_node_1_... -> validator_node_0_...: 5.67
    ...

    --- 2. Selecting Validator ---
    Chosen Validator: Node 0 (validator_node_0_...) with stake 543

    --- 3. Proposing Block ---
    Validator proposed: Block 1 | By: validator_... | Txns: 5 | Hash: a3f4e...

    --- 4. Broadcasting and Validating Block ---
    Proposing Node validator_... added its own block to its chain.
    Node validator_... successfully validated and added Block 1...
    ...

    ================ SIMULATION FINISHED ================

    --- Final Blockchain State ---
    Block 0 | By: genesis | Txns: 0 | Hash: ...
    Block 1 | By: validator_... | Txns: 5 | Hash: ...
    Block 2 | By: validator_... | Txns: 4 | Hash: ...
    ...
    ```