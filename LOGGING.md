# Logging Guide

This document explains the logging system in the RISC-V simulator.

## Overview

The simulator provides two logging modes:
- **Standard Mode**: Minimal output, basic statistics
- **Verbose Mode**: Detailed cycle-by-cycle execution logs

All logs are written to `run.log` file, and in verbose mode, also displayed on console.

---

## Logging Configuration

### Enabling Logging

When you run `python main.py`, you'll be prompted:

```
Enable detailed logging?
  (Logs execution details to run.log and console)
Enable verbose mode? (y/n):
```

- Type `y` or `yes` for verbose mode
- Type `n` or `no` for standard mode

### Log Levels

The simulator uses Python's standard logging framework with these levels:

- **DEBUG**: Detailed execution flow (function calls, state changes)
- **INFO**: Cycle information, major events
- **WARNING**: Potential issues (misaligned memory access)
- **ERROR**: Execution errors

---

## Standard Mode Output

Typical console output in standard mode:

```
============================================================
Running: FIBONACCI
============================================================
* Creating core instance...
  Single Cycle Model initialized
* Loading binary into memory...
  Loaded 236 bytes
* Starting simulation (max 200 cycles)...

Simulation complete.
  Executed 140 cycles in 0.0234s
  Performance: 5983 cycles/sec

============================================================
Final Register Values
============================================================
  x1  =         55 (0x00000037)
  x2  =         89 (0x00000059)
  ...
============================================================
```

The `run.log` file will contain basic execution info.

---

## Verbose Mode Output

In verbose mode, you get additional details:

```
============================================================
Running: FIBONACCI
============================================================
* Creating core instance...
  Pipelined Model initialized
* Loading binary into memory...
  Loaded 236 bytes
* Starting simulation (max 200 cycles)...
  Verbose logging enabled - check run.log for details

INFO    : **** Simulation started ****
INFO    : **** Cycle 0 ****
INFO    : PC = 0x00000000
INFO    : IR = 0x00400093
INFO    : **** Cycle 1 ****
...

Simulation complete.
  Executed 140 cycles in 0.0456s
  Performance: 3070 cycles/sec
  Logs written to: run.log
```

---

## Log File Format

### Standard Mode Log

```
[22:14:32] INFO     pyv: **** Simulation started on Wednesday, Dec 18, 2024 at 22:14:32 ****
```

### Verbose Mode Log

```
[22:14:32] INFO     pyv: **** Simulation started on Wednesday, Dec 18, 2024 at 22:14:32 ****

[22:14:32] INFO     pyv: **** Cycle 0 ****
[22:14:32] DEBUG    pyv: Running IFStage.propagate
[22:14:32] DEBUG    pyv: Running IDStage.propagate
[22:14:32] DEBUG    pyv: Running EXStage.propagate
[22:14:32] DEBUG    pyv: Running MEMStage.propagate
[22:14:32] DEBUG    pyv: Running WBStage.propagate

[22:14:32] INFO     pyv: **** Cycle 1 ****
[22:14:32] DEBUG    pyv: Running IFStage.propagate
...
```

---

## What Gets Logged

### Always Logged (Standard and Verbose)

1. **Simulation Start**: Timestamp and configuration
2. **Cycle Count**: Total cycles executed
3. **Warnings**: Memory alignment issues, illegal instructions
4. **Errors**: Execution failures

### Verbose Mode Only

1. **Cycle Information**: Start of each cycle
2. **Stage Execution**: Each pipeline stage propagation
3. **Register Updates**: Register file writes
4. **Memory Access**: Load/store operations
5. **Branch Decisions**: Branch taken/not taken
6. **Pipeline Events**: Stalls, flushes, hazards

---

## Debugging with Logs

### Finding Issues

1. **Check Cycle Count**: Did the program execute expected number of cycles?
2. **Look for Warnings**: Misaligned access can cause incorrect behavior
3. **Trace PC Values**: Follow program counter to see execution flow
4. **Check Register Updates**: Verify calculations are correct

### Example: Debugging a Loop

If a loop runs forever:

1. Enable verbose mode
2. Look for PC values in the log
3. Find the loop branch instruction
4. Check if branch condition is being met
5. Verify loop counter register is being updated

### Example: Memory Issues

If data is not being loaded correctly:

1. Enable verbose mode
2. Search log for memory address: `grep "0x00001000" run.log`
3. Check if store happened before load
4. Verify alignment (addresses should be word-aligned for word access)

---

## Performance Impact

- **Standard Mode**: Minimal overhead (<5%)
- **Verbose Mode**: Significant overhead (2-3x slower)
  - Use for debugging specific issues
  - Not recommended for long simulations
  - Logs can become very large (MB per thousand cycles)

---

## Tips

1. **Start with Standard Mode**: Get baseline performance
2. **Use Verbose for Debugging**: When something doesn't work
3. **Check Log Size**: Large logs can fill disk space
4. **Search Logs**: Use `grep` or text editor search
5. **Compare Logs**: Diff logs from working vs broken versions

---

## Log File Location

The log file is always created in the project root directory:
```
ca-project/run.log
```

It is overwritten each time you run the simulator.

To keep multiple logs:
```bash
# Rename log after each run
python main.py
mv run.log fibonacci_run1.log

python main.py
mv run.log fibonacci_run2.log
```

---

## Programmatic Access

You can also configure logging programmatically:

```python
from pyv.log import enable_logging

# Enable verbose logging
enable_logging(verbose=True, log_file="my_simulation.log")

# Then run your simulation
core = SingleCycleModel()
core.load_binary("programs/fibonacci/fibonacci.bin")
core.run(1000)
```

---

## Troubleshooting

**Q: Log file is empty**
- Make sure logging is enabled
- Check that simulation actually ran

**Q: Too much output**
- Use standard mode instead of verbose
- Reduce number of cycles

**Q: Can't find specific instruction**
- Search for PC value: `grep "PC = 0x00000010" run.log`
- Or search for cycle: `grep "Cycle 42" run.log`

**Q: Log file is huge**
- Verbose mode generates lots of data
- Consider running fewer cycles for debugging
- Delete old logs: `rm run.log`
