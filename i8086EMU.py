from enum import Enum


class Rg(Enum):
    AX = 0
    CX = 1
    DX = 2
    BX = 3
    DI = 4
    SI = 5
    BP = 6
    SP = 7


class i8086:
    def __init__(self):
        # REG
        self.regs = [0] * 8
        self.opcode = 0x00
        self.arg1 = 0x00
        self.arg2 = 0x00
        self.cs = self.ds = self.ss = self.es = 0
        self.flag = 0
        self.ip = 0
        self.mem = bytearray(1 << 20)
        self.description = str()
        self.stack = []

    def set_instruction(self, instruction):
        self.opcode = (instruction & 0xFF0000) >> 16
        self.arg1 = (instruction & 0x00FF00) >> 8
        self.arg2 = instruction & 0x0000FF
        self.decode()

    def decode(self):
        op = self.opcode
        val16 = self.imm16()
        cf = self.flag & 0x0001
        # MOV RG, im16
        if (op & 0xF8) == 0xB8:
            reg = op & 0x07
            self.regs[reg] = val16
            self.description = f"MOV {Rg(reg).name}, {format(val16,'04x')}H"
        # ADD/ADC/OR/XOR/... AX, im16 (ALU)
        elif (op & 0xC7) == 0x05:
            which = (op >> 3) & 7
            if which == 0:
                self.regs[Rg.AX.value], setcarry = self.add16(
                    self.regs[Rg.AX.value], val16
                )
            elif which == 1:
                self.regs[Rg.AX.value], setcarry = self.add16(
                    self.regs[Rg.AX.value], val16, cf
                )
                self.flag |= 0x0001 if setcarry else self.flag
            self.description = f"ADD AX, {format(val16,'04x')}H"
        # INC/DEC RG
        elif (op & 0xF0) == 0x40:
            reg = op & 0x0F
            inc_or_dec = reg < 0x8
            reg = reg if inc_or_dec else reg - 8
            val = self.regs[reg]
            self.regs[reg] = (val + 1) if inc_or_dec else (val - 1)
            self.regs[reg] &= 0xFFFF
            self.description = f"{'INC' if inc_or_dec else 'DEC'} {Rg(reg).name}"
        # PUSH/POP RG
        elif (op & 0xF0) == 0x50:
            reg = op & 0x0F
            pushpop = reg < 0x8
            reg = reg if pushpop else reg - 8
            val = self.regs[reg]
            if pushpop:
                self.stack.append(val)
            else:
                self.regs[reg] = self.stack.pop()
            self.description = f"{'PUSH' if pushpop else 'POP'} {Rg(reg).name}"
        else:
            raise NotImplementedError(f"Unimplemented opcode with {format(op,'#04x')}")
        self.print_desc()
        self.ip += 4

    def imm16(self):
        return (self.arg2 << 8) | self.arg1

    def add16(self, a, b, carry=0):
        resultprev = a + b + carry
        result = resultprev & 0xFFFF
        if carry != 0:
            carry = result < resultprev
        return result, carry

    def print_desc(self):
        print(self.description)

    def print_state(self):
        for i in range(8):
            hex = ""
            if i <= 3:
                hex = format(self.regs[Rg(i).value], "04X")
                hex = " ".join(hex[i : i + 2] for i in range(0, len(hex), 2))
            else:
                hex = format(self.regs[Rg(i).value], "02X")
            print(f"{Rg(i).name} =", hex)
        print([format(x, "#x") for x in self.stack])


def main():
    cpu = i8086()
    # MOV AX, 6968H
    cpu.set_instruction(0xB86869)
    # ADD AX, 9697H
    cpu.set_instruction(0x059796)
    # INC AX
    cpu.set_instruction(0x400000)
    # INC BX
    cpu.set_instruction(0x430000)
    # DEC AX
    cpu.set_instruction(0x480000)
    # PUSH AX
    cpu.set_instruction(0x500000)
    cpu.print_state()


if __name__ == "__main__":
    main()
