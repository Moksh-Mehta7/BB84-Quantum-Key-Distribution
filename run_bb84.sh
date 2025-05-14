#!/bin/bash

# BB84 Quantum Key Distribution - Complete Docker Runner
# Single script for building, testing, and running the entire project

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Banner
echo "=================================================="
echo "🔬 BB84 Quantum Key Distribution Protocol 🔬"
echo "=================================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed! Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

print_status "Docker found"

# Function to validate required files
validate_files() {
    print_info "Validating project files..."
    
    required_files=(
        "Dockerfile"
        "requirements.txt"
        "src/bb84_protocol.py"
        "src/analysis.py"
        "experiments/demo.py"
    )
    
    for file in "${required_files[@]}"; do
        if [ -f "$file" ]; then
            print_status "Found: $file"
        else
            print_error "Missing required file: $file"
            exit 1
        fi
    done
    
    print_status "All required files present"
}

# Function to build Docker image
build_image() {
    print_info "Building Docker image..."
    
    if docker build -t bb84-project . > docker_build.log 2>&1; then
        print_status "Docker image built successfully"
        rm docker_build.log
    else
        print_error "Docker build failed! Check docker_build.log for details"
        exit 1
    fi
}

# Function to test imports
test_imports() {
    print_info "Testing Python imports..."
    
    if docker run --rm bb84-project python -c "
import sys
sys.path.append('/app/src')
try:
    from bb84_protocol import BB84Protocol
    from analysis import BB84Analysis
    print('All imports successful')
except Exception as e:
    print(f'Import failed: {e}')
    exit(1)
" > /dev/null 2>&1; then
        print_status "All imports working correctly"
    else
        print_error "Import test failed"
        exit 1
    fi
}

# Function to create results directory
create_results_dir() {
    print_info "Setting up results directory..."
    mkdir -p results/figures results/data results/logs
    print_status "Results directory ready"
}

# Function to run specific analysis
run_analysis() {
    local choice=$1
    
    case $choice in
        "1"|"quick")
            print_info "Running Quick Demo..."
            docker run -it --rm \
              -v $(pwd)/results:/app/results \
              -e MPLBACKEND=Agg \
              bb84-project python -c "
import sys; sys.path.append('/app/src')
from experiments.demo import *
success, BB84Analysis, BB84Protocol = debug_imports()
if success: quick_demo(BB84Protocol)
else: exit(1)
"
            ;;
        "2"|"full")
            print_info "Running Full Analysis..."
            docker run -it --rm \
              -v $(pwd)/results:/app/results \
              -e MPLBACKEND=Agg \
              bb84-project python -c "
import sys; sys.path.append('/app/src')
from experiments.demo import *
success, BB84Analysis, BB84Protocol = debug_imports()
if success: full_analysis(BB84Analysis)
else: exit(1)
"
            ;;
        "3"|"components")
            print_info "Running Component Testing..."
            docker run -it --rm \
              -v $(pwd)/results:/app/results \
              -e MPLBACKEND=Agg \
              bb84-project python -c "
import sys; sys.path.append('/app/src')
from experiments.demo import *
success, BB84Analysis, BB84Protocol = debug_imports()
if success: test_protocol_components(BB84Protocol)
else: exit(1)
"
            ;;
        "4"|"all")
            print_info "Running All Demonstrations..."
            docker run -it --rm \
              -v $(pwd)/results:/app/results \
              -e MPLBACKEND=Agg \
              bb84-project python experiments/demo.py
            ;;
        "5"|"shell")
            print_info "Starting interactive shell..."
            docker run -it --rm \
              -v $(pwd)/results:/app/results \
              -e MPLBACKEND=Agg \
              bb84-project bash
            ;;
        *)
            print_error "Invalid choice!"
            exit 1
            ;;
    esac
}

# Function to show results
show_results() {
    print_info "Analysis Results:"
    echo ""
    
    if [ -d "results/figures" ] && [ "$(ls -A results/figures)" ]; then
        print_status "Generated plots in results/figures/:"
        ls -la results/figures/ | grep -E '\.(png|pdf)$' | awk '{print "  📊 " $9}'
    fi
    
    if [ -d "results/data" ] && [ "$(ls -A results/data)" ]; then
        print_status "Data files in results/data/:"
        ls -la results/data/ | grep -E '\.(csv|json|txt)$' | awk '{print "  📁 " $9}'
    fi
    
    echo ""
    print_status "All results saved in the 'results/' directory"
}

# Main menu function
show_menu() {
    echo ""
    echo "What would you like to do?"
    echo "1) Quick Demo (basic eavesdropping comparison)"
    echo "2) Full Analysis (comprehensive analysis with all features)"
    echo "3) Component Testing (test individual protocol components)"
    echo "4) All Demonstrations (run complete demo script)"
    echo "5) Interactive Shell (for manual exploration)"
    echo "6) Exit"
    echo ""
}

# Parse command line arguments
if [ $# -gt 0 ]; then
    case $1 in
        "-h"|"--help")
            echo "Usage: $0 [option]"
            echo ""
            echo "Options:"
            echo "  quick, 1       Run quick demo"
            echo "  full, 2        Run full analysis"
            echo "  components, 3  Run component testing"
            echo "  all, 4         Run all demonstrations"
            echo "  shell, 5       Open interactive shell"
            echo "  -h, --help     Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 quick       # Run quick demo"
            echo "  $0 full        # Run full analysis"
            echo "  $0             # Show interactive menu"
            exit 0
            ;;
        "quick"|"full"|"components"|"all"|"shell"|"1"|"2"|"3"|"4"|"5")
            AUTO_RUN=$1
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use '$0 --help' for usage information"
            exit 1
            ;;
    esac
fi

# Main execution
echo ""
print_info "Starting BB84 Project Setup..."

# Validate, build, and test
validate_files
build_image
test_imports
create_results_dir

# Run analysis
if [ -n "$AUTO_RUN" ]; then
    # Automatic mode from command line
    run_analysis "$AUTO_RUN"
    show_results
    print_status "BB84 Analysis Complete!"
else
    # Interactive mode
    while true; do
        show_menu
        read -p "Enter your choice (1-6): " choice
        
        case $choice in
            6)
                print_info "Goodbye!"
                exit 0
                ;;
            1|2|3|4|5)
                echo ""
                run_analysis "$choice"
                show_results
                
                echo ""
                read -p "Press Enter to continue or 'q' to quit: " continue_choice
                if [ "$continue_choice" = "q" ]; then
                    print_info "Goodbye!"
                    exit 0
                fi
                ;;
            *)
                print_warning "Invalid choice! Please enter 1-6."
                ;;
        esac
    done
fi