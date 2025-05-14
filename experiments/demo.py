import os
import sys
import traceback
import matplotlib
matplotlib.use('TkAgg')  
import matplotlib.pyplot as plt
import numpy as np


# Add src directory to Python path
src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
sys.path.insert(0, src_path)

def debug_imports():
    """Test if imports work correctly"""
    print("Testing imports...")
    print(f"Current directory: {os.getcwd()}")
    print(f"Python path: {sys.path}")
    print(f"Adding to path: {src_path}")
    
    try:
        print("Attempting to import BB84Analysis...")
        from analysis import BB84Analysis
        print("✓ Successfully imported BB84Analysis")
        
        print("Attempting to import BB84Protocol...")
        from bb84_protocol import BB84Protocol
        print("✓ Successfully imported BB84Protocol")
        
        return True, BB84Analysis, BB84Protocol
    except Exception as e:
        print(f"✗ Import error: {type(e).__name__}: {e}")
        print("Full traceback:")
        traceback.print_exc()
        return False, None, None

def quick_test(BB84Protocol):
    """Run a quick test of the BB84 protocol"""
    print("\nRunning quick test...")
    try:
        protocol = BB84Protocol(n_bits=50)
        result = protocol.run_protocol(with_eve=False)
        print(f"✓ Quick test successful!")
        print(f"  QBER: {result['qber']:.4f}")
        print(f"  Secure: {result['secure']}")
        return True
    except Exception as e:
        print(f"✗ Quick test failed: {e}")
        traceback.print_exc()
        return False

