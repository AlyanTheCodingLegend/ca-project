# RISC-V Instruction-Level Cycle Accurate Simulator

**Course:** Computer Architecture
**Class:** BSCS-13B
**Group:** 1

## Team Members

- Alyan Ahmed Memon - 469355 (Team Representative)
- Muhammad Abdullah Waqar - 458785
- Uswa Khan - 454092
- Muhammad Rayyan Faisal - 475207

---

## Project Overview

Py-V is a cycle-accurate RISC-V CPU simulator implemented in Python for educational purposes. It features both single-cycle and pipelined execution models, complete RV32I instruction set support, and comprehensive hazard detection mechanisms.

### Key Features

- **Two Execution Models:**
  - Single-cycle: Classic 5-stage RISC CPU (1 instruction/cycle)
  - Pipelined: 5-stage pipeline with hazard detection

- **Complete RV32I Support:**
  - Arithmetic, logical, shifts, comparisons
  - Branches, jumps, loads, stores
  - System instructions and CSRs

- **Educational Features:**
  - Cycle-by-cycle execution visibility
  - Pipeline stage monitoring
  - Hazard detection demonstration
  - Register and memory inspection

---

## Quick Start

### Prerequisites

- Python 3.8+
- RISC-V GNU toolchain (for compiling programs)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd ca-project

# Install dependencies (optional, only standard library used)
pip install -r requirements.txt
```

### Running the Simulator

```bash
# Run with default test programs
python main.py
```

Expected output:
```
===== LOOP_ACC =====
* Creating core instance...
* Loading binary...
* Starting simulation...

Sim done at cycle 2010 after 0.17s.

x1 = 1000
x2 = 1000
pc = 0x20
mem@4096 = ['0xe8', '0x3', '0x0', '0x0']
```

---

## Project Structure

```
ca-project/
├── pyv/                    # Simulator source code
│   ├── models/             # CPU models (single-cycle, pipelined)
│   ├── stages.py           # Pipeline stages (IF, ID, EX, MEM, WB)
│   ├── simulator.py        # Simulation engine
│   ├── hazard.py           # Hazard detection unit
│   ├── reg.py              # Register file
│   ├── mem.py              # Memory system
│   └── ...                 # Other modules
│
├── programs/               # Test programs
│   ├── fibonacci/          # Fibonacci calculation
│   ├── loop_acc/           # Loop accumulator
│   └── endless_loop/       # Infinite loop test
│
├── main.py                 # Main entry point
│
└── report_diagrams/        # Architecture diagrams
```

---

## Test Programs

### 1. Fibonacci
- Calculates F(10) = 55
- Stored at memory[2048]
- ~140 cycles

### 2. Loop Accumulator
- Counts from 0 to 1000
- Stored at memory[4096]
- ~2010 cycles

### 3. Endless Loop
- Tests infinite loop handling
- Runs until cycle limit

---

## Architecture

### Pipeline Stages

```
IF (Fetch) → ID (Decode) → EX (Execute) → MEM (Memory) → WB (Write-Back)
```

### Key Components

- **Program Counter (PC):** Tracks current instruction
- **Register File:** 32 x 32-bit general-purpose registers
- **Memory:** Unified 8 KiB instruction/data memory
- **Hazard Detection Unit:** Detects and resolves pipeline hazards
- **Control Units:** Branch, CSR, Exception handling

---

## Documentation

- **Project Report:** `BSCS-13B_Gp1_RISC-V_Simulator_Report.docx`
- **Screenshot Guide:** `screenshot_guide_condensed.md`
- **Architecture Diagrams:** `report_diagrams/`

---

## License

Educational project for Computer Architecture course.

---

## Contact

For questions or issues, contact the team representative:
**Alyan Ahmed Memon** - 469355
