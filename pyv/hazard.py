"""Hazard detection and control for pipelined RISC-V CPU."""

from pyv.module import Module
from pyv.port import Input, Output
from pyv.stages import IFID_t, IDEX_t, EXMEM_t, MEMWB_t
import pyv.isa as isa


class HazardUnit(Module):
    """Detects and resolves pipeline hazards.

    This is a simple hazard unit that stalls on data hazards.
    No forwarding is implemented - all hazards are resolved via stalling.

    Inputs:
        IFID_i: IF/ID pipeline register contents
        IDEX_i: ID/EX pipeline register contents
        EXMEM_i: EX/MEM pipeline register contents
        take_branch_i: Whether a branch/jump is taken (from EX stage)

    Outputs:
        stall_pc_o: Stall the PC (don't update)
        stall_ifid_o: Stall IF/ID register
        stall_idex_o: Stall ID/EX register (not used in simple stall)
        stall_exmem_o: Stall EX/MEM register (not used in simple stall)
        stall_memwb_o: Stall MEM/WB register (not used in simple stall)
        flush_ifid_o: Flush IF/ID register (insert bubble)
        flush_idex_o: Flush ID/EX register (insert bubble)
        flush_exmem_o: Flush EX/MEM register (insert bubble)
    """

    def __init__(self):
        super().__init__()

        # Inputs
        self.IFID_i = Input(IFID_t)
        self.IDEX_i = Input(IDEX_t)
        self.EXMEM_i = Input(EXMEM_t)
        self.take_branch_i = Input(bool)

        # Outputs
        self.stall_pc_o = Output(bool)
        self.stall_ifid_o = Output(bool)
        self.stall_idex_o = Output(bool)
        self.stall_exmem_o = Output(bool)
        self.stall_memwb_o = Output(bool)
        self.flush_ifid_o = Output(bool)
        self.flush_idex_o = Output(bool)
        self.flush_exmem_o = Output(bool)

    def process(self):
        """Detect hazards and generate control signals."""
        ifid = self.IFID_i.read()
        idex = self.IDEX_i.read()
        exmem = self.EXMEM_i.read()
        take_branch = self.take_branch_i.read()

        # Default: no stall, no flush
        stall_pc = False
        stall_ifid = False
        flush_ifid = False
        flush_idex = False
        flush_exmem = False

        # Extract register indices from IF/ID (instruction being decoded)
        inst = ifid.inst
        if (inst & 0x3) == 0x3:  # Valid instruction
            opcode = (inst >> 2) & 0x1F
            rs1_idx = (inst >> 15) & 0x1F
            rs2_idx = (inst >> 20) & 0x1F

            # Check for load-use hazard
            # If ID/EX stage has a LOAD and its destination is used by current inst
            if idex.mem == 1:  # LOAD instruction in EX stage
                load_dest = idex.rd

                # Check if current instruction uses this register
                need_rs1 = self._needs_rs1(opcode)
                need_rs2 = self._needs_rs2(opcode)

                if need_rs1 and (rs1_idx == load_dest) and (load_dest != 0):
                    # Load-use hazard: stall
                    stall_pc = True
                    stall_ifid = True
                    flush_idex = True  # Insert bubble into ID/EX

                elif need_rs2 and (rs2_idx == load_dest) and (load_dest != 0):
                    # Load-use hazard: stall
                    stall_pc = True
                    stall_ifid = True
                    flush_idex = True

            # Check for general data hazard (non-load instructions)
            # We need to stall if a source register is being written by
            # an instruction in EX or MEM stage
            else:
                need_rs1 = self._needs_rs1(opcode)
                need_rs2 = self._needs_rs2(opcode)

                # Check EX stage hazard
                if idex.we and (idex.rd != 0):
                    if (need_rs1 and rs1_idx == idex.rd) or \
                       (need_rs2 and rs2_idx == idex.rd):
                        stall_pc = True
                        stall_ifid = True
                        flush_idex = True

                # Check MEM stage hazard
                elif exmem.we and (exmem.rd != 0):
                    if (need_rs1 and rs1_idx == exmem.rd) or \
                       (need_rs2 and rs2_idx == exmem.rd):
                        stall_pc = True
                        stall_ifid = True
                        flush_idex = True

        # Control hazard: flush pipeline on branch/jump
        if take_branch:
            flush_ifid = True
            flush_idex = True
            # Don't need to flush EXMEM since branch is decided in EX

        # Write outputs
        self.stall_pc_o.write(stall_pc)
        self.stall_ifid_o.write(stall_ifid)
        self.stall_idex_o.write(False)  # Not used in simple design
        self.stall_exmem_o.write(False)
        self.stall_memwb_o.write(False)
        self.flush_ifid_o.write(flush_ifid)
        self.flush_idex_o.write(flush_idex)
        self.flush_exmem_o.write(flush_exmem)

    def _needs_rs1(self, opcode):
        """Check if instruction needs rs1 register."""
        return opcode in [
            isa.OPCODES["OP"],
            isa.OPCODES["OP-IMM"],
            isa.OPCODES["LOAD"],
            isa.OPCODES["STORE"],
            isa.OPCODES["BRANCH"],
            isa.OPCODES["JALR"],
        ]

    def _needs_rs2(self, opcode):
        """Check if instruction needs rs2 register."""
        return opcode in [
            isa.OPCODES["OP"],
            isa.OPCODES["STORE"],
            isa.OPCODES["BRANCH"],
        ]