def quick_demo(BB84Protocol):
    """Quick demonstration of BB84 protocol with error correction and privacy amplification"""
    print("\n" + "="*40)
    print("BB84 PROTOCOL QUICK DEMO")
    print("="*40)
    
    # Create protocol instance
    bb84 = BB84Protocol(n_bits=100, save_results=True, results_dir='../results')
    
    print("\n1. Running BB84 without eavesdropping (full protocol)...")
    result_no_eve = bb84.run_protocol(with_eve=False, save_detailed=True,
                                     enable_error_correction=True,
                                     enable_privacy_amplification=True)
    
    print(f"   Initial QBER: {result_no_eve['qber']:.4f}")
    print(f"   Sifted key length: {result_no_eve['sifted_key_length']}")
    print(f"   Final key length: {result_no_eve['final_key_length']}")
    print(f"   Overall key rate: {result_no_eve['overall_key_rate']:.4f}")
    print(f"   Secure: {result_no_eve['secure']}")
    
    print("\n2. Running BB84 with eavesdropping (full protocol)...")
    result_with_eve = bb84.run_protocol(with_eve=True, save_detailed=True,
                                       enable_error_correction=True,
                                       enable_privacy_amplification=True)
    
    print(f"   Initial QBER: {result_with_eve['qber']:.4f}")
    print(f"   Sifted key length: {result_with_eve['sifted_key_length']}")
    print(f"   Final key length: {result_with_eve['final_key_length']}")
    print(f"   Overall key rate: {result_with_eve['overall_key_rate']:.4f}")
    print(f"   Secure: {result_with_eve['secure']}")
    
    if result_with_eve['error_correction_enabled']:
        ec_stats = result_with_eve['error_correction_stats']
        print(f"   Errors corrected: {ec_stats.get('errors_corrected', 0)}")
    
    if result_with_eve['privacy_amplification_enabled']:
        pa_stats = result_with_eve['privacy_amplification_stats']
        print(f"   Key compression ratio: {pa_stats.get('key_compression_ratio', 0):.3f}")
    
    # Create comprehensive comparison plot
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    
    scenarios = ['No Eavesdropping', 'With Eavesdropping']
    colors = ['green', 'red']
    
    # Plot 1: QBER Comparison
    qbers = [result_no_eve['qber'], result_with_eve['qber']]
    bars1 = ax1.bar(scenarios, qbers, color=colors, alpha=0.7)
    ax1.axhline(y=0.11, color='darkred', linestyle='--', linewidth=2, 
                label='Security Threshold (11%)')
    ax1.set_ylabel('QBER')
    ax1.set_title('Quantum Bit Error Rate')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Add value labels
    for bar, qber in zip(bars1, qbers):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{qber:.4f}', ha='center', va='bottom', fontweight='bold')
    
    # Plot 2: Key Lengths Comparison
    sifted_lengths = [result_no_eve['sifted_key_length'], result_with_eve['sifted_key_length']]
    final_lengths = [result_no_eve['final_key_length'], result_with_eve['final_key_length']]
    
    x = np.arange(len(scenarios))
    width = 0.35
    
    bars2a = ax2.bar(x - width/2, sifted_lengths, width, label='After Sifting', 
                    color=['lightgreen', 'lightcoral'], alpha=0.7)
    bars2b = ax2.bar(x + width/2, final_lengths, width, label='Final Key', 
                    color=['darkgreen', 'darkred'], alpha=0.7)
    
    ax2.set_ylabel('Key Length (bits)')
    ax2.set_title('Key Length at Different Stages')
    ax2.set_xticks(x)
    ax2.set_xticklabels(scenarios)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Key Rate Comparison
    sifting_rates = [result_no_eve['sifting_rate'], result_with_eve['sifting_rate']]
    overall_rates = [result_no_eve['overall_key_rate'], result_with_eve['overall_key_rate']]
    
    bars3a = ax3.bar(x - width/2, sifting_rates, width, label='Sifting Rate', 
                    color=['lightblue', 'lightyellow'], alpha=0.7)
    bars3b = ax3.bar(x + width/2, overall_rates, width, label='Overall Rate', 
                    color=['blue', 'orange'], alpha=0.7)
    
    ax3.set_ylabel('Key Rate')
    ax3.set_title('Key Generation Rates')
    ax3.set_xticks(x)
    ax3.set_xticklabels(scenarios)
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Security Analysis
    security_status = [1 if result_no_eve['secure'] else 0, 
                      1 if result_with_eve['secure'] else 0]
    colors_security = ['green' if s else 'red' for s in security_status]
    
    bars4 = ax4.bar(scenarios, security_status, color=colors_security, alpha=0.7)
    ax4.set_ylabel('Secure (1) / Insecure (0)')
    ax4.set_title('Security Status')
    ax4.set_ylim(0, 1.2)
    ax4.grid(True, alpha=0.3)
    
    # Add status labels
    for bar, status in zip(bars4, security_status):
        height = bar.get_height()
        label = 'SECURE' if status else 'INSECURE'
        ax4.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                label, ha='center', va='bottom', fontweight='bold', fontsize=10)
    
    plt.suptitle('BB84 Protocol: Complete Analysis with Error Correction & Privacy Amplification', 
                fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    # Ensure results directory exists
    os.makedirs('../results/figures', exist_ok=True)
    
    # Save plot
    plt.savefig('../results/figures/bb84_complete_demo.png', dpi=300, bbox_inches='tight')
    print(f"\n3. Complete demo plot saved to: ../results/figures/bb84_complete_demo.png")
    plt.show()
    
    print("\n" + "="*40)
    print("QUICK DEMO COMPLETE!")
    print("="*40)

def full_analysis(BB84Analysis):
    """Run comprehensive analysis including error correction and privacy amplification"""
    print("\n" + "="*40)
    print("BB84 COMPREHENSIVE ANALYSIS")
    print("="*40)
    
    print("\nCreating BB84Analysis instance...")
    analyzer = BB84Analysis(n_bits=200, n_trials=10, results_dir='../results')  # Increased for better stats
    print("✓ Successfully created analyzer")
    
    print("\nRunning comprehensive analysis...")
    try:
        # Original analysis
        print("1. Running eavesdropping analysis...")
        eavesdrop_results, key_length_results = analyzer.run_comprehensive_analysis()
        
        # New analyses
        print("\n2. Running error correction analysis...")
        error_correction_results = analyzer.analyze_error_correction_impact()
        
        print("\n3. Running privacy amplification analysis...")
        privacy_amplification_results = analyzer.analyze_privacy_amplification_impact()
        
        print("\n" + "="*40)
        print("ANALYSIS COMPLETE!")
        print("="*40)
        print(f"Results saved in: {analyzer.results_dir}")
        
        # Print summary of new analyses
        print("\nError Correction Summary:")
        print(f"- Without Error Correction: {error_correction_results['No Error Correction']['mean_final_key_length']:.1f} bits")
        print(f"- With Error Correction: {error_correction_results['With Error Correction']['mean_final_key_length']:.1f} bits")
        print(f"- Average errors corrected: {error_correction_results['With Error Correction']['mean_errors_corrected']:.1f}")
        
        print(f"\nPrivacy Amplification Summary:")
        print(f"- Compression ratios range from {min(privacy_amplification_results['compression_ratios']):.3f} to {max(privacy_amplification_results['compression_ratios']):.3f}")
        print(f"- Higher QBER leads to more aggressive compression")
        
        return True
    except Exception as e:
        print(f"✗ Analysis failed: {e}")
        traceback.print_exc()
        return False

def test_protocol_components(BB84Protocol):
    """Test individual components of the enhanced BB84 protocol"""
    print("\n" + "="*40)
    print("TESTING PROTOCOL COMPONENTS")
    print("="*40)
    
    try:
        bb84 = BB84Protocol(n_bits=100, save_results=False)
        
        # Test 1: Basic protocol
        print("\n1. Testing basic protocol...")
        result_basic = bb84.run_protocol(with_eve=False, 
                                        enable_error_correction=False,
                                        enable_privacy_amplification=False)
        print(f"   Basic QBER: {result_basic['qber']:.4f}")
        print(f"   Sifted key length: {result_basic['sifted_key_length']}")
        
        # Test 2: With error correction only
        print("\n2. Testing with error correction...")
        result_ec = bb84.run_protocol(with_eve=True,
                                     enable_error_correction=True,
                                     enable_privacy_amplification=False)
        print(f"   QBER: {result_ec['qber']:.4f}")
        print(f"   Errors corrected: {result_ec['error_correction_stats'].get('errors_corrected', 0)}")
        print(f"   Final key length: {result_ec['final_key_length']}")
        
        # Test 3: With privacy amplification only
        print("\n3. Testing with privacy amplification...")
        result_pa = bb84.run_protocol(with_eve=True,
                                     enable_error_correction=False,
                                     enable_privacy_amplification=True)
        print(f"   QBER: {result_pa['qber']:.4f}")
        print(f"   Compression ratio: {result_pa['privacy_amplification_stats'].get('key_compression_ratio', 0):.3f}")
        print(f"   Final key length: {result_pa['final_key_length']}")
        
        # Test 4: Complete protocol
        print("\n4. Testing complete protocol...")
        result_complete = bb84.run_protocol(with_eve=True,
                                           enable_error_correction=True,
                                           enable_privacy_amplification=True)
        print(f"   QBER: {result_complete['qber']:.4f}")
        print(f"   Errors corrected: {result_complete['error_correction_stats'].get('errors_corrected', 0)}")
        print(f"   Compression ratio: {result_complete['privacy_amplification_stats'].get('key_compression_ratio', 0):.3f}")
        print(f"   Final key length: {result_complete['final_key_length']}")
        print(f"   Overall key rate: {result_complete['overall_key_rate']:.4f}")
        print(f"   Secure: {result_complete['secure']}")
        
        print("\n✓ All component tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Component testing failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Main function to run the enhanced demo"""
    print("="*60)
    print("BB84 PROJECT DEMO - WITH ERROR CORRECTION & PRIVACY AMPLIFICATION")
    print("="*60)
    
    # Test imports first
    success, BB84Analysis, BB84Protocol = debug_imports()
    if not success:
        print("\n❌ Import test failed. Please check your installation and file paths.")
        return
    
    # Run quick test
    if not quick_test(BB84Protocol):
        print("\n❌ Quick test failed. Aborting demo.")
        return
    
    # Ask user what they want to run
    print("\n" + "="*60)
    print("DEMO OPTIONS:")
    print("="*60)
    print("1. Quick Demo           - Simple demonstration with new features")
    print("2. Full Analysis        - Comprehensive analysis including new features")
    print("3. Component Testing    - Test individual protocol components")
    print("4. All Demos            - Run all demonstrations")
    print("5. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            quick_demo(BB84Protocol)
            break
        elif choice == '2':
            full_analysis(BB84Analysis)
            break
        elif choice == '3':
            test_protocol_components(BB84Protocol)
            break
        elif choice == '4':
            quick_demo(BB84Protocol)
            print("\n" + "-"*60)
            print("PROCEEDING TO COMPONENT TESTING...")
            print("-"*60)
            test_protocol_components(BB84Protocol)
            print("\n" + "-"*60)
            print("PROCEEDING TO FULL ANALYSIS...")
            print("-"*60)
            full_analysis(BB84Analysis)
            break
        elif choice == '5':
            print("Exiting demo. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3, 4, or 5.")
    
    print("\n" + "="*60)
    print("DEMO COMPLETE!")
    print("="*60)
    print("Check the results/ directory for generated files:")
    print("• figures/ - Plots and visualizations")
    print("• data/    - CSV files and detailed results")
    print("\nNew files with error correction and privacy amplification:")
    print("• bb84_error_correction_analysis_*.png")
    print("• bb84_privacy_amplification_analysis_*.png")
    print("• bb84_error_correction_data_*.csv")
    print("• bb84_privacy_amplification_data_*.csv")
    print("="*60)

if __name__ == "__main__":
    main()