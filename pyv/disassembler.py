"""RISC-V instruction disassembler for educational output."""

import pyv.isa as isa
from pyv.util import get_bit, get_bits


class Disassembler:
    """Disassembles RISC-V instructions into human-readable format."""

    # Register ABI names for easier reading
    REG_ABI_NAMES = {
        0: "zero", 1: "ra", 2: "sp", 3: "gp",
        4: "tp", 5: "t0", 6: "t1", 7: "t2",
        8: "s0", 9: "s1", 10: "a0", 11: "a1",
        12: "a2", 13: "a3", 14: "a4", 15: "a5",
        16: "a6", 17: "a7", 18: "s2", 19: "s3",
        20: "s4", 21: "s5", 22: "s6", 23: "s7",
        24: "s8", 25: "s9", 26: "s10", 27: "s11",
        28: "t3", 29: "t4", 30: "t5", 31: "t6",
    }

    @staticmethod
    def reg_name(reg_num):
        """Convert register number to ABI name."""
        return f"x{reg_num}({Disassembler.REG_ABI_NAMES[reg_num]})"

    @staticmethod
    def decode_imm(opcode, inst):
        """Decode immediate value from instruction."""
        sign = get_bit(inst, 31)
        sign_ext = 0
        imm = 0

        if opcode in isa.INST_I:
            imm = get_bits(inst, 31, 20)
            if sign:
                sign_ext = 0xfffff << 12

        elif opcode in isa.INST_S:
            imm_11_5 = get_bits(inst, 31, 25)
            imm_4_0 = get_bits(inst, 11, 7)
            imm = (imm_11_5 << 5) | imm_4_0
            if sign:
                sign_ext = 0xfffff << 12

        elif opcode in isa.INST_B:
            imm_12 = get_bit(inst, 31)
            imm_10_5 = get_bits(inst, 30, 25)
            imm_4_1 = get_bits(inst, 11, 8)
            imm_11 = get_bits(inst, 7, 7)
            imm = ((imm_12 << 12) | (imm_11 << 11) | (imm_10_5 << 5) | (imm_4_1 << 1))
            if sign:
                sign_ext = 0x7ffff << 13

        elif opcode in isa.INST_U:
            imm = get_bits(inst, 31, 12) << 12

        elif opcode in isa.INST_J:
            imm_20 = get_bit(inst, 31)
            imm_10_1 = get_bits(inst, 30, 21)
            imm_11 = get_bits(inst, 20, 20)
            imm_19_12 = get_bits(inst, 19, 12)
            imm = ((imm_20 << 20) | (imm_19_12 << 12) | (imm_11 << 11) | (imm_10_1 << 1))
            if sign:
                sign_ext = 0x7ff << 21

        return sign_ext | imm

    @staticmethod
    def disassemble(inst):
        """Disassemble a single instruction.

        Args:
            inst: 32-bit instruction word

        Returns:
            Tuple of (mnemonic, description) strings
        """
        if inst == 0x00000013:
            return "NOP", "nop (addi x0, x0, 0)"

        if inst == 0x73:
            return "ECALL", "ecall"

        if inst == 0x30200073:
            return "MRET", "mret"

        # Check if valid instruction
        if (inst & 0x3) != 0x3:
            return "INVALID", f"invalid instruction (0x{inst:08x})"

        opcode = get_bits(inst, 6, 2)
        funct3 = get_bits(inst, 14, 12)
        funct7 = get_bits(inst, 31, 25)
        rd = get_bits(inst, 11, 7)
        rs1 = get_bits(inst, 19, 15)
        rs2 = get_bits(inst, 24, 20)
        imm = Disassembler.decode_imm(opcode, inst)

        # Convert to signed for display
        def to_signed(val, bits=32):
            if val & (1 << (bits - 1)):
                return val - (1 << bits)
            return val

        imm_signed = to_signed(imm)

        try:
            # R-type instructions
            if opcode == isa.OPCODES["OP"]:
                rd_name = Disassembler.reg_name(rd)
                rs1_name = Disassembler.reg_name(rs1)
                rs2_name = Disassembler.reg_name(rs2)

                if funct7 == 0:
                    if funct3 == 0b000:
                        return "ADD", f"add {rd_name}, {rs1_name}, {rs2_name}"
                    elif funct3 == 0b001:
                        return "SLL", f"sll {rd_name}, {rs1_name}, {rs2_name}"
                    elif funct3 == 0b010:
                        return "SLT", f"slt {rd_name}, {rs1_name}, {rs2_name}"
                    elif funct3 == 0b011:
                        return "SLTU", f"sltu {rd_name}, {rs1_name}, {rs2_name}"
                    elif funct3 == 0b100:
                        return "XOR", f"xor {rd_name}, {rs1_name}, {rs2_name}"
                    elif funct3 == 0b101:
                        return "SRL", f"srl {rd_name}, {rs1_name}, {rs2_name}"
                    elif funct3 == 0b110:
                        return "OR", f"or {rd_name}, {rs1_name}, {rs2_name}"
                    elif funct3 == 0b111:
                        return "AND", f"and {rd_name}, {rs1_name}, {rs2_name}"
                elif funct7 == 0b0100000:
                    if funct3 == 0b000:
                        return "SUB", f"sub {rd_name}, {rs1_name}, {rs2_name}"
                    elif funct3 == 0b101:
                        return "SRA", f"sra {rd_name}, {rs1_name}, {rs2_name}"

            # I-type instructions
            elif opcode == isa.OPCODES["OP-IMM"]:
                rd_name = Disassembler.reg_name(rd)
                rs1_name = Disassembler.reg_name(rs1)
                shamt = get_bits(inst, 24, 20)

                if funct3 == 0b000:
                    return "ADDI", f"addi {rd_name}, {rs1_name}, {imm_signed}"
                elif funct3 == 0b010:
                    return "SLTI", f"slti {rd_name}, {rs1_name}, {imm_signed}"
                elif funct3 == 0b011:
                    return "SLTIU", f"sltiu {rd_name}, {rs1_name}, {imm_signed}"
                elif funct3 == 0b100:
                    return "XORI", f"xori {rd_name}, {rs1_name}, {imm_signed}"
                elif funct3 == 0b110:
                    return "ORI", f"ori {rd_name}, {rs1_name}, {imm_signed}"
                elif funct3 == 0b111:
                    return "ANDI", f"andi {rd_name}, {rs1_name}, {imm_signed}"
                elif funct3 == 0b001:
                    return "SLLI", f"slli {rd_name}, {rs1_name}, {shamt}"
                elif funct3 == 0b101:
                    if funct7 == 0:
                        return "SRLI", f"srli {rd_name}, {rs1_name}, {shamt}"
                    elif funct7 == 0b0100000:
                        return "SRAI", f"srai {rd_name}, {rs1_name}, {shamt}"

            # Load instructions
            elif opcode == isa.OPCODES["LOAD"]:
                rd_name = Disassembler.reg_name(rd)
                rs1_name = Disassembler.reg_name(rs1)

                if funct3 == 0:
                    return "LB", f"lb {rd_name}, {imm_signed}({rs1_name})"
                elif funct3 == 1:
                    return "LH", f"lh {rd_name}, {imm_signed}({rs1_name})"
                elif funct3 == 2:
                    return "LW", f"lw {rd_name}, {imm_signed}({rs1_name})"
                elif funct3 == 4:
                    return "LBU", f"lbu {rd_name}, {imm_signed}({rs1_name})"
                elif funct3 == 5:
                    return "LHU", f"lhu {rd_name}, {imm_signed}({rs1_name})"

            # Store instructions
            elif opcode == isa.OPCODES["STORE"]:
                rs1_name = Disassembler.reg_name(rs1)
                rs2_name = Disassembler.reg_name(rs2)

                if funct3 == 0:
                    return "SB", f"sb {rs2_name}, {imm_signed}({rs1_name})"
                elif funct3 == 1:
                    return "SH", f"sh {rs2_name}, {imm_signed}({rs1_name})"
                elif funct3 == 2:
                    return "SW", f"sw {rs2_name}, {imm_signed}({rs1_name})"

            # Branch instructions
            elif opcode == isa.OPCODES["BRANCH"]:
                rs1_name = Disassembler.reg_name(rs1)
                rs2_name = Disassembler.reg_name(rs2)

                if funct3 == 0:
                    return "BEQ", f"beq {rs1_name}, {rs2_name}, {imm_signed}"
                elif funct3 == 1:
                    return "BNE", f"bne {rs1_name}, {rs2_name}, {imm_signed}"
                elif funct3 == 4:
                    return "BLT", f"blt {rs1_name}, {rs2_name}, {imm_signed}"
                elif funct3 == 5:
                    return "BGE", f"bge {rs1_name}, {rs2_name}, {imm_signed}"
                elif funct3 == 6:
                    return "BLTU", f"bltu {rs1_name}, {rs2_name}, {imm_signed}"
                elif funct3 == 7:
                    return "BGEU", f"bgeu {rs1_name}, {rs2_name}, {imm_signed}"

            # Jump instructions
            elif opcode == isa.OPCODES["JAL"]:
                rd_name = Disassembler.reg_name(rd)
                return "JAL", f"jal {rd_name}, {imm_signed}"

            elif opcode == isa.OPCODES["JALR"]:
                rd_name = Disassembler.reg_name(rd)
                rs1_name = Disassembler.reg_name(rs1)
                return "JALR", f"jalr {rd_name}, {rs1_name}, {imm_signed}"

            # U-type instructions
            elif opcode == isa.OPCODES["LUI"]:
                rd_name = Disassembler.reg_name(rd)
                return "LUI", f"lui {rd_name}, {imm >> 12}"

            elif opcode == isa.OPCODES["AUIPC"]:
                rd_name = Disassembler.reg_name(rd)
                return "AUIPC", f"auipc {rd_name}, {imm >> 12}"

            # CSR instructions
            elif opcode == isa.OPCODES["SYSTEM"]:
                rd_name = Disassembler.reg_name(rd)
                rs1_name = Disassembler.reg_name(rs1)
                csr = get_bits(inst, 31, 20)

                if funct3 == isa.CSR_F3["CSRRW"]:
                    return "CSRRW", f"csrrw {rd_name}, 0x{csr:03x}, {rs1_name}"
                elif funct3 == isa.CSR_F3["CSRRS"]:
                    return "CSRRS", f"csrrs {rd_name}, 0x{csr:03x}, {rs1_name}"
                elif funct3 == isa.CSR_F3["CSRRC"]:
                    return "CSRRC", f"csrrc {rd_name}, 0x{csr:03x}, {rs1_name}"
                elif funct3 == isa.CSR_F3["CSRRWI"]:
                    return "CSRRWI", f"csrrwi {rd_name}, 0x{csr:03x}, {rs1}"
                elif funct3 == isa.CSR_F3["CSRRSI"]:
                    return "CSRRSI", f"csrrsi {rd_name}, 0x{csr:03x}, {rs1}"
                elif funct3 == isa.CSR_F3["CSRRCI"]:
                    return "CSRRCI", f"csrrci {rd_name}, 0x{csr:03x}, {rs1}"

        except Exception:
            pass

        return "UNKNOWN", f"unknown instruction (0x{inst:08x})"
