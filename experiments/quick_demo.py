import os
import sys

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from bb84_protocol import BB84Protocol
import matplotlib.pyplot as plt

def quick_demo():
    """Quick demonstration of BB84 protocol"""
    print("BB84 Protocol Quick Demo")
    print("=" * 30)
    
    # Create protocol instance
    bb84 = BB84Protocol(n_bits=100, save_results=True, results_dir='../results')
    
    # Test without eavesdropping
    print("\n1. Running BB84 without eavesdropping...")
    result_no_eve = bb84.run_protocol(with_eve=False, save_detailed=True)
    
    print(f"   QBER: {result_no_eve['qber']:.4f}")
    print(f"   Key rate: {result_no_eve['key_rate']:.4f}")
    print(f"   Sifted key length: {result_no_eve['sifted_key_length']}")
    print(f"   Secure: {result_no_eve['secure']}")
    
    # Test with eavesdropping
    print("\n2. Running BB84 with eavesdropping...")
    result_with_eve = bb84.run_protocol(with_eve=True, save_detailed=True)
    
    print(f"   QBER: {result_with_eve['qber']:.4f}")
    print(f"   Key rate: {result_with_eve['key_rate']:.4f}")
    print(f"   Sifted key length: {result_with_eve['sifted_key_length']}")
    print(f"   Secure: {result_with_eve['secure']}")
    
    # Create simple comparison plot
    scenarios = ['No Eavesdropping', 'With Eavesdropping']
    qbers = [result_no_eve['qber'], result_with_eve['qber']]
    colors = ['green', 'red']
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(scenarios, qbers, color=colors, alpha=0.7)
    plt.axhline(y=0.11, color='darkred', linestyle='--', label='Security Threshold')
    plt.ylabel('QBER')
    plt.title('BB84 Protocol: Eavesdropping Detection Demo')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Add value labels
    for bar, qber in zip(bars, qbers):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{qber:.4f}', ha='center', va='bottom', fontweight='bold')
    
    # Save plot
    plt.savefig('../results/figures/bb84_quick_demo.png', dpi=300, bbox_inches='tight')
    print(f"\n3. Demo plot saved to: ../results/figures/bb84_quick_demo.png")
    plt.show()
    
    print("\n" + "=" * 30)
    print("Quick demo complete!")
    print("=" * 30)

if __name__ == "__main__":
    quick_demo()