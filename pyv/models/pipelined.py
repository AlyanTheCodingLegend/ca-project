"""Pipelined RISC-V CPU model."""

from pyv.csr import CSRUnit
from pyv.exception_unit import ExceptionUnit
from pyv.stages import IFStage, IDStage, EXStage, MEMStage, WBStage, BranchUnit
from pyv.pipeline_regs import IFIDReg, IDEXReg, EXMEMReg, MEMWBReg
from pyv.hazard import HazardUnit
from pyv.mem import Memory
from pyv.reg import Regfile, Reg
from pyv.module import Module
from pyv.models.model import Model
from pyv.port import Wire, Constant


class Pipelined(Module):
    """Implements a 5-stage pipelined RISC-V CPU with hazard detection.

    Default memory size: 8 KiB

    Pipeline stages:
    - IF: Instruction Fetch
    - ID: Instruction Decode
    - EX: Execute
    - MEM: Memory Access
    - WB: Write Back

    Features:
    - Hazard detection with stalling (no forwarding)
    - Branch/jump flushing
    - Educational logging support
    """

    def __init__(self):
        super().__init__()

        # Core components
        self.regf = Regfile()
        """RISC-V 32-bit base register file"""
        self.csr_unit = CSRUnit()
        """RISC-V CSRs"""
        self.mem = Memory(8 * 1024)
        """Main Memory (for both instructions and data)"""

        # Pipeline stages
        self.if_stg = IFStage(self.mem.read_port1)
        """Instruction Fetch"""
        self.id_stg = IDStage(self.regf, self.csr_unit)
        """Instruction Decode"""
        self.ex_stg = EXStage()
        """Execute"""
        self.mem_stg = MEMStage(self.mem.read_port0, self.mem.write_port)
        """Memory stage"""
        self.wb_stg = WBStage(self.regf)
        """Write-back"""
        self.bu = BranchUnit()
        """Branch unit"""
        self.excep = ExceptionUnit(self.csr_unit)
        """Exception unit"""

        # Pipeline registers
        self.ifid_reg = IFIDReg()
        """IF/ID pipeline register"""
        self.idex_reg = IDEXReg()
        """ID/EX pipeline register"""
        self.exmem_reg = EXMEMReg()
        """EX/MEM pipeline register"""
        self.memwb_reg = MEMWBReg()
        """MEM/WB pipeline register"""

        # Hazard detection unit
        self.hazard = HazardUnit()
        """Hazard detection and control"""

        # PC register (separate from IF stage for stall control)
        self.pc_reg = Reg(int, -4)
        """Program counter"""

        # Wires for interconnection
        self.pc = Wire(int)
        self.npc = Wire(int)
        self.stall_pc = Wire(bool)
        self.take_branch = Wire(bool, [self.connects])
        self.alu_res = Wire(int, [self.connects])

        # Connect PC
        self.pc << self.pc_reg.cur
        self.npc << self.bu.npc_o

        # Connect IF stage
        self.if_stg.npc_i << self.npc

        # Connect IF/ID pipeline register
        self.ifid_reg.IFID_i << self.if_stg.IFID_o
        self.ifid_reg.stall_i << self.hazard.stall_ifid_o
        self.ifid_reg.flush_i << self.hazard.flush_ifid_o

        # Connect ID stage
        self.id_stg.IFID_i << self.ifid_reg.IFID_o

        # Connect ID/EX pipeline register
        self.idex_reg.IDEX_i << self.id_stg.IDEX_o
        self.idex_reg.stall_i << self.hazard.stall_idex_o
        self.idex_reg.flush_i << self.hazard.flush_idex_o

        # Connect EX stage
        self.ex_stg.IDEX_i << self.idex_reg.IDEX_o

        # Connect EX/MEM pipeline register
        self.exmem_reg.EXMEM_i << self.ex_stg.EXMEM_o
        self.exmem_reg.stall_i << self.hazard.stall_exmem_o
        self.exmem_reg.flush_i << self.hazard.flush_exmem_o

        # Connect MEM stage
        self.mem_stg.EXMEM_i << self.exmem_reg.EXMEM_o

        # Connect MEM/WB pipeline register
        self.memwb_reg.MEMWB_i << self.mem_stg.MEMWB_o
        self.memwb_reg.stall_i << self.hazard.stall_memwb_o
        self.const_false = Constant(False)
        self.memwb_reg.flush_i << self.const_false  # Never flush WB stage

        # Connect WB stage
        self.wb_stg.MEMWB_i << self.memwb_reg.MEMWB_o

        # Connect branch unit
        self.bu.pc_i << self.pc
        self.bu.take_branch_i << self.take_branch
        self.bu.target_i << self.alu_res

        # Connect exception logic
        self.excep.pc_i << self.pc
        self.excep.ecall_i << self.id_stg.ecall_o
        self.excep.mret_i << self.id_stg.mret_o
        self.bu.raise_exception_i << self.excep.raise_exception_o
        self.bu.mtvec_i << self.excep.npc_o
        self.bu.trap_return_i << self.excep.trap_return_o
        self.bu.mepc_i << self.excep.npc_o
        self.csr_unit.ex_i << self.excep.raise_exception_o
        self.csr_unit.mepc_i << self.excep.mepc_o
        self.csr_unit.mcause_i << self.excep.mcause_o

        # Connect WBStage to CSR unit
        self.csr_unit.write_en_i << self.wb_stg.csr_write_en_o
        self.csr_unit.write_addr_i << self.wb_stg.csr_write_addr_o
        self.csr_unit.write_val_i << self.wb_stg.csr_write_val_o

        # Connect hazard detection unit
        self.hazard.IFID_i << self.ifid_reg.IFID_o
        self.hazard.IDEX_i << self.idex_reg.IDEX_o
        self.hazard.EXMEM_i << self.exmem_reg.EXMEM_o
        self.hazard.take_branch_i << self.take_branch
        self.stall_pc << self.hazard.stall_pc_o

    def connects(self):
        """Update PC register with stall control."""
        stall = self.stall_pc.read()

        if not stall:
            # Update PC
            self.pc_reg.next.write(self.npc.read())

        # Update internal signals
        exmem = self.exmem_reg.EXMEM_o.read()
        self.take_branch.write(exmem.take_branch)
        self.alu_res.write(exmem.alu_res)


