# BB84 Quantum Key Distribution Protocol Analysis

## Project Overview

This project implements and analyzes the BB84 quantum key distribution protocol with comprehensive security analysis and practical enhancements. The implementation includes:

- **Complete BB84 Protocol**: Full implementation with quantum state preparation, measurement, and basis reconciliation
- **Eavesdropping Detection**: Simulation of intercept-resend attacks and QBER analysis
- **Error Correction**: Implementation of parity-check error correction algorithms
- **Privacy Amplification**: Universal hash functions for key compression and security enhancement
- **Performance Analysis**: Comprehensive statistical analysis across multiple scenarios
- **Visualization**: Detailed plots and reports for all aspects of the protocol

## Team Members

- **Moksh Mehta** (s4826878)
- **Iresha Piyatissa** (s4833717)
- **Alen Siby** (S4851488)
- **Neah Sunny** (S4851587)

## AI Assistance Disclosure

**Note**: AI was used to assist with code debugging, optimization, and implementation guidance throughout this project. All core concepts, algorithm design, and analysis methodology were developed by the team members.


## Prerequisites

**Docker** is required to run this project.

### Installation

Download Docker from: https://docs.docker.com/get-docker/

#### Quick Install Commands:

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install docker.io
sudo systemctl start docker
sudo systemctl enable docker
```

**CentOS/RHEL:**
```bash
sudo yum install docker
sudo systemctl start docker
sudo systemctl enable docker
```

**Windows/macOS:**
Install Docker Desktop from the link above.

### Verify Installation
```bash
docker --version
```

## Features

### Core Protocol Implementation
- ✅ **Quantum State Preparation**: Alice prepares qubits in Z and X bases
- ✅ **Quantum Measurement**: Bob's random basis measurements with Qiskit simulation
- ✅ **Basis Reconciliation**: Public comparison and key sifting
- ✅ **QBER Calculation**: Quantum bit error rate estimation

### Security Analysis
- ✅ **Eavesdropping Simulation**: Intercept-resend attack implementation
- ✅ **Security Threshold**: Detection based on 11% QBER threshold
- ✅ **Statistical Testing**: Comprehensive analysis with confidence intervals

### Enhanced Features
- ✅ **Error Correction**: Adaptive parity-check algorithm
- ✅ **Privacy Amplification**: SHA-256 based universal hashing
- ✅ **Complete Key Rate Analysis**: From initial transmission to final secure key
- ✅ **Docker Support**: Full containerization for reproducible results

## Installation

### Option 1: Docker (Recommended)
```bash
cd bb84-project

# Run with Docker (automatically builds and runs)
./run_bb84.sh
```

### Option 2: Local Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Run the demo
python experiments/demo.py
```

## Usage

### Quick Start with Docker
```bash
# Interactive menu
./run_bb84.sh

# Quick demo
./run_bb84.sh quick

# Full analysis
./run_bb84.sh full

# Component testing
./run_bb84.sh components

# All demonstrations
./run_bb84.sh all
```

### Manual Execution
```bash
# Quick demo
python experiments/demo.py

# Full analysis
python src/analysis.py
```

## Project Structure

```
bb84-project/
├── src/                          # Core implementation
│   ├── bb84_protocol.py         # Main BB84 protocol with enhancements
│   └── analysis.py              # Comprehensive analysis suite
├── experiments/                  # Demonstrations and testing
│   └── demo.py                  # Interactive demo script
├── results/                     # Generated outputs
│   ├── figures/                 # Plots and visualizations
│   ├── data/                    # CSV files and raw data
│   └── logs/                    # Execution logs
├── Dockerfile                   # Container configuration
├── run_bb84.sh                  # Automated runner script
└── requirements.txt             # Python dependencies
```

## Analysis Components

### 1. Eavesdropping Analysis
- **No Eavesdropping**: Baseline performance measurement
- **Intercept-Resend Attack**: Security analysis under attack
- **QBER Comparison**: Statistical analysis of error rates
- **Security Assessment**: Threshold-based security evaluation

