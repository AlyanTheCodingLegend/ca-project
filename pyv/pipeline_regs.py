"""Pipeline registers for pipelined RISC-V CPU."""

from pyv.module import Module
from pyv.port import Input, Output
from pyv.reg import Reg
from pyv.stages import IFID_t, IDEX_t, EXMEM_t, MEMWB_t


class IFIDReg(Module):
    """Pipeline register between IF and ID stages.

    Inputs:
        IFID_i: Data from IF stage
        stall_i: Stall signal (hold current value)
        flush_i: Flush signal (insert bubble/NOP)

    Outputs:
        IFID_o: Registered data to ID stage
    """

    def __init__(self):
        super().__init__()
        self.IFID_i = Input(IFID_t)
        self.stall_i = Input(bool)
        self.flush_i = Input(bool)
        self.IFID_o = Output(IFID_t)

        # Internal register
        self.reg = Reg(IFID_t, IFID_t(inst=0x00000013, pc=-4))

        # Connect output to register
        self.IFID_o << self.reg.cur

    def process(self):
        """Update register based on stall/flush signals."""
        stall = self.stall_i.read()
        flush = self.flush_i.read()

        if flush:
            # Insert NOP
            self.reg.next.write(IFID_t(inst=0x00000013, pc=-4))
        elif not stall:
            # Normal operation: latch input
            self.reg.next.write(self.IFID_i.read())
        # else: stall = keep current value (don't write to reg.next)


class IDEXReg(Module):
    """Pipeline register between ID and EX stages.

    Inputs:
        IDEX_i: Data from ID stage
        stall_i: Stall signal (hold current value)
        flush_i: Flush signal (insert bubble/NOP)

    Outputs:
        IDEX_o: Registered data to EX stage
    """

    def __init__(self):
        super().__init__()
        self.IDEX_i = Input(IDEX_t)
        self.stall_i = Input(bool)
        self.flush_i = Input(bool)
        self.IDEX_o = Output(IDEX_t)

        # Internal register - default to NOP-like state
        self.reg = Reg(IDEX_t, IDEX_t())

        # Connect output to register
        self.IDEX_o << self.reg.cur

    def process(self):
        """Update register based on stall/flush signals."""
        stall = self.stall_i.read()
        flush = self.flush_i.read()

        if flush:
            # Insert bubble (NOP-like: no write enable)
            self.reg.next.write(IDEX_t())
        elif not stall:
            # Normal operation: latch input
            self.reg.next.write(self.IDEX_i.read())


class EXMEMReg(Module):
    """Pipeline register between EX and MEM stages.

    Inputs:
        EXMEM_i: Data from EX stage
        stall_i: Stall signal (hold current value)
        flush_i: Flush signal (insert bubble/NOP)

    Outputs:
        EXMEM_o: Registered data to MEM stage
    """

    def __init__(self):
        super().__init__()
        self.EXMEM_i = Input(EXMEM_t)
        self.stall_i = Input(bool)
        self.flush_i = Input(bool)
        self.EXMEM_o = Output(EXMEM_t)

        # Internal register
        self.reg = Reg(EXMEM_t, EXMEM_t())

        # Connect output to register
        self.EXMEM_o << self.reg.cur

    def process(self):
        """Update register based on stall/flush signals."""
        stall = self.stall_i.read()
        flush = self.flush_i.read()

        if flush:
            # Insert bubble
            self.reg.next.write(EXMEM_t())
        elif not stall:
            # Normal operation: latch input
            self.reg.next.write(self.EXMEM_i.read())


class MEMWBReg(Module):
    """Pipeline register between MEM and WB stages.

    Inputs:
        MEMWB_i: Data from MEM stage
        stall_i: Stall signal (hold current value)
        flush_i: Flush signal (insert bubble/NOP)

    Outputs:
        MEMWB_o: Registered data to WB stage
    """

    def __init__(self):
        super().__init__()
        self.MEMWB_i = Input(MEMWB_t)
        self.stall_i = Input(bool)
        self.flush_i = Input(bool)
        self.MEMWB_o = Output(MEMWB_t)

        # Internal register
        self.reg = Reg(MEMWB_t, MEMWB_t())

        # Connect output to register
        self.MEMWB_o << self.reg.cur

    def process(self):
        """Update register based on stall/flush signals."""
        stall = self.stall_i.read()
        flush = self.flush_i.read()

        if flush:
            # Insert bubble
            self.reg.next.write(MEMWB_t())
        elif not stall:
            # Normal operation: latch input
            self.reg.next.write(self.MEMWB_i.read())