class PipelinedModel(Model):
    """Model wrapper for Pipelined CPU."""

    def __init__(self, verbose=False, interactive=False):
        self.core = Pipelined()
        """Module instance"""
        self.verbose = verbose
        """Enable verbose cycle-by-cycle logging"""
        self.interactive = interactive
        """Enable interactive stepping mode"""
        self.setTop(self.core, 'PipelinedTop')

        super().__init__()

    def log(self):
        """Custom log function for basic output."""
        if not self.verbose:
            # Minimal logging (like SingleCycleModel)
            print("PC = 0x%08X" % self.core.pc_reg.cur.read())
            print("IR = 0x%08X" % self.core.if_stg.ir_reg.cur.read())

    def load_instructions(self, instructions):
        """Load instructions into the instruction memory.

        Args:
            instructions (list): List of instruction words.
        """
        self.core.mem.mem[:len(instructions)] = instructions

    def load_binary(self, file):
        """Load a program binary into the instruction memory.

        Args:
            file (string): Path to the binary.
        """
        f = open(file, 'rb')
        ba = bytearray(f.read())
        f.close()
        inst = list(ba)

        self.core.mem.mem[:len(inst)] = inst

    def readReg(self, reg):
        """Read a register in the register file.

        Args:
            reg (int): index of register to be read.

        Returns:
            int: Value of register.
        """
        return self.core.regf.read(reg)

    def readPC(self):
        """Read current program counter (PC).

        Returns:
            int: current program counter
        """
        return self.core.pc_reg.cur.read()

    def readDataMem(self, addr, nbytes):
        """Read bytes from data memory.

        Args:
            addr (int): Address to read from
            nbytes (int): How many bytes to read starting from `addr`.

        Returns:
            list: List of bytes.
        """
        return [hex(self.core.mem.mem[addr + i]) for i in range(0, nbytes)]

    def readInstMem(self, addr, nbytes):
        """Read bytes from instruction memory.

        Args:
            addr (int): Address to read from
            nbytes (int): How many bytes to read starting from `addr`.

        Returns:
            list: List of bytes.
        """
        return [hex(self.core.mem.mem[addr + i]) for i in range(0, nbytes)]
