import hashlib
import json
import random
import time
from typing import List, Dict, Optional

# --- Core Data Structures ---

class Transaction:
    """
    Represents a single transaction in the network.
    In a real system, this would be cryptographically signed.
    """
    def __init__(self, sender: str, recipient: str, amount: float):
        """
        Initializes a transaction.
        :param sender: The address of the sender.
        :param recipient: The address of the recipient.
        :param amount: The amount being transferred.
        """
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.timestamp = time.time()
        # In a real implementation, a signature would be created here.
        self.signature = f"signed_by_{sender}"

    def to_dict(self) -> Dict:
        """Converts the transaction to a dictionary for serialization."""
        return {
            'sender': self.sender,
            'recipient': self.recipient,
            'amount': self.amount,
            'timestamp': self.timestamp,
            'signature': self.signature
        }

    def __str__(self) -> str:
        return f"{self.sender} -> {self.recipient}: {self.amount}"


class Block:
    """
    Represents a block in the blockchain, containing transactions, metadata,
    and a link to the previous block.
    """
    def __init__(self, index: int, transactions: List[Transaction], previous_hash: str, validator: str):
        """
        Initializes a block.
        :param index: The block's position in the chain.
        :param transactions: A list of transactions included in the block.
        :param previous_hash: The hash of the preceding block.
        :param validator: The address of the validator node that created this block.
        """
        self.index = index
        self.timestamp = time.time()
        self.transactions = [tx.to_dict() for tx in transactions]
        self.previous_hash = previous_hash
        self.validator = validator
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        """
        Calculates the SHA-256 hash of the block.
        The hash is based on the block's content, ensuring its integrity.
        """
        block_string = json.dumps({
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': self.transactions,
            'previous_hash': self.previous_hash,
            'validator': self.validator
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def __str__(self) -> str:
        return f"Block {self.index} | By: {self.validator[:10]}... | Txns: {len(self.transactions)} | Hash: {self.hash[:15]}..."


class Blockchain:
    """
    Manages the chain of blocks. This class is intended to be a shared
    resource among all nodes in the simulation.
    """
    def __init__(self):
        """Initializes the blockchain and creates the genesis block."""
        self.chain: List[Block] = []
        self.create_genesis_block()

    def create_genesis_block(self):
        """Creates the very first block in the chain."""
        genesis_block = Block(index=0, transactions=[], previous_hash="0", validator="genesis")
        self.chain.append(genesis_block)

    @property
    def latest_block(self) -> Block:
        """Returns the most recent block in the chain."""
        return self.chain[-1]

    def add_block(self, block: Block) -> bool:
        """
        Adds a new block to the chain after validation.
        :param block: The new block to be added.
        :return: True if the block was added successfully, False otherwise.
        """
        # Basic validation: check if the previous_hash matches the latest block's hash.
        if block.previous_hash != self.latest_block.hash:
            print(f"[ERROR] Invalid previous hash for Block {block.index}.")
            return False
        
        # In a real scenario, more checks would be performed, e.g., signature verification.
        self.chain.append(block)
        return True


# --- Node and Network Simulation ---

class ValidatorNode:
    """
    Simulates a validator node in a Proof-of-Stake network.
    Each node has a stake, maintains a mempool of transactions, and participates
    in the block creation and validation process.
    """
    def __init__(self, address: str, stake: int, blockchain: Blockchain):
        """
        Initializes a validator node.
        :param address: A unique identifier for the node.
        :param stake: The amount of currency staked by the node.
        :param blockchain: A reference to the shared blockchain instance.
        """
        self.address = address
        self.stake = stake
        self.mempool: List[Transaction] = []
        # Each node keeps its own copy of the chain, starting with the shared one.
        self.blockchain = blockchain 

    def receive_transaction(self, transaction: Transaction):
        """
        Receives a new transaction and adds it to the mempool.
        In a real system, it would validate the transaction first.
        """
        print(f"Node {self.address[:10]}... received transaction: {transaction}")
        self.mempool.append(transaction)

    def propose_block(self) -> Optional[Block]:
        """
        If the node has transactions in its mempool, it creates and returns a new block.
        This would be called after this node has been selected as the validator.
        """
        if not self.mempool:
            print(f"Node {self.address[:10]}... has no transactions to propose.")
            return None

        # Usually, a node would pick the most profitable transactions.
        # Here we just take the first few (e.g., up to 5).
        transactions_for_block = self.mempool[:5]

        new_block = Block(
            index=self.blockchain.latest_block.index + 1,
            transactions=transactions_for_block,
            previous_hash=self.blockchain.latest_block.hash,
            validator=self.address
        )

        # Clear the processed transactions from the mempool.
        self.mempool = self.mempool[5:]
        return new_block

    def validate_and_add_block(self, block: Block) -> bool:
        """
        Validates a block received from the network and adds it to its local chain.
        """
        expected_hash = block.calculate_hash()
        if block.hash != expected_hash:
            print(f"[VALIDATION FAILED] Node {self.address[:10]}...: Block {block.index} hash is corrupt.")
            return False
        
        if block.previous_hash != self.blockchain.latest_block.hash:
            print(f"[VALIDATION FAILED] Node {self.address[:10]}...: Block {block.index} previous_hash is invalid.")
            # This could indicate a fork, which requires more complex resolution logic (e.g., longest chain rule).
            # For this simulation, we assume a simple linear progression.
            return False

        # If validation passes, add the block to the local copy of the chain.
        self.blockchain.add_block(block)
        print(f"Node {self.address[:10]}... successfully validated and added {block}")
        return True


class NetworkSimulator:
    """
    Orchestrates the entire simulation, managing nodes, generating transactions,
    and running the consensus rounds.
    """
    def __init__(self, num_nodes: int):
        self.blockchain = Blockchain()
        self.nodes: List[ValidatorNode] = []

        # Create validator nodes with random stakes.
        for i in range(num_nodes):
            address = f'validator_node_{i}_' + hashlib.sha256(str(random.random()).encode()).hexdigest()
            stake = random.randint(10, 1000)
            node = ValidatorNode(address, stake, self.blockchain)
            self.nodes.append(node)
            print(f"Created Node {i} with stake {stake}")

    def select_validator(self) -> ValidatorNode:
        """
        Selects a validator for the next block based on their stake.
        Nodes with higher stakes have a higher probability of being chosen.
        This is the core of the Proof-of-Stake mechanism.
        """
        total_stake = sum(node.stake for node in self.nodes)
        weights = [node.stake / total_stake for node in self.nodes]
        
        # random.choices allows for weighted random selection.
        chosen_validator = random.choices(self.nodes, weights, k=1)[0]
        return chosen_validator

    def run_simulation(self, num_blocks_to_create: int):
        """
        Runs the main simulation loop.
        :param num_blocks_to_create: The number of blocks to simulate creating.
        """
        print("\n--- Starting Proof-of-Stake Simulation ---")
        for i in range(num_blocks_to_create):
            print(f"\n================ ROUND {i + 1} ================")
            
            # 1. Generate some random transactions and distribute them to nodes.
            print("\n--- 1. Generating Transactions ---")
            for _ in range(random.randint(3, 8)):
                sender_node = random.choice(self.nodes)
                recipient_node = random.choice(self.nodes)
                if sender_node == recipient_node:
                    continue # Avoid sending to self
                
                tx = Transaction(sender_node.address, recipient_node.address, random.uniform(0.1, 10))
                # Broadcast transaction to a few random nodes
                for node in random.sample(self.nodes, k=min(3, len(self.nodes))):
                    node.receive_transaction(tx)

            time.sleep(1) # Simulate network delay

            # 2. Select a validator for this round.
            print("\n--- 2. Selecting Validator ---")
            validator = self.select_validator()
            print(f"Chosen Validator: Node {self.nodes.index(validator)} ({validator.address[:10]}...) with stake {validator.stake}")

            time.sleep(1)

            # 3. The chosen validator proposes a new block.
            print("\n--- 3. Proposing Block ---")
            new_block = validator.propose_block()
            if not new_block:
                print("Validator had no transactions. Skipping block proposal for this round.")
                continue
            
            print(f"Validator proposed: {new_block}")
            time.sleep(1)

            # 4. Broadcast the new block to all other nodes for validation.
            print("\n--- 4. Broadcasting and Validating Block ---")
            for node in self.nodes:
                # The proposing node doesn't need to re-validate, it adds it directly.
                if node == validator:
                    node.blockchain.add_block(new_block)
                    print(f"Proposing Node {node.address[:10]}... added its own block to its chain.")
                else:
                    # Other nodes validate the block before adding it.
                    node.validate_and_add_block(new_block)
        
        print("\n================ SIMULATION FINISHED ================")
        self.print_final_state()

    def print_final_state(self):
        """Prints the final state of the blockchain and nodes."""
        print("\n--- Final Blockchain State ---")
        for block in self.blockchain.chain:
            print(block)
        
        print("\n--- Final Node Stakes ---")
        for i, node in enumerate(self.nodes):
            print(f"Node {i} ({node.address[:10]}...): Stake = {node.stake}")

if __name__ == '__main__':
    # Run the simulation with 5 nodes, creating 5 new blocks.
    simulation = NetworkSimulator(num_nodes=5)
    simulation.run_simulation(num_blocks_to_create=5)
