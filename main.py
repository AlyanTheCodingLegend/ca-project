import time
import os
import subprocess
from pyv.models.model import Model
from pyv.models.singlecycle import SingleCycleModel
from pyv.models.pipelined import PipelinedModel
from pyv.log import enable_logging


def execute_bin(
        core_type: str,
        program_name: str,
        path_to_bin: str,
        num_cycles: int,
        verbose: bool = False) -> Model:
    print("\n" + "=" * 60)
    print(f"Running: {program_name}")
    print("=" * 60)

    # Create core instance
    print("* Creating core instance...")
    if core_type == 'single':
        core = SingleCycleModel()
        print(f"  Single Cycle Model initialized")
    elif core_type == 'pipelined':
        core = PipelinedModel(verbose=verbose)
        print(f"  Pipelined Model initialized")
    else:
        raise ValueError(f"Unknown core type: {core_type}")

    # Load binary into memory
    print("* Loading binary into memory...")
    file_size = os.path.getsize(path_to_bin)
    core.load_binary(path_to_bin)
    print(f"  Loaded {file_size} bytes")

    # Set probes
    core.set_probes([])

    # Simulate
    print(f"* Starting simulation (max {num_cycles} cycles)...")
    if verbose:
        print("  Verbose logging enabled - check run.log for details")
    print()

    start = time.perf_counter()
    core.run(num_cycles)
    end = time.perf_counter()

    print(f"\nSimulation complete.")
    print(f"  Executed {core.get_cycles()} cycles in {end - start:.4f}s")
    print(f"  Performance: {core.get_cycles() / (end - start):.0f} cycles/sec")
    if verbose:
        print(f"  Logs written to: run.log")
    print()

    return core


def loop_acc():
    core_type = 'single'
    program_name = 'LOOP_ACC'
    path_to_bin = 'programs/loop_acc/loop_acc.bin'
    num_cycles = 2010

    core = execute_bin(core_type, program_name, path_to_bin, num_cycles)

    # Print register and memory contents
    print("x1 = " + str(core.readReg(1)))
    print("x2 = " + str(core.readReg(2)))
    print("x5 = " + str(core.readReg(5)))
    print("pc = " + str(hex(core.readPC())))
    print("mem@4096 = ", core.readDataMem(4096, 4))
    print("")


def fibonacci():
    core_type = 'single'
    program_name = 'FIBONACCI'
    path_to_bin = 'programs/fibonacci/fibonacci.bin'
    num_cycles = 140

    core = execute_bin(core_type, program_name, path_to_bin, num_cycles)

    # Print result
    print("Result = ", core.readDataMem(2048, 4))
    print("")


def endless_loop():
    core_type = 'single'
    program_name = 'ENDLESS_LOOP'
    path_to_bin = 'programs/endless_loop/endless_loop.bin'
    num_cycles = 1000

    execute_bin(core_type, program_name, path_to_bin, num_cycles)


def get_toolchain_path():
    """Get the path to the RISC-V toolchain binaries.

    Returns:
        Tuple of (toolchain_bin_path, prefix) or (None, prefix) if using system PATH
    """
    import platform

    # Check for local toolchain
    local_toolchain = os.path.join("riscv-toolchain", "xpack-riscv-none-elf-gcc-12.2.0-3", "bin")

    if os.path.exists(local_toolchain):
        return local_toolchain, "riscv-none-elf-"

    # Fall back to system PATH with common prefixes
    return None, "riscv-none-elf-"  # Try riscv-none-elf first, then riscv64-unknown-elf


