# Installation Guide

## Quick Setup (Recommended)

### Step 1: Clone the Repository
```bash
git clone https://github.com/AlyanTheCodingLegend/ca-project.git
cd ca-project
```

### Step 2: Run the Setup Script
```bash
python setup_toolchain.py
```

This will automatically:
- Detect your OS (Windows, Linux, or macOS)
- Download the RISC-V toolchain (~100MB)
- Extract and configure it
- No manual configuration needed!

### Step 3: Run the Simulator
```bash
python main.py
```

That's it! You're ready to simulate RISC-V programs.

---

## Platform-Specific Notes

### Windows
- Requires Python 3.8+
- Internet connection for initial toolchain download
- No additional dependencies

### Linux
- Requires Python 3.8+
- Internet connection for initial toolchain download
- May need to install `tar` and `gzip` (usually pre-installed)

### macOS
- Requires Python 3.8+
- Internet connection for initial toolchain download
- Works on both Intel and Apple Silicon (M1/M2/M3)

---

## Manual Installation (Alternative)

If you prefer to install the toolchain manually:

1. Download from: https://github.com/xpack-dev-tools/riscv-none-elf-gcc-xpack/releases
2. Choose version `12.2.0-3` for your platform
3. Extract to `riscv-toolchain/` in the project root
4. The simulator will automatically detect it

---

## Troubleshooting

### "Toolchain not found" error
- Run `python setup_toolchain.py` to download the toolchain
- Check that `riscv-toolchain/` folder exists
- Verify internet connection during setup

### Download fails
- Check your internet connection
- Try running the setup script again
- If persistent, download manually from the link above

### Compilation errors
- Ensure the toolchain is properly installed
- Check that your source files are in the correct format (.S or .c)
- Verify the `programs/common/crt.S` file exists

---

## Verifying Installation

To verify the toolchain is working:

```bash
# On Windows
.\riscv-toolchain\xpack-riscv-none-elf-gcc-12.2.0-3\bin\riscv-none-elf-gcc.exe --version

# On Linux/macOS
./riscv-toolchain/xpack-riscv-none-elf-gcc-12.2.0-3/bin/riscv-none-elf-gcc --version
```

You should see: `riscv-none-elf-gcc (xPack GNU RISC-V Embedded GCC x86_64) 12.2.0`

---

## Need Help?

- Check the README.md for usage examples
- Ensure Python 3.8+ is installed: `python --version`
- For issues, contact the team representative
