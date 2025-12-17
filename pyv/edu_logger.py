"""Educational logging system for RISC-V simulator.

This module provides detailed cycle-by-cycle logging for learning purposes,
showing the state of all pipeline stages, registers, and control signals.
"""

from pyv.disassembler import Disassembler
from pyv.stages import LOAD, STORE


class EducationalLogger:
    """Provides detailed educational logging for the simulator."""

    def __init__(self, model):
        """Initialize the logger with a model instance.

        Args:
            model: SingleCycleModel or PipelinedModel instance
        """
        self.model = model
        self.core = model.core
        self.cycle = 0
        self.disasm = Disassembler()

    def print_separator(self, char="=", length=80):
        """Print a separator line."""
        print(char * length)

    def print_header(self, text):
        """Print a section header."""
        print(f"\n{'='*80}")
        print(f"  {text}")
        print(f"{'='*80}")

    def print_subheader(self, text):
        """Print a subsection header."""
        print(f"\n{'-'*80}")
        print(f"  {text}")
        print(f"{'-'*80}")

    def log_cycle(self, cycle_num):
        """Log complete state for one cycle.

        Args:
            cycle_num: Current cycle number
        """
        self.cycle = cycle_num
        self.print_header(f"CYCLE {cycle_num}")

        # Determine if pipelined or single-cycle
        is_pipelined = hasattr(self.core, 'ifid_reg')

        if is_pipelined:
            self._log_pipelined_cycle()
        else:
            self._log_singlecycle_cycle()

        # Always show register file
        self._log_registers()

        print()  # Blank line after cycle

    def _log_singlecycle_cycle(self):
        """Log single-cycle CPU state."""
        # PC and instruction
        pc = self.core.if_stg.pc_reg.cur.read()
        inst = self.core.if_stg.ir_reg.cur.read()

        print(f"\nPC: 0x{pc:08X}")
        mnemonic, desc = self.disasm.disassemble(inst)
        print(f"Instruction: 0x{inst:08X}  [{mnemonic}] {desc}")

        # All 5 stages execute in same cycle for single-cycle
        self.print_subheader("Pipeline Stages (All execute in same cycle)")

        # IF Stage
        print(f"[IF] PC=0x{pc:08X}, IR=0x{inst:08X}")

        # ID Stage
        ifid = self.core.if_stg.IFID_o.read()
        idex = self.core.id_stg.IDEX_o.read()
        print(f"[ID] rs1=x{idex.rs1 & 0xFFFFFFFF:08X}, rs2=x{idex.rs2 & 0xFFFFFFFF:08X}, "
              f"imm={idex.imm:08X}, rd=x{idex.rd}, we={idex.we}, wb_sel={idex.wb_sel}")
        print(f"     Control: mem={idex.mem}, opcode=0x{idex.opcode:02X}, "
              f"funct3=0x{idex.funct3:X}, funct7=0x{idex.funct7:02X}")

        # EX Stage
        exmem = self.core.ex_stg.EXMEM_o.read()
        print(f"[EX] ALU Result=0x{exmem.alu_res & 0xFFFFFFFF:08X}, "
              f"take_branch={exmem.take_branch}, PC+4=0x{exmem.pc4:08X}")

        # MEM Stage
        memwb = self.core.mem_stg.MEMWB_o.read()
        mem_op = "LOAD" if exmem.mem == LOAD else ("STORE" if exmem.mem == STORE else "NONE")
        print(f"[MEM] Operation={mem_op}, Addr=0x{exmem.alu_res & 0xFFFFFFFF:08X}, "
              f"Data=0x{memwb.mem_rdata & 0xFFFFFFFF:08X}")

        # WB Stage
        wb_src = ["ALU", "PC+4", "MEM", "CSR"][memwb.wb_sel] if memwb.wb_sel < 4 else "?"
        print(f"[WB] rd=x{memwb.rd}, we={memwb.we}, wb_sel={wb_src}, "
              f"value=0x{self._get_wb_value(memwb) & 0xFFFFFFFF:08X}")

    def _log_pipelined_cycle(self):
        """Log pipelined CPU state showing all stages simultaneously."""
        self.print_subheader("Pipeline Stages (Concurrent Execution)")

        # Get pipeline register contents
        ifid = self.core.ifid_reg.IFID_o.read()
        idex = self.core.idex_reg.IDEX_o.read()
        exmem = self.core.exmem_reg.EXMEM_o.read()
        memwb = self.core.memwb_reg.MEMWB_o.read()

        # Hazard signals
        stall_pc = self.core.hazard.stall_pc_o.read()
        stall_ifid = self.core.hazard.stall_ifid_o.read()
        flush_ifid = self.core.hazard.flush_ifid_o.read()
        flush_idex = self.core.hazard.flush_idex_o.read()

        # Show hazard status
        hazard_str = ""
        if stall_pc or stall_ifid:
            hazard_str = " [STALL]"
        if flush_ifid or flush_idex:
            hazard_str += " [FLUSH]"
        if hazard_str:
            print(f"\nHazard Status:{hazard_str}")
            if stall_pc:
                print("  - PC stalled")
            if flush_ifid:
                print("  - IF/ID flushed (bubble inserted)")
            if flush_idex:
                print("  - ID/EX flushed (bubble inserted)")

        # IF Stage (current)
        pc = self.core.pc_reg.cur.read()
        npc = self.core.npc.read()
        inst_fetching = self.core.if_stg.ir_reg.cur.read()
        print(f"\n[IF] PC=0x{pc:08X} -> NPC=0x{npc:08X}")
        mnemonic, desc = self.disasm.disassemble(inst_fetching)
        print(f"     Fetching: 0x{inst_fetching:08X} [{mnemonic}] {desc}")

        # ID Stage (IF/ID register)
        print(f"\n[ID] PC=0x{ifid.pc:08X}")
        mnemonic, desc = self.disasm.disassemble(ifid.inst)
        print(f"     Decoding: 0x{ifid.inst:08X} [{mnemonic}] {desc}")
        if idex.we:
            print(f"     Outputs: rs1=0x{idex.rs1 & 0xFFFFFFFF:08X}, "
                  f"rs2=0x{idex.rs2 & 0xFFFFFFFF:08X}, imm=0x{idex.imm & 0xFFFFFFFF:08X}")
            print(f"     Control: rd=x{idex.rd}, we={idex.we}, wb_sel={idex.wb_sel}, "
                  f"mem={idex.mem}")

        # EX Stage (ID/EX register)
        print(f"\n[EX] PC=0x{idex.pc:08X}")
        if idex.we or idex.mem:
            print(f"     ALU: op1=0x{idex.rs1 & 0xFFFFFFFF:08X}, "
                  f"op2=0x{idex.imm & 0xFFFFFFFF:08X} (or rs2=0x{idex.rs2 & 0xFFFFFFFF:08X})")
            print(f"     Result: 0x{exmem.alu_res & 0xFFFFFFFF:08X}, "
                  f"take_branch={exmem.take_branch}")
        else:
            print(f"     [BUBBLE - No operation]")

        # MEM Stage (EX/MEM register)
        print(f"\n[MEM]")
        if exmem.mem == LOAD:
            print(f"     LOAD from addr=0x{exmem.alu_res & 0xFFFFFFFF:08X}, "
                  f"data=0x{memwb.mem_rdata & 0xFFFFFFFF:08X}")
        elif exmem.mem == STORE:
            print(f"     STORE to addr=0x{exmem.alu_res & 0xFFFFFFFF:08X}, "
                  f"data=0x{exmem.rs2 & 0xFFFFFFFF:08X}")
        else:
            if exmem.we:
                print(f"     No memory operation (pass-through ALU result=0x{exmem.alu_res & 0xFFFFFFFF:08X})")
            else:
                print(f"     [BUBBLE - No operation]")

        # WB Stage (MEM/WB register)
        print(f"\n[WB]")
        if memwb.we:
            wb_src = ["ALU", "PC+4", "MEM", "CSR"][memwb.wb_sel] if memwb.wb_sel < 4 else "?"
            wb_val = self._get_wb_value(memwb)
            print(f"     Writing x{memwb.rd} = 0x{wb_val & 0xFFFFFFFF:08X} (source: {wb_src})")
        else:
            print(f"     [BUBBLE - No writeback]")

    def _get_wb_value(self, memwb):
        """Get the value that will be written back."""
        if memwb.wb_sel == 0:  # ALU
            return memwb.alu_res
        elif memwb.wb_sel == 1:  # PC+4
            return memwb.pc4
        elif memwb.wb_sel == 2:  # MEM
            return memwb.mem_rdata
        elif memwb.wb_sel == 3:  # CSR
            return memwb.csr_read_val
        return 0

    def _log_registers(self):
        """Log all register values."""
        self.print_subheader("Register File (x0-x31)")

        # Print in 4 columns for compact display
        for row in range(8):
            line = ""
            for col in range(4):
                reg_num = row + col * 8
                reg_val = self.core.regf.read(reg_num)
                reg_name = self.disasm.REG_ABI_NAMES[reg_num]
                line += f"x{reg_num:2d}({reg_name:4s})=0x{reg_val & 0xFFFFFFFF:08X}  "
            print(line)

    def log_summary(self, total_cycles, elapsed_time):
        """Log execution summary.

        Args:
            total_cycles: Total number of cycles executed
            elapsed_time: Wall clock time in seconds
        """
        self.print_header("EXECUTION SUMMARY")
        print(f"Total Cycles: {total_cycles}")
        print(f"Wall Clock Time: {elapsed_time:.4f} seconds")
        print(f"Simulation Speed: {total_cycles/elapsed_time:.2f} cycles/second")

        # Final PC
        pc = self.core.pc_reg.cur.read() if hasattr(self.core, 'pc_reg') else \
             self.core.if_stg.pc_reg.cur.read()
        print(f"Final PC: 0x{pc:08X}")

        # Show some interesting final register values
        print("\nFinal Register Values (non-zero):")
        for i in range(32):
            val = self.core.regf.read(i)
            if val != 0:
                reg_name = self.disasm.REG_ABI_NAMES[i]
                print(f"  x{i:2d}({reg_name:4s}) = 0x{val & 0xFFFFFFFF:08X} ({val})")

        print(f"\n{'='*80}\n")

    def interactive_prompt(self):
        """Show interactive prompt and wait for user input.

        Returns:
            True to continue, False to quit
        """
        print("\n[Press ENTER to step to next cycle, or 'q' to quit]")
        user_input = input("> ").strip().lower()
        return user_input != 'q'
