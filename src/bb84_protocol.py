import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
import random
import json
import os
from datetime import datetime
import pandas as pd

class BB84Protocol:
    def __init__(self, n_bits=100, save_results=True, results_dir='../results'):
        """
        Initialize BB84 protocol
        
        Args:
            n_bits: Number of bits to transmit
            save_results: Whether to save simulation results
            results_dir: Directory to save results
        """
        self.n_bits = n_bits
        self.simulator = AerSimulator()
        self.save_results = save_results
        self.results_dir = results_dir
        self.simulation_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create results directories if they don't exist
        if self.save_results:
            os.makedirs(os.path.join(self.results_dir, 'data'), exist_ok=True)
            os.makedirs(os.path.join(self.results_dir, 'logs'), exist_ok=True)
    
    def alice_prepare_qubits(self, bits, bases):
        """
        Alice prepares qubits based on her bits and bases
        
        Args:
            bits: List of bits (0 or 1)
            bases: List of bases (0 for Z-basis, 1 for X-basis)
        
        Returns:
            List of quantum circuits representing the qubits
        """
        circuits = []
        
        for bit, basis in zip(bits, bases):
            qc = QuantumCircuit(1, 1)
            
            # If bit is 1, apply X gate
            if bit == 1:
                qc.x(0)
            
            # If X-basis (diagonal), apply Hadamard
            if basis == 1:
                qc.h(0)
            
            circuits.append(qc)
        
        return circuits
    
    def bob_measure_qubits(self, circuits, bob_bases):
        """
        Bob measures the qubits with his randomly chosen bases
        
        Args:
            circuits: List of quantum circuits from Alice
            bob_bases: List of bases Bob chooses for measurement
        
        Returns:
            List of measurement results
        """
        measurements = []
        
        for qc, basis in zip(circuits, bob_bases):
            # Create new circuit for measurement
            measure_qc = qc.copy()
            
            # If X-basis, apply Hadamard before measurement
            if basis == 1:
                measure_qc.h(0)
            
            # Measure
            measure_qc.measure(0, 0)
            
            # Run simulation
            result = self.simulator.run(measure_qc, shots=1).result()
            counts = result.get_counts(measure_qc)
            
            # Extract result (0 or 1)
            measured_bit = int(list(counts.keys())[0])
            measurements.append(measured_bit)
        
        return measurements
    
    def sift_key(self, alice_bits, alice_bases, bob_bases, bob_measurements):
        """
        Perform basis reconciliation to get sifted key
        
        Args:
            alice_bits: Alice's original bits
            alice_bases: Alice's chosen bases
            bob_bases: Bob's chosen bases
            bob_measurements: Bob's measurement results
        
        Returns:
            alice_sifted_key, bob_sifted_key
        """
        alice_sifted = []
        bob_sifted = []
        
        for i in range(len(alice_bits)):
            # Keep bits only when bases match
            if alice_bases[i] == bob_bases[i]:
                alice_sifted.append(alice_bits[i])
                bob_sifted.append(bob_measurements[i])
        
        return alice_sifted, bob_sifted
    
    def calculate_qber(self, alice_key, bob_key, sample_size=None):
        """
        Calculate Quantum Bit Error Rate
        
        Args:
            alice_key: Alice's sifted key
            bob_key: Bob's sifted key
            sample_size: Size of sample to check (if None, check all)
        
        Returns:
            QBER value (float)
        """
        if len(alice_key) == 0:
            return 0.0
            
        if sample_size is None:
            sample_size = len(alice_key)
        
        # Randomly sample bits for QBER estimation
        sample_indices = random.sample(range(len(alice_key)), 
                                     min(sample_size, len(alice_key)))
        
        errors = 0
        for i in sample_indices:
            if alice_key[i] != bob_key[i]:
                errors += 1
        
        qber = errors / len(sample_indices)
        return qber
    
    def run_protocol(self, with_eve=False, eve_strategy='intercept_resend', save_detailed=False):
        """
        Run the complete BB84 protocol
        
        Args:
            with_eve: Whether to simulate eavesdropping
            eve_strategy: Type of eavesdropping attack
            save_detailed: Whether to save detailed step-by-step results
        
        Returns:
            Dictionary with protocol results
        """
        # Step 1: Generate random bits and bases for Alice
        alice_bits = [random.randint(0, 1) for _ in range(self.n_bits)]
        alice_bases = [random.randint(0, 1) for _ in range(self.n_bits)]
        
        # Step 2: Prepare qubits
        circuits = self.alice_prepare_qubits(alice_bits, alice_bases)
        
        # Step 3: Simulate eavesdropping if enabled
        if with_eve:
            if eve_strategy == 'intercept_resend':
                circuits = self.eve_intercept_resend(circuits)
            # Add more attack strategies here
        
        # Step 4: Bob chooses random bases and measures
        bob_bases = [random.randint(0, 1) for _ in range(self.n_bits)]
        bob_measurements = self.bob_measure_qubits(circuits, bob_bases)
        
        # Step 5: Basis reconciliation
        alice_sifted, bob_sifted = self.sift_key(alice_bits, alice_bases, 
                                                bob_bases, bob_measurements)
        
        # Step 6: Calculate QBER
        qber = self.calculate_qber(alice_sifted, bob_sifted, 
                                  sample_size=min(50, len(alice_sifted)//2))
        
        # Compile results
        results = {
            'simulation_id': self.simulation_id,
            'timestamp': datetime.now().isoformat(),
            'n_bits': self.n_bits,
            'with_eve': with_eve,
            'eve_strategy': eve_strategy if with_eve else None,
            'alice_sifted_key': alice_sifted,
            'bob_sifted_key': bob_sifted,
            'qber': qber,
            'sifted_key_length': len(alice_sifted),
            'key_rate': len(alice_sifted) / self.n_bits,
            'secure': qber <= 0.11 if len(alice_sifted) > 0 else False
        }
        
        # Save detailed results if requested
        if save_detailed and self.save_results:
            detailed_data = {
                'alice_bits': alice_bits,
                'alice_bases': alice_bases,
                'bob_bases': bob_bases,
                'bob_measurements': bob_measurements,
                'basis_matches': [a == b for a, b in zip(alice_bases, bob_bases)],
                'results': results
            }
            self._save_detailed_results(detailed_data)
        
        return results
    
    def eve_intercept_resend(self, circuits):
        """
        Simulate Eve's intercept-resend attack
        
        Args:
            circuits: Original circuits from Alice
        
        Returns:
            Modified circuits after Eve's interference
        """
        new_circuits = []
        
        for qc in circuits:
            # Eve randomly chooses a basis
            eve_basis = random.randint(0, 1)
            
            # Create measurement circuit
            measure_qc = qc.copy()
            
            # If X-basis, apply Hadamard
            if eve_basis == 1:
                measure_qc.h(0)
            
            measure_qc.measure(0, 0)
            
            # Eve measures
            result = self.simulator.run(measure_qc, shots=1).result()
            counts = result.get_counts(measure_qc)
            eve_bit = int(list(counts.keys())[0])
            
            # Eve prepares new qubit
            new_qc = QuantumCircuit(1, 1)
            
            if eve_bit == 1:
                new_qc.x(0)
            
            if eve_basis == 1:
                new_qc.h(0)
            
            new_circuits.append(new_qc)
        
        return new_circuits
    
    def _save_detailed_results(self, data):
        """Save detailed simulation results"""
        filename = f"bb84_detailed_{self.simulation_id}.json"
        filepath = os.path.join(self.results_dir, 'data', filename)
        
        # Convert numpy types to Python types for JSON serialization
        def convert_types(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, list):
                return [convert_types(item) for item in obj]
            return obj
        
        data_copy = {k: convert_types(v) for k, v in data.items()}
        
        with open(filepath, 'w') as f:
            json.dump(data_copy, f, indent=2)
        
        print(f"Detailed results saved to: {filepath}")