# RISC-V Instruction-Level Cycle Accurate Simulator

**Course:** Computer Architecture
**Class:** BSCS-13B
**Group:** 1

## Team Members

- Alyan Ahmed Memon - 469355
- Muhammad Abdullah Waqar - 458785 (Team Representative)
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
- No other dependencies required! (RISC-V toolchain is set up automatically)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd ca-project

# Install RISC-V toolchain (one-time setup)
python setup_toolchain.py
```

The setup script will automatically:
- Detect your operating system (Windows/Linux/macOS)
- Download the appropriate RISC-V toolchain
- Extract and configure it in the `riscv-toolchain/` folder
- No manual PATH configuration needed!

### Running the Simulator

```bash
# Run the interactive simulator
python main.py
```

The simulator will ask you to:
1. Choose CPU model (Single Cycle or Pipelined)
2. Enable verbose logging (optional - logs detailed execution to run.log)
3. Enter program name (e.g., `fibonacci`, `loop_acc`, `endless_loop`)
4. Specify number of cycles to simulate


### Graphical UI (minimal viewer)

A simple Tkinter-based GUI is available to visualize the pipelined model and step through cycles.

```bash
# Launch the GUI
python gui.py
```

Features:
- Compile & load a program from `programs/`
- Step single cycles or run continuously
- View PC, pipeline registers and first 16 registers

Note: This is a lightweight educational viewer - use the `--verbose` mode with the console for detailed tracing.
Example session:
```
============================================================
RISC-V Simulator
============================================================

Select CPU model:
1. Single Cycle
2. Pipelined

Enter choice (1 or 2): 1
Selected: Single Cycle Model

Enable detailed logging?
  (Logs execution details to run.log and console)
Enable verbose mode? (y/n): n
Standard mode (minimal logging)

Available programs in /programs folder:
  1. endless_loop
  2. fibonacci
  3. loop_acc

Enter program name: fibonacci
Enter maximum number of cycles to simulate (e.g., 1000): 200

* Compiling programs/fibonacci/fibonacci.c...
* Using local toolchain: riscv-toolchain/xpack-riscv-none-elf-gcc-12.2.0-3/bin
* Compilation successful: programs/fibonacci/fibonacci.bin

===== FIBONACCI =====
* Creating core instance...
* Loading binary...
* Starting simulation...

Sim done at cycle 140 after 0.02s.

Register values:
x1 = 55
x2 = 89
...
pc = 0x50
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

### Adding Your Own Programs

To add a custom RISC-V program:

1. Create a new folder in `programs/`:
   ```bash
   mkdir programs/my_program
   ```

2. Add your source file (`.S` assembly or `.c` C file):
   ```bash
   # For assembly
   programs/my_program/my_program.S

   # Or for C
   programs/my_program/my_program.c
   ```

3. Run the simulator and enter your program name:
   ```bash
   python main.py
   # When prompted, enter: my_program
   ```

The simulator will automatically compile and run your program!

---

## Logging and Debugging

The simulator includes a comprehensive logging system to help you understand program execution.

### Logging Modes

**Standard Mode (default)**:
- Minimal console output
- Basic execution info (cycles, performance)
- Logs written to `run.log` file
- Suitable for normal program execution

**Verbose Mode**:
- Detailed console output
- Cycle-by-cycle execution logs
- Port/signal changes
- Memory access warnings
- Useful for debugging and understanding CPU behavior

### Enabling Verbose Logging

When running the simulator, you'll be prompted:
```
Enable detailed logging?
  (Logs execution details to run.log and console)
Enable verbose mode? (y/n):
```

Choose 'y' for verbose mode or 'n' for standard mode.

### Log File Contents

The `run.log` file contains:
- Simulation start time
- Cycle-by-cycle execution (if verbose)
- Pipeline stage information
- Memory access patterns
- Warning messages (misaligned access, etc.)

Example log entry:
```
[12:34:56] INFO     pyv: **** Simulation started on Monday, Dec 18, 2023 at 12:34:56 ****

[12:34:56] INFO     pyv: **** Cycle 0 ****
[12:34:56] DEBUG    pyv: Running IFStage.propagate
[12:34:56] DEBUG    pyv: Running IDStage.propagate
...
```

### Inspecting Execution

After simulation completes, you can:
- View register values (printed automatically)
- Check program counter (PC)
- Inspect memory contents using `core.readDataMem(address, num_bytes)`

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

- **Installation Guide:** `INSTALL.md` - Setup instructions
- **Logging Guide:** `LOGGING.md` - Detailed logging documentation
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
