# Screenshot Guide - Condensed Report (3 Screenshots)

Quick guide for capturing the 3 screenshots needed for your 5-6 page report.

---

## Prerequisites

- Terminal/Command Prompt
- Code Editor (VS Code, PyCharm, etc.)
- Screen capture tool:
  - **Windows**: Win + Shift + S
  - **Mac**: Cmd + Shift + 4
  - **Linux**: Spectacle or Shutter

---

## Screenshot 1: Simulator Execution with Results

**Location in report:** Section 2 (after pipeline diagram)

**What to capture:** Terminal showing simulator running with cycle count and final results

### Steps:

1. Open terminal in project directory
2. Run the simulator:
   ```bash
   python main.py
   ```

3. Wait for execution to complete
4. Capture the terminal window showing:
   - Program names (LOOP_ACC, FIBONACCI, etc.)
   - "Sim done at cycle X" messages
   - Final register values
   - Memory contents

### Expected Output:
```
===== LOOP_ACC =====
* Creating core instance...
* Loading binary...
* Starting simulation...

Sim done at cycle 2010 after 0.172s.

x1 = 1000
x2 = 1000
pc = 0x20
mem@4096 = ['0xe8', '0x3', '0x0', '0x0']

===== FIBONACCI =====
...
Sim done at cycle 140 after 0.026s.
Result = ['0x37', '0x0', '0x0', '0x0']
```

### Tips:
- Make sure text is readable (12-14pt font)
- Capture complete output from all test programs
- Use dark terminal theme for better visibility (optional)

---

## Screenshot 2: Test Programs and Validation

**Location in report:** Section 4 (after requirements)

**What to capture:** Combined view showing tests passing

### Option A: pytest Results (Recommended)

1. Install pytest if not already: `pip install pytest`
2. Run tests with verbose output:
   ```bash
   pytest test/ -v
   ```

3. Capture showing:
   - Test file names (test_reg.py, test_mem.py, etc.)
   - PASSED markers (green checkmarks)
   - Final summary (X passed in Y.Ys)

### Expected Output:
```
test/test_clock.py::test_clock_tick PASSED
test/test_reg.py::test_register_write PASSED
test/test_mem.py::test_memory_read_write PASSED
test/test_stages.py::test_if_stage PASSED
...
========== 25 passed in 2.34s ==========
```

### Option B: All Programs Running Successfully

If pytest isn't working, capture the complete `python main.py` output showing all three test programs completing successfully.

### Tips:
- Show as many test results as possible in one screenshot
- Green PASSED text is good visual confirmation
- Make sure the summary line is visible

---

## Screenshot 3: Code Structure and Architecture

**Location in report:** Section 8 (after testing table)

**What to capture:** Code editor showing project organization

### Option A: File Explorer View (Easiest)

1. Open your code editor (VS Code, PyCharm, etc.)
2. Expand the `pyv/` directory in the file explorer
3. Show the modular structure:
   ```
   pyv/
   ├── __init__.py
   ├── clocked.py
   ├── csr.py
   ├── isa.py
   ├── mem.py
   ├── models/
   │   ├── singlecycle.py
   │   └── pipelined.py
   ├── reg.py
   ├── simulator.py
   ├── stages.py
   ├── hazard.py
   └── pipeline_regs.py
   ```

4. Capture the file explorer panel

### Option B: Module Connection Code

1. Open `pyv/models/singlecycle.py` in your editor
2. Navigate to lines 50-77 (the connection section)
3. Capture the code showing module connections:
   ```python
   # Connect stages
   self.if_stg.npc_i     << self.bu.npc_o
   self.id_stg.IFID_i    << self.if_stg.IFID_o
   self.ex_stg.IDEX_i    << self.id_stg.IDEX_o
   self.mem_stg.EXMEM_i  << self.ex_stg.EXMEM_o
   self.wb_stg.MEMWB_i   << self.mem_stg.MEMWB_o
   ```

### Option C: Directory Tree (Terminal)

**Windows:**
```cmd
tree /F pyv
```

**Linux/Mac:**
```bash
tree pyv
# or
ls -R pyv
```

Capture the tree output showing project structure.

### Tips:
- Choose the option that looks most professional
- File explorer view is usually cleanest
- Enable syntax highlighting if showing code
- Make sure folder names are readable

---

## Screenshot Quality Guidelines

### All Screenshots Should Have:
- ✅ High resolution (at least 1920x1080)
- ✅ Clear, readable text (12-14pt)
- ✅ Relevant content visible (no cut-off text)
- ✅ Professional appearance

### Terminal Screenshots:
- Font: Consolas, Courier New, or Monaco
- Theme: Dark (easier to read) or Light (better for print)
- Make window wide enough to avoid line wrapping

### Code Editor Screenshots:
- Font Size: 13-15pt
- Line Numbers: Enabled
- Syntax Highlighting: Enabled
- Theme: Your choice (Dark+ recommended)

---

## Quick Reference Card

| Screenshot | What to Show | How to Get It |
|------------|-------------|---------------|
| **1** | Simulator running with results | `python main.py` |
| **2** | Tests passing | `pytest test/ -v` |
| **3** | Code structure | Open file explorer in editor |

---

## Inserting into Word Document

1. Open the generated Word document:
   ```
   BSCS-13B_Gp1_RISC-V_Simulator_Report.docx
   ```

2. Find each `[INSERT SCREENSHOT X: ...]` marker

3. Click on the marker line

4. Go to: **Insert** → **Pictures** → **This Device**

5. Select your screenshot file

6. Resize if needed:
   - Right-click image → Size and Position
   - Set width to 6-6.5 inches
   - Keep aspect ratio locked

7. Center the image:
   - Select image
   - Home tab → Center align

8. Add caption (optional but recommended):
   - Right-click image → Insert Caption
   - "Figure X: [Description]"

---

## Troubleshooting

### Problem: Can't run main.py
**Solution:**
```bash
cd D:\Codes\ca-project
python main.py
```

### Problem: pytest not found
**Solution:**
```bash
pip install pytest
pytest test/ -v
```

### Problem: No tests directory
**Solution:**
Tests might not be set up yet. Use Option B for Screenshot 2 (just show main.py output).

### Problem: Screenshot too large for document
**Solution:**
- In Word: Right-click image → Size → Scale to 80%
- Or use image editor to reduce resolution before inserting

### Problem: Text not readable in screenshot
**Solution:**
- Increase terminal/editor font size before capturing
- Use higher resolution capture
- Zoom in before taking screenshot

---

## Final Checklist

Before submitting your report:

- [ ] All 3 screenshots captured and clear
- [ ] Screenshots inserted in correct locations
- [ ] Images are properly sized (not too big/small)
- [ ] Images are centered
- [ ] No placeholder text remains in document
- [ ] Table of Contents added
- [ ] Document is 5-6 pages total
- [ ] Spell check run
- [ ] File named correctly: `BSCS-13B_Gp1_RISC-V_Simulator_Report.docx`

---

## Time Estimate

- Screenshot 1: 2 minutes (just run program)
- Screenshot 2: 3 minutes (run tests or capture output)
- Screenshot 3: 2 minutes (show file structure)
- Inserting into Word: 5 minutes
- **Total: ~15 minutes**

---

## Example File Names

Save your screenshots as:
- `screenshot_1_simulator_output.png`
- `screenshot_2_tests_passing.png`
- `screenshot_3_code_structure.png`

---

You're all set! Just capture these 3 screenshots and insert them into your report. Good luck! 🚀