def compile_program(program_name: str) -> str:
    """Compile a RISC-V assembly/C file to binary using the toolchain.

    Args:
        program_name: Name of the program (without extension)

    Returns:
        Path to the compiled binary file
    """
    program_dir = os.path.join('programs', program_name)

    # Check if program directory exists
    if not os.path.exists(program_dir):
        raise FileNotFoundError(f"Program directory not found: {program_dir}")

    # Look for source file (.S or .c)
    asm_file = os.path.join(program_dir, f"{program_name}.S")
    c_file = os.path.join(program_dir, f"{program_name}.c")

    if os.path.exists(asm_file):
        source_file = asm_file
    elif os.path.exists(c_file):
        source_file = c_file
    else:
        raise FileNotFoundError(f"No .S or .c file found for program: {program_name}")

    # Output files
    out_file = os.path.join(program_dir, f"{program_name}.out")
    bin_file = os.path.join(program_dir, f"{program_name}.bin")

    print(f"* Compiling {os.path.basename(source_file)}...")

    # Get toolchain path
    toolchain_bin, riscv_prefix = get_toolchain_path()

    # RISC-V toolchain configuration
    gcc_opts = ["-march=rv32i", "-mabi=ilp32", "-nostdlib", "-nostartfiles", "programs/common/crt.S"]

    # Build command paths
    if toolchain_bin:
        gcc_path = os.path.join(toolchain_bin, f"{riscv_prefix}gcc")
        objcopy_path = os.path.join(toolchain_bin, f"{riscv_prefix}objcopy")
        # Add .exe extension on Windows
        if os.name == 'nt':
            gcc_path += ".exe"
            objcopy_path += ".exe"
        print(f"  Using local toolchain")
    else:
        gcc_path = f"{riscv_prefix}gcc"
        objcopy_path = f"{riscv_prefix}objcopy"
        print(f"  Using system toolchain")

    try:
        # Compile source to executable
        gcc_cmd = [gcc_path] + gcc_opts + [source_file, "-o", out_file]
        subprocess.run(gcc_cmd, check=True, capture_output=True)

        # Convert to binary
        objcopy_cmd = [objcopy_path, "-O", "binary", out_file, bin_file]
        subprocess.run(objcopy_cmd, check=True, capture_output=True)

        print(f"* Compilation successful: {bin_file}")
        return bin_file

    except subprocess.CalledProcessError as e:
        print(f"Error during compilation: {e}")
        if e.stderr:
            print(e.stderr.decode())
        raise
    except FileNotFoundError:
        print(f"\n{'='*60}")
        print(f"Error: RISC-V toolchain not found!")
        print(f"{'='*60}")
        print(f"\nPlease run the setup script to install the toolchain:")
        print(f"  python setup_toolchain.py")
        print(f"\nOr install it manually from:")
        print(f"  https://github.com/xpack-dev-tools/riscv-none-elf-gcc-xpack/releases")
        print(f"{'='*60}\n")
        raise


def main():
    print("=" * 60)
    print("RISC-V Simulator")
    print("=" * 60)

    # Ask for model type
    print("\nSelect CPU model:")
    print("1. Single Cycle")
    print("2. Pipelined")

    while True:
        choice = input("\nEnter choice (1 or 2): ").strip()
        if choice == '1':
            core_type = 'single'
            print("Selected: Single Cycle Model")
            break
        elif choice == '2':
            core_type = 'pipelined'
            print("Selected: Pipelined Model")
            break
        else:
            print("Invalid choice. Please enter 1 or 2.")

    # Ask for verbose logging
    print("\nEnable detailed logging?")
    print("  (Logs execution details to run.log and console)")
    while True:
        verbose_choice = input("Enable verbose mode? (y/n): ").strip().lower()
        if verbose_choice in ['y', 'yes']:
            verbose = True
            print("Verbose logging enabled")
            break
        elif verbose_choice in ['n', 'no']:
            verbose = False
            print("Standard mode (minimal logging)")
            break
        else:
            print("Invalid choice. Please enter y or n.")

    # Enable logging system
    enable_logging(verbose=verbose, log_file="run.log")

    # Ask for program name
    print("\nAvailable programs in /programs folder:")
    programs_dir = 'programs'
    available_programs = [d for d in os.listdir(programs_dir)
                         if os.path.isdir(os.path.join(programs_dir, d)) and d != 'common']

    for i, prog in enumerate(available_programs, 1):
        print(f"  {i}. {prog}")

    program_name = input("\nEnter program name: ").strip()

    # Ask for number of cycles
    while True:
        try:
            num_cycles = int(input("Enter maximum number of cycles to simulate (e.g., 1000): ").strip())
            if num_cycles > 0:
                break
            else:
                print("Please enter a positive number.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    try:
        # Compile the program
        bin_file = compile_program(program_name)

        # Execute the binary
        core = execute_bin(core_type, program_name.upper(), bin_file, num_cycles, verbose)

        # Print final register values
        print("=" * 60)
        print("Final Register Values")
        print("=" * 60)
        for i in range(1, 11):
            value = core.readReg(i)
            print(f"  x{i:<2} = {value:10} (0x{value:08X})")
        pc_value = core.readPC()
        print(f"  pc  = {pc_value:10} (0x{pc_value:08X})")
        print("=" * 60)

        print("\nNote: Use core.readDataMem(address, num_bytes) to inspect memory")

    except Exception as e:
        print(f"\n{'='*60}")
        print(f"Error: {e}")
        print("="*60)
        return 1

    print("\nSimulation finished successfully.")
    return 0


if __name__ == '__main__':
    exit(main())
