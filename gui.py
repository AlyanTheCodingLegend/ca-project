#!/usr/bin/env python3
"""Simple Tkinter GUI for Py-V (minimal viewer & cycle stepper).

Features:
- Select a program, compile and load into pipelined model
- Step single cycles or run continuously
- Display PC, IF/ID instruction, EX ALU result, MEM read data and registers x0-x7
"""

import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

from pyv.models.pipelined import PipelinedModel

# Import compile_program from main (safe; main has guard)
import main as simulator_main


class PipelinedGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Py-V: Pipeline Visualizer")
        self.geometry("800x600")

        self.model = None
        self.core = None
        self.running = False
        self._run_job = None
        self._run_n_remaining = 0

        # State for change-detection and auto-stop
        self._prev_snapshot = None
        self._stable_count = 0
        self._stable_threshold = 6  # stop after 6 consecutive cycles with no changes

        # Project root (dir where this file lives) — use for finding programs/run.log
        self.proj_root = os.path.dirname(__file__)

        self._build_ui()
        self._populate_programs()

    def _build_ui(self):
        # Top frame: controls
        ctrl = ttk.Frame(self)
        ctrl.pack(side=tk.TOP, fill=tk.X, padx=8, pady=8)

        ttk.Label(ctrl, text="Program:").pack(side=tk.LEFT)
        self.program_var = tk.StringVar()
        self.program_cb = ttk.Combobox(ctrl, textvariable=self.program_var, state='readonly')
        self.program_cb.pack(side=tk.LEFT, padx=6)

        # Model selection (Pipelined or Single-cycle)
        ttk.Label(ctrl, text="Model:").pack(side=tk.LEFT, padx=(12,0))
        self.model_var = tk.StringVar()
        self.model_cb = ttk.Combobox(ctrl, textvariable=self.model_var, state='readonly', width=14)
        self.model_cb['values'] = ('Pipelined', 'Single-cycle')
        self.model_cb.current(0)
        self.model_cb.pack(side=tk.LEFT, padx=6)

        self.compile_btn = ttk.Button(ctrl, text="Compile & Load", command=self.compile_and_load)
        self.compile_btn.pack(side=tk.LEFT, padx=6) 

        # Secondary row for run/step controls so widgets do not get squashed
        run_ctrl = ttk.Frame(self)
        run_ctrl.pack(side=tk.TOP, fill=tk.X, padx=8, pady=(4,8))

        self.step_btn = ttk.Button(run_ctrl, text="Step", command=self.step_cycle, state=tk.DISABLED)
        self.step_btn.pack(side=tk.LEFT, padx=6)

        self.run_btn = ttk.Button(run_ctrl, text="Run", command=self.toggle_run, state=tk.DISABLED)
        self.run_btn.pack(side=tk.LEFT, padx=6)

        # Run N cycles controls
        ttk.Label(run_ctrl, text="Cycles (N):").pack(side=tk.LEFT, padx=(8,0))
        self.cycles_var = tk.IntVar(value=100)
        try:
            # Use ttk.Spinbox when available for nicer UX
            self.cycles_spin = ttk.Spinbox(run_ctrl, from_=1, to=1000000, textvariable=self.cycles_var, width=8)
        except Exception:
            self.cycles_spin = tk.Spinbox(run_ctrl, from_=1, to=1000000, textvariable=self.cycles_var, width=8)
        self.cycles_spin.pack(side=tk.LEFT, padx=4)
        self.run_n_btn = ttk.Button(run_ctrl, text="Run N", command=self.run_n_cycles, state=tk.DISABLED)
        self.run_n_btn.pack(side=tk.LEFT, padx=6)

        self.reset_btn = ttk.Button(run_ctrl, text="Reset", command=self.reset_model, state=tk.DISABLED)
        self.reset_btn.pack(side=tk.LEFT, padx=6)

        # Trace / Log buttons
        self.trace_btn = ttk.Button(run_ctrl, text="Dump Trace", command=self.dump_trace, state=tk.DISABLED)
        self.trace_btn.pack(side=tk.LEFT, padx=6)

        self.loadlog_btn = ttk.Button(run_ctrl, text="Load run.log", command=self.load_run_log)
        self.loadlog_btn.pack(side=tk.LEFT, padx=6)

        self.clearlog_btn = ttk.Button(run_ctrl, text="Clear Logs", command=self.clear_logs)
        self.clearlog_btn.pack(side=tk.LEFT, padx=6)

        # Middle frame: pipeline state
        mid = ttk.Frame(self)
        mid.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=8, pady=8)

        left = ttk.Frame(mid)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        right = ttk.Frame(mid)
        right.pack(side=tk.RIGHT, fill=tk.Y)

        # PC and IF/ID
        self.pc_label = ttk.Label(left, text="PC: 0x00000000", font=("Courier", 12))
        self.pc_label.pack(anchor=tk.W)

        self.ifid_label = ttk.Label(left, text="IF/ID: inst=0x00000000", font=("Courier", 10))
        self.ifid_label.pack(anchor=tk.W, pady=(6, 0))

        self.ex_label = ttk.Label(left, text="EX: alu_res=0x00000000", font=("Courier", 10))
        self.ex_label.pack(anchor=tk.W, pady=(6, 0))

        self.mem_label = ttk.Label(left, text="MEM: mem_rdata=0x00000000", font=("Courier", 10))
        self.mem_label.pack(anchor=tk.W, pady=(6, 0))

        # Registers view
        reg_frame = ttk.LabelFrame(left, text="Registers (x0-x15)")
        reg_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        self.reg_text = scrolledtext.ScrolledText(reg_frame, height=10, width=40, font=("Courier", 10))
        self.reg_text.pack(fill=tk.BOTH, expand=True)
        self.reg_text.config(state=tk.DISABLED)

        # Right: log
        log_frame = ttk.LabelFrame(right, text="Log")
        log_frame.pack(fill=tk.BOTH, expand=True)

        self.log_text = scrolledtext.ScrolledText(log_frame, height=20, width=40, font=("Courier", 10))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)

    def _populate_programs(self):
        prog_dir = os.path.join(self.proj_root, 'programs')
        if not os.path.exists(prog_dir):
            # Keep GUI usable even if launched from a different CWD
            self.log(f"Program directory not found: {prog_dir}")
            self.program_cb['values'] = []
            return
        progs = [d for d in os.listdir(prog_dir) if os.path.isdir(os.path.join(prog_dir, d)) and d != 'common']
        progs.sort()
        self.program_cb['values'] = progs
        if progs:
            self.program_cb.current(0) 

    def log(self, text: str):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, text + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def compile_and_load(self):
        prog = self.program_var.get().strip()
        if not prog:
            messagebox.showerror("Error", "No program selected")
            return

        self.log(f"Compiling {prog}...")
        # Ensure compile is run from project root so main.compile_program can find paths
        oldcwd = os.getcwd()
        try:
            os.chdir(self.proj_root)
            bin_file = simulator_main.compile_program(prog)
        except Exception as e:
            self.log(f"Compilation error: {e}")
            messagebox.showerror("Compilation Error", str(e))
            return
        finally:
            os.chdir(oldcwd)

        self.log(f"Loading binary: {bin_file}")

        # Instantiate selected model
        sel = self.model_var.get() if hasattr(self, 'model_var') else 'Pipelined'
        try:
            if sel == 'Single-cycle' or sel.lower().startswith('single'):
                from pyv.models.singlecycle import SingleCycleModel
                self.model = SingleCycleModel()
                self.log("Using Single-Cycle model")
            else:
                from pyv.models.pipelined import PipelinedModel
                self.model = PipelinedModel(verbose=False, interactive=True)
                self.log("Using Pipelined model")
            self.core = self.model.core
            self.model.load_binary(bin_file)
        except Exception as e:
            self.log(f"Error creating/loading model: {e}")
            messagebox.showerror("Model Error", str(e))
            return

        # Ensure registers are reset so stepping/run behaves predictably
        try:
            self.model.sim.reset()
        except Exception:
            pass

        # Run combinatorial logic once so outputs are stable for the GUI
        try:
            self.model.sim.run_comb_logic()
        except Exception:
            # If there's an early exception (e.g., bad binary), catch and log
            self.log("Warning: combinatorial update failed after load")

        self.log("Binary loaded into instruction memory")

        # Initialize snapshot state so we don't log initial state as a "change" on first step
        try:
            self._prev_snapshot = self._snapshot_state()
            self._stable_count = 0
        except Exception:
            self._prev_snapshot = None
            self._stable_count = 0

        self.step_btn.config(state=tk.NORMAL)
        self.run_btn.config(state=tk.NORMAL)
        self.run_n_btn.config(state=tk.NORMAL)
        self.reset_btn.config(state=tk.NORMAL)
        self.trace_btn.config(state=tk.NORMAL)

        self.update_view()

    def step_cycle(self):
        if not self.model:
            return
        # Single cycle step
        try:
            self.model.sim.step()
        except Exception as e:
            # Show error and stop continuous run if active
            self.log(f"Error during step: {e}")
            messagebox.showerror("Simulation Error", str(e))
            self.running = False
            self.run_btn.config(text="Run")
            return
        # Handle snapshot/diff logging and check for auto-stop
        self._handle_post_step()
        self.update_view()

    def run_loop(self):
        if not self.running or not self.model:
            return
        try:
            self.model.sim.step()
        except Exception as e:
            self.log(f"Error during run: {e}")
            messagebox.showerror("Simulation Error", str(e))
            self.running = False
            self.run_btn.config(text="Run")
            return
        # Handle snapshot/diff logging and check for auto-stop
        self._handle_post_step()

        # If auto-stop triggered, stop scheduling
        if not self.running:
            self.log("Continuous run stopped by condition.")
            return

        self.update_view()
        # Schedule next
        self._run_job = self.after(10, self.run_loop)  # 10ms per cycle (fast)

    def toggle_run(self):
        if not self.model:
            return
        self.running = not self.running
        if self.running:
            self.run_btn.config(text="Stop")
            self.log("Starting continuous run...")
            self.run_loop()
        else:
            self.run_btn.config(text="Run")
            self.log("Stopped")
            if self._run_job:
                self.after_cancel(self._run_job)
                self._run_job = None

    def run_n_cycles(self):
        """Run N cycles (non-blocking, cancellable via the 'Run N' button)."""
        if not self.model:
            return
        try:
            n = int(self.cycles_var.get())
            if n <= 0:
                raise ValueError("Number must be positive")
        except Exception as e:
            messagebox.showerror("Invalid cycles", f"Invalid cycle count: {e}")
            return
        self.log(f"Run N: executing {n} cycles...")
        self._run_n_remaining = n
        # Disable conflicting controls
        self.step_btn.config(state=tk.DISABLED)
        self.run_btn.config(state=tk.DISABLED)
        # Change button into a stop control
        self.run_n_btn.config(text="Stop N", command=self.stop_run_n)
        # Start stepping
        self.after(1, self._run_n_step)

    def _run_n_step(self):
        """Single-step helper for run_n_cycles."""
        if not self.model:
            self._run_n_remaining = 0
        if self._run_n_remaining <= 0:
            self.log("Run N: completed")
            self.run_n_btn.config(text="Run N", command=self.run_n_cycles)
            self.step_btn.config(state=tk.NORMAL)
            self.run_btn.config(state=tk.NORMAL)
            return
        try:
            self.model.sim.step()
        except Exception as e:
            self.log(f"Error during Run N: {e}")
            messagebox.showerror("Simulation Error", str(e))
            self._run_n_remaining = 0
            self.run_n_btn.config(text="Run N", command=self.run_n_cycles)
            self.step_btn.config(state=tk.NORMAL)
            self.run_btn.config(state=tk.NORMAL)
            return
        # After a successful step, handle diffs & auto-stop
        self._handle_post_step()
        # If auto-stop cancelled run_n, ensure we clean up
        if self._run_n_remaining <= 0:
            self.run_n_btn.config(text="Run N", command=self.run_n_cycles)
            self.step_btn.config(state=tk.NORMAL)
            self.run_btn.config(state=tk.NORMAL)
            return
        self._run_n_remaining -= 1
        # Update UI
        self.update_view()
        # Schedule next step
        self.after(1, self._run_n_step)

    def stop_run_n(self):
        self.log("Run N: cancelled by user")
        self._run_n_remaining = 0
        # Reset button and controls
        self.run_n_btn.config(text="Run N", command=self.run_n_cycles)
        self.step_btn.config(state=tk.NORMAL)
        self.run_btn.config(state=tk.NORMAL)

    def reset_model(self):
        if not self.model:
            return
        self.model.sim.reset()
        # Reset cycles counter to 0 in simulator
        # Note: PipelinedModel keeps memory intact; registers reset
        self.log("Simulator reset (registers cleared).")
        self.update_view()

    def update_view(self):
        if not self.model:
            return
        core = self.core
        try:
            # Prefer model API where available
            try:
                pc = self.model.readPC()
            except Exception:
                # Fallback to core registers
                try:
                    pc = core.pc_reg.cur.read()
                except Exception:
                    pc = 0

            self.pc_label.config(text=f"PC: 0x{pc:08X}")

            # Instruction (attempt to read 4 bytes from instruction memory)
            try:
                inst_bytes = self.model.readInstMem(pc, 4)
                inst_display = inst_bytes[0] if inst_bytes else '0x00000000'
            except Exception:
                inst_display = 'N/A'
            self.ifid_label.config(text=f"IF/ID: inst={inst_display} pc=0x{pc:08X}")

            # EX/ALU (best effort)
            alu_text = 'EX: N/A'
            try:
                if hasattr(core, 'exmem_reg'):
                    ex = core.exmem_reg.EXMEM_o.read()
                    alu_text = f"EX: alu_res=0x{ex.alu_res:08X} take_branch={ex.take_branch}"
                elif hasattr(core, 'EXMEM'):
                    ex = core.EXMEM.read()
                    alu_text = f"EX: alu_res=0x{ex.alu_res:08X} take_branch={ex.take_branch}"
            except Exception:
                pass
            self.ex_label.config(text=alu_text)

            # MEM
            mem_text = 'MEM: N/A'
            try:
                if hasattr(core, 'memwb_reg'):
                    m = core.memwb_reg.MEMWB_o.read()
                    mem_text = f"MEM: mem_rdata=0x{m.mem_rdata:08X} wb_sel={m.wb_sel}"
            except Exception:
                pass
            self.mem_label.config(text=mem_text)

            # Registers x0-x15 via model API
            regs = []
            for i in range(16):
                try:
                    val = self.model.readReg(i)
                except Exception:
                    try:
                        val = core.regf.read(i)
                    except Exception:
                        val = 0
                regs.append(f"x{i:02} = 0x{val:08X}")
            self.reg_text.config(state=tk.NORMAL)
            self.reg_text.delete('1.0', tk.END)
            self.reg_text.insert(tk.END, "\n".join(regs))
            self.reg_text.config(state=tk.DISABLED)

            self.log(f"Cycle: {self.model.get_cycles()}  PC=0x{pc:08X}")
        except Exception as e:
            self.log(f"Error updating view: {e}")

    def _snapshot_state(self):
        """Return a compact snapshot of observable state."""
        core = getattr(self, 'core', None)
        snap = {}
        # PC
        try:
            snap['pc'] = self.model.readPC()
        except Exception:
            try:
                snap['pc'] = core.pc_reg.cur.read()
            except Exception:
                snap['pc'] = None

        # Registers x0-x15
        regs = {}
        for i in range(16):
            try:
                regs[i] = self.model.readReg(i)
            except Exception:
                try:
                    regs[i] = core.regf.read(i)
                except Exception:
                    regs[i] = None
        snap['regs'] = regs

        # IF/ID instruction
        try:
            if hasattr(core, 'ifid_reg'):
                ifid = core.ifid_reg.IFID_o.read()
                snap['ifid_inst'] = getattr(ifid, 'inst', None)
                snap['ifid_pc'] = getattr(ifid, 'pc', None)
            else:
                snap['ifid_inst'] = None
                snap['ifid_pc'] = None
        except Exception:
            snap['ifid_inst'] = None
            snap['ifid_pc'] = None

        # EX/MEM and MEM/WB
        try:
            if hasattr(core, 'exmem_reg'):
                ex = core.exmem_reg.EXMEM_o.read()
                snap['ex_alu'] = getattr(ex, 'alu_res', None)
                snap['ex_take_branch'] = getattr(ex, 'take_branch', None)
            else:
                snap['ex_alu'] = None
                snap['ex_take_branch'] = None
        except Exception:
            snap['ex_alu'] = None
            snap['ex_take_branch'] = None

        try:
            if hasattr(core, 'memwb_reg'):
                memwb = core.memwb_reg.MEMWB_o.read()
                snap['mem_rdata'] = getattr(memwb, 'mem_rdata', None)
            else:
                snap['mem_rdata'] = None
        except Exception:
            snap['mem_rdata'] = None

        return snap

    def _format_diff(self, prev, cur):
        """Return list of human-readable diff lines between prev and cur snapshots."""
        lines = []
        if prev is None:
            lines.append(f"PC: {cur.get('pc'):#010x}" if cur.get('pc') is not None else "PC: N/A")
            # show a summary of registers
            regs = cur.get('regs', {})
            changed = [f"x{i}=0x{v:08X}" for i, v in regs.items() if v is not None]
            if changed:
                lines.append("Regs: " + ' '.join(changed))
            return lines

        # PC change
        pprev = prev.get('pc')
        pcur = cur.get('pc')
        if pprev != pcur:
            lines.append(f"PC: {pprev:#010x} -> {pcur:#010x}")

        # Registers changes (only show those that changed)
        regs_prev = prev.get('regs', {})
        regs_cur = cur.get('regs', {})
        reg_lines = []
        for i in range(16):
            pv = regs_prev.get(i)
            cv = regs_cur.get(i)
            if pv != cv:
                pv_s = f"0x{pv:08X}" if pv is not None else 'N/A'
                cv_s = f"0x{cv:08X}" if cv is not None else 'N/A'
                reg_lines.append(f"x{i}: {pv_s} -> {cv_s}")
        if reg_lines:
            lines.extend(reg_lines)

        # IF/ID change
        if prev.get('ifid_inst') != cur.get('ifid_inst') or prev.get('ifid_pc') != cur.get('ifid_pc'):
            lines.append(f"IF/ID: inst {prev.get('ifid_inst')} -> {cur.get('ifid_inst')} pc {prev.get('ifid_pc')} -> {cur.get('ifid_pc')}")

        # EX
        if prev.get('ex_alu') != cur.get('ex_alu'):
            lines.append(f"EX: alu_res {prev.get('ex_alu')} -> {cur.get('ex_alu')}")
        if prev.get('ex_take_branch') != cur.get('ex_take_branch'):
            lines.append(f"EX: take_branch {prev.get('ex_take_branch')} -> {cur.get('ex_take_branch')}")

        # MEM
        if prev.get('mem_rdata') != cur.get('mem_rdata'):
            lines.append(f"MEM: mem_rdata {prev.get('mem_rdata')} -> {cur.get('mem_rdata')}")

        return lines

    def _handle_post_step(self):
        """Handle snapshot/diff logging and auto-stop logic after a cycle step."""
        try:
            cur = self._snapshot_state()
            prev = self._prev_snapshot
            diffs = self._format_diff(prev, cur)

            if diffs:
                # Log a compact diff with cycle number
                cyc = None
                try:
                    cyc = self.model.get_cycles()
                except Exception:
                    pass
                prefix = f"Δ Cycle {cyc}: " if cyc is not None else "Δ Cycle: "
                self.log(prefix + ('\n' + prefix).join(diffs))
                self._stable_count = 0
            else:
                # No observable differences this cycle
                self._stable_count += 1

            # Check for execution completion (pipeline empty) -- stop immediately
            try:
                core = self.core
                pipeline_empty = True
                if hasattr(core, 'ifid_reg'):
                    if core.ifid_reg.IFID_o.read().inst != 0:
                        pipeline_empty = False
                if hasattr(core, 'idex_reg'):
                    idex = core.idex_reg.IDEX_o.read()
                    if getattr(idex, 'opcode', 0) != 0 or getattr(idex, 'rd', 0) != 0:
                        pipeline_empty = False
                if hasattr(core, 'exmem_reg'):
                    exm = core.exmem_reg.EXMEM_o.read()
                    if getattr(exm, 'rd', 0) != 0 or getattr(exm, 'alu_res', None) != None:
                        # treat as non-empty if rd != 0 or alu_res set
                        if getattr(exm, 'rd', 0) != 0:
                            pipeline_empty = False
                if hasattr(core, 'memwb_reg'):
                    mw = core.memwb_reg.MEMWB_o.read()
                    if getattr(mw, 'rd', 0) != 0:
                        pipeline_empty = False
                if pipeline_empty:
                    self.log("Pipeline appears empty — execution complete. Stopping.")
                    if self.running:
                        self.running = False
                        self.run_btn.config(text="Run")
                    if self._run_n_remaining:
                        self._run_n_remaining = 0
                        self.run_n_btn.config(text="Run N", command=self.run_n_cycles)
                    # keep prev snapshot update and return
                    self._prev_snapshot = cur
                    return
            except Exception:
                pass

            if self._stable_count >= self._stable_threshold:
                self.log(f"No changes observed for {self._stable_count} cycles — stopping execution.")
                # stop continuous run and cancel Run N
                if self.running:
                    self.running = False
                    self.run_btn.config(text="Run")
                if self._run_n_remaining:
                    self._run_n_remaining = 0
                    self.run_n_btn.config(text="Run N", command=self.run_n_cycles)

            # Keep snapshot
            self._prev_snapshot = cur
        except Exception as e:
            self.log(f"Error handling post-step: {e}")

    def dump_trace(self):
        """Dump a concise pipeline trace into GUI log."""
        if not self.model:
            self.log("No model loaded")
            return
        try:
            core = self.core
            lines = []
            lines.append("--- Pipeline Trace ---")
            lines.append(f"Cycle: {self.model.get_cycles()}")

            # PC via API if possible
            try:
                pc = self.model.readPC()
            except Exception:
                try:
                    pc = core.pc_reg.cur.read()
                except Exception:
                    pc = 0
            lines.append(f"PC      : 0x{pc:08X}")

            # IF/ID / instruction
            try:
                if hasattr(core, 'ifid_reg'):
                    ifid = core.ifid_reg.IFID_o.read()
                    lines.append(f"IF/ID   : inst=0x{ifid.inst:08X} pc=0x{ifid.pc:08X}")
                elif hasattr(core, 'IFID'):
                    ifid = core.IFID.read()
                    lines.append(f"IF/ID   : inst=0x{ifid.inst:08X} pc=0x{ifid.pc:08X}")
                else:
                    inst = self.model.readInstMem(pc, 4)[0]
                    lines.append(f"IF/ID   : inst={inst} pc=0x{pc:08X}")
            except Exception:
                lines.append("IF/ID   : N/A")

            # ID/EX (best-effort)
            try:
                if hasattr(core, 'idex_reg'):
                    idex = core.idex_reg.IDEX_o.read()
                    lines.append(f"ID/EX   : rd={idex.rd} we={idex.we} opcode=0x{idex.opcode:02X} imm=0x{idex.imm:08X}")
            except Exception:
                pass

            # EX/MEM
            try:
                if hasattr(core, 'exmem_reg'):
                    exmem = core.exmem_reg.EXMEM_o.read()
                    lines.append(f"EX/MEM  : rd={exmem.rd} we={exmem.we} alu_res=0x{exmem.alu_res:08X} take_branch={exmem.take_branch}")
            except Exception:
                pass

            # MEM/WB
            try:
                if hasattr(core, 'memwb_reg'):
                    memwb = core.memwb_reg.MEMWB_o.read()
                    lines.append(f"MEM/WB  : rd={memwb.rd} we={memwb.we} alu_res=0x{memwb.alu_res:08X} mem_rdata=0x{memwb.mem_rdata:08X}")
            except Exception:
                pass

            # Registers (small subset)
            regs = []
            for i in range(8):
                try:
                    regs.append(f"x{i}={self.model.readReg(i):08X}")
                except Exception:
                    try:
                        regs.append(f"x{i}={core.regf.read(i):08X}")
                    except Exception:
                        regs.append(f"x{i}=00000000")
            lines.append("Regs   : " + ' '.join(regs))

            self.log('\n'.join(lines))
        except Exception as e:
            self.log(f"Error dumping trace: {e}")

    def load_run_log(self):
        """Load the run.log contents (if present) into GUI log area."""
        try:
            runlog = os.path.join(self.proj_root, 'run.log')
            if not os.path.exists(runlog):
                self.log("No run.log file found in project dir.")
                return
            with open(runlog, 'r') as f:
                data = f.read()
            self.log_text.config(state=tk.NORMAL)
            self.log_text.delete('1.0', tk.END)
            self.log_text.insert(tk.END, data)
            self.log_text.config(state=tk.DISABLED)
            self.log("Loaded run.log into GUI")
        except Exception as e:
            self.log(f"Error loading run.log: {e}")

    def clear_logs(self):
        """Clear the GUI log pane and reset snapshot/auto-stop state.

        Prompts the user whether to also delete the on-disk `run.log` file.
        """
        try:
            self.log_text.config(state=tk.NORMAL)
            self.log_text.delete('1.0', tk.END)
            self.log_text.config(state=tk.DISABLED)
            # Reset snapshot so subsequent diffs will be recalculated from current state
            try:
                self._prev_snapshot = self._snapshot_state()
            except Exception:
                self._prev_snapshot = None
            self._stable_count = 0
            self.log("Logs cleared by user.")

            # Ask whether to delete on-disk run.log
            runlog = os.path.join(self.proj_root, 'run.log')
            if os.path.exists(runlog):
                ans = messagebox.askyesno("Delete run.log?", "Also delete on-disk 'run.log'? This cannot be undone.")
                if ans:
                    try:
                        os.remove(runlog)
                        self.log("Deleted on-disk run.log")
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to delete run.log: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clear logs: {e}")


def main():
    app = PipelinedGUI()
    app.mainloop()


if __name__ == '__main__':
    main()