### 2. Error Correction Analysis
- **Parity Check Algorithm**: Adaptive block size based on QBER
- **Error Detection Rate**: Performance under various noise levels
- **Key Length Impact**: Before and after error correction comparison

### 3. Privacy Amplification Analysis
- **Key Compression**: Universal hash function implementation
- **Security Parameter**: Information-theoretic security analysis
- **QBER vs Compression**: Analysis of trade-offs

### 4. Performance Metrics
- **Key Rates**: Sifting rate and overall key generation rate
- **Statistical Significance**: T-tests and confidence intervals
- **Effect Size Analysis**: Cohen's d calculations

## Key Results

### Security Performance
- **Detection Rate**: 100% for QBER > 11% threshold
- **False Positive Rate**: Near 0% in ideal conditions
- **Key Rate**: ~50% sifting rate as expected

### Error Correction Impact
- **Error Reduction**: Significant improvement in noisy conditions
- **Key Length Preservation**: Minimized loss through adaptive algorithms
- **Security Enhancement**: Maintains security while correcting errors

### Privacy Amplification Benefits
- **Information-Theoretic Security**: Provable security against quantum attacks
- **Flexible Compression**: Adapts to channel noise levels
- **Practical Implementation**: Efficient hash-based approach

## Dependencies

- **Qiskit**: Quantum circuit simulation
- **NumPy**: Numerical computations
- **Matplotlib**: Visualization
- **Pandas**: Data analysis
- **SciPy**: Statistical testing
- **Python 3.8+**: Core language

## Output Files

The analysis generates several types of output:

### Visualizations (`results/figures/`)
- `bb84_eavesdropping_analysis_*.png`: Complete eavesdropping impact analysis
- `bb84_key_length_analysis_*.png`: Key length effect analysis
- `bb84_error_correction_analysis_*.png`: Error correction impact
- `bb84_privacy_amplification_analysis_*.png`: Privacy amplification analysis
- `bb84_complete_demo.png`: Quick demo visualization

### Data Files (`results/data/`)
- `bb84_eavesdropping_data_*.csv`: Raw eavesdropping analysis data
- `bb84_error_correction_data_*.csv`: Error correction performance data
- `bb84_privacy_amplification_data_*.csv`: Privacy amplification metrics
- `bb84_statistical_analysis_*.json`: Complete statistical results
- `bb84_summary_report_*.txt`: Human-readable summary report

## Technical Details

### Protocol Implementation
- **Quantum Simulation**: Uses Qiskit AerSimulator for accurate quantum behavior
- **Random Number Generation**: Cryptographically secure random basis selection
- **Error Modeling**: Realistic noise simulation and error introduction

### Error Correction Algorithm
```python
# Adaptive block size based on QBER
block_size = max(4, int(16 / max(qber, 0.01)))
```

### Privacy Amplification
```python
# Security parameter calculation
security_parameter = max(10, int(0.1 * len(key)))
secure_length = len(key) - eve_info_estimate - security_parameter
```

## Future Enhancements

- **Advanced Error Correction**: LDPC codes, Turbo codes
- **Device-Independent QKD**: Protocol modifications for device independence
- **Continuous Variable QKD**: Extension to CV-QKD protocols
- **Real Hardware Integration**: Connection to actual quantum devices
- **Advanced Attack Models**: Collective and coherent attacks

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Submit a pull request

## License

This project is developed for educational purposes only.

## Acknowledgments

- **Qiskit Team**: For the excellent quantum computing framework
- **BB84 Creators**: Bennett and Brassard for the foundational protocol
- **AI Assistance**: Claude (Anthropic) and Chatgpt was used for code debugging, optimization, and implementation guidance

## Contact

For questions or issues, please contact any of the team members listed above.

---

*This implementation demonstrates the practical aspects of quantum key distribution and provides a foundation for understanding real-world QKD systems.*
