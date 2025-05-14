import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
import random
import json
import os
from datetime import datetime
import pandas as pd
import hashlib
from typing import List, Tuple, Dict, Any

class BB84Protocol:
    def __init__(self, n_bits=100, save_results=True, results_dir='../results'):
        """
        Initialize BB84 protocol with error correction and privacy amplification
        
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
    
    def simple_error_correction(self, alice_key: List[int], bob_key: List[int], 
                               qber: float) -> Tuple[List[int], List[int], Dict]:
        """
        Simple error correction using parity check method
        
        Args:
            alice_key: Alice's sifted key
            bob_key: Bob's sifted key  
            qber: Quantum bit error rate
            
        Returns:
            Corrected keys for Alice and Bob, and correction statistics
        """
        if len(alice_key) == 0:
            return [], [], {'errors_corrected': 0, 'parity_checks': 0}
        
        alice_corrected = alice_key.copy()
        bob_corrected = bob_key.copy()
        errors_corrected = 0
        parity_checks = 0
        
        # Simple parity check error correction
        # Divide key into blocks and check parity
        block_size = max(4, int(16 / max(qber, 0.01)))  # Adaptive block size based on QBER
        
        for i in range(0, len(alice_key), block_size):
            block_end = min(i + block_size, len(alice_key))
            
            # Calculate parity for both keys
            alice_parity = sum(alice_key[i:block_end]) % 2
            bob_parity = sum(bob_key[i:block_end]) % 2
            parity_checks += 1
            
            # If parities don't match, there's an error in this block
            if alice_parity != bob_parity:
                # Find the error using binary search approach
                # For simplicity, just flip the first differing bit
                for j in range(i, block_end):
                    if alice_key[j] != bob_key[j]:
                        bob_corrected[j] = alice_key[j]
                        errors_corrected += 1
                        break
        
        return alice_corrected, bob_corrected, {
            'errors_corrected': errors_corrected,
            'parity_checks': parity_checks,
            'block_size': block_size
        }
    
    def privacy_amplification(self, key: List[int], qber: float, 
                            eve_info_estimate: float = None) -> Tuple[List[int], Dict]:
        """
        Privacy amplification using universal hash functions
        
        Args:
            key: Input key after error correction
            qber: Quantum bit error rate
            eve_info_estimate: Estimate of information leaked to Eve
            
        Returns:
            Shortened secure key and amplification statistics
        """
        if len(key) == 0:
            return [], {'key_compression_ratio': 0, 'eve_info_estimate': 0}
        
        # Estimate information leaked to Eve based on QBER
        if eve_info_estimate is None:
            # Conservative estimate: assume Eve gets 1 bit of info per error
            # Plus some additional information from basis reconciliation
            eve_info_estimate = min(qber * len(key) + 0.1 * len(key), len(key) * 0.5)
        
        # Calculate secure key length using entropy formula
        # Secure length = original length - leaked info - security parameter
        security_parameter = max(10, int(0.1 * len(key)))  # Security parameter (typically 100-200 bits)
        secure_length = max(1, int(len(key) - eve_info_estimate - security_parameter))
        
        # Use universal hash function (simple implementation)
        # In practice, this would use proper universal hash families
        hashed_key = self._universal_hash(key, secure_length)
        
        compression_ratio = secure_length / len(key) if len(key) > 0 else 0
        
        return hashed_key, {
            'original_length': len(key),
            'secure_length': secure_length,
            'eve_info_estimate': eve_info_estimate,
            'security_parameter': security_parameter,
            'key_compression_ratio': compression_ratio
        }
    
    def _universal_hash(self, key: List[int], output_length: int) -> List[int]:
        """
        Simple universal hash function implementation
        
        Args:
            key: Input bit string
            output_length: Desired output length
            
        Returns:
            Hashed key of specified length
        """
        # Convert bit list to byte string
        key_str = ''.join(map(str, key))
        
        # Use multiple hash iterations to get required length
        hashed_bits = []
        seed = 0
        
        while len(hashed_bits) < output_length:
            # Create hash with different seed each iteration
            hash_input = f"{key_str}{seed}".encode()
            hash_result = hashlib.sha256(hash_input).hexdigest()
            
            # Convert hex to binary
            binary_str = bin(int(hash_result, 16))[2:].zfill(256)
            hashed_bits.extend([int(b) for b in binary_str])
            seed += 1
        
        return hashed_bits[:output_length]
    
    def run_protocol(self, with_eve=False, eve_strategy='intercept_resend', 
                    save_detailed=False, enable_error_correction=True, 
                    enable_privacy_amplification=True):
        """
        Run the complete BB84 protocol with error correction and privacy amplification
        
        Args:
            with_eve: Whether to simulate eavesdropping
            eve_strategy: Type of eavesdropping attack
            save_detailed: Whether to save detailed step-by-step results
            enable_error_correction: Whether to perform error correction
            enable_privacy_amplification: Whether to perform privacy amplification
        
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
        
        # Step 5: Basis reconciliation (sifting)
        alice_sifted, bob_sifted = self.sift_key(alice_bits, alice_bases, 
                                                bob_bases, bob_measurements)
        
        # Step 6: Calculate QBER
        qber = self.calculate_qber(alice_sifted, bob_sifted, 
                                  sample_size=min(50, len(alice_sifted)//2))
        
        # Initialize keys for further processing
        alice_corrected = alice_sifted
        bob_corrected = bob_sifted
        error_correction_stats = {}
        privacy_amplification_stats = {}
        
        # Step 7: Error Correction (if enabled and needed)
        if enable_error_correction and len(alice_sifted) > 0:
            alice_corrected, bob_corrected, error_correction_stats = \
                self.simple_error_correction(alice_sifted, bob_sifted, qber)
        
        # Step 8: Privacy Amplification (if enabled)
        final_alice_key = alice_corrected
        final_bob_key = bob_corrected
        
        if enable_privacy_amplification and len(alice_corrected) > 0:
            # Apply privacy amplification to Alice's key
            final_alice_key, privacy_amplification_stats = \
                self.privacy_amplification(alice_corrected, qber)
            
            # Bob applies the same hash function (in practice, Alice would share the hash function)
            final_bob_key, _ = self.privacy_amplification(bob_corrected, qber)
        
        # Step 9: Final security check
        final_qber = self.calculate_qber(final_alice_key, final_bob_key) if len(final_alice_key) > 0 else 0
        is_secure = final_qber <= 0.11 and len(final_alice_key) > 0
        
        # Compile results
        results = {
            'simulation_id': self.simulation_id,
            'timestamp': datetime.now().isoformat(),
            'n_bits': self.n_bits,
            'with_eve': with_eve,
            'eve_strategy': eve_strategy if with_eve else None,
            
            # Sifting results
            'alice_sifted_key': alice_sifted,
            'bob_sifted_key': bob_sifted,
            'sifted_key_length': len(alice_sifted),
            'sifting_rate': len(alice_sifted) / self.n_bits,
            'qber_after_sifting': qber,
            
            # Error correction results
            'error_correction_enabled': enable_error_correction,
            'error_correction_stats': error_correction_stats,
            'alice_corrected_key': alice_corrected,
            'bob_corrected_key': bob_corrected,
            
            # Privacy amplification results
            'privacy_amplification_enabled': enable_privacy_amplification,
            'privacy_amplification_stats': privacy_amplification_stats,
            
            # Final results
            'final_alice_key': final_alice_key,
            'final_bob_key': final_bob_key,
            'final_key_length': len(final_alice_key),
            'final_qber': final_qber,
            'overall_key_rate': len(final_alice_key) / self.n_bits,
            'secure': is_secure,
            
            # Legacy fields for backward compatibility
            'key_rate': len(alice_sifted) / self.n_bits,
            'qber': qber
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