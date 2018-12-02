from collections import deque
from elfsembly.instruction import JumpInstruction
import unittest


class ChronalDevice:

    MAX = None

    def __init__(self):
        self.registers = [0] * 4
        self.opcode_map = {
            0: self.gtir,
            1: self.mulr,
            2: self.seti,
            3: self.gtrr,
            4: self.bori,
            5: self.borr,
            6: self.banr,
            7: self.eqri,
            8: self.bani,
            9: self.addr,
            10: self.addi,
            11: self.eqrr,
            12: self.gtri,
            13: self.eqir,
            14: self.setr,
            15: self.muli,
        }

    def execute_instructions(self, instructions):
        for instruction in instructions:
            self.execute(instruction)

    def execute(self, instruction):
        self.opcode_map[instruction.opcode](instruction)

    def set_register(self, register, value):
        if not ChronalDevice.MAX:
            self.registers[register] = value
        else:
            self.registers[register] = value % ChronalDevice.MAX

    def addr(self, instruction):
        """
        addr (add register) stores into register C the result of adding register A and register B.
        """
        self.set_register(instruction.output, self.registers[instruction.a] + self.registers[instruction.b])

    def addi(self, instruction):
        """
        addi (add immediate) stores into register C the result of adding register A and value B.
        """
        self.set_register(instruction.output, self.registers[instruction.a] + instruction.b)

    def mulr(self, instruction):
        """
        mulr (multiply register) stores into register C the result of multiplying register A and register B.
        """
        self.set_register(instruction.output, self.registers[instruction.a] * self.registers[instruction.b])

    def muli(self, instruction):
        """
        muli (multiply immediate) stores into register C the result of multiplying register A and value B.
        """
        self.set_register(instruction.output, self.registers[instruction.a] * instruction.b)

    def banr(self, instruction):
        """
        banr (bitwise AND register) stores into register C the result of the bitwise AND of register A and register B.
        """
        self.set_register(instruction.output, self.registers[instruction.a] & self.registers[instruction.b])

    def bani(self, instruction):
        """
        bani (bitwise AND immediate) stores into register C the result of the bitwise AND of register A and value B.
        """
        self.set_register(instruction.output, self.registers[instruction.a] & instruction.b)

    def borr(self, instruction):
        """
        borr (bitwise OR register) stores into register C the result of the bitwise OR of register A and register B.
        """
        self.set_register(instruction.output, self.registers[instruction.a] | self.registers[instruction.b])

    def bori(self, instruction):
        """
        bori (bitwise OR immediate) stores into register C the result of the bitwise OR of register A and value B.
        """
        self.set_register(instruction.output, self.registers[instruction.a] | instruction.b)

    def setr(self, instruction):
        """
        setr (set register) copies the contents of register A into register C. (Input B is ignored.)
        """
        self.set_register(instruction.output, self.registers[instruction.a])

    def seti(self, instruction):
        """
        seti (set immediate) stores value A into register C. (Input B is ignored.)
        """
        self.set_register(instruction.output, instruction.a)

    def gtir(self, instruction):
        """
        gtir (greater-than immediate/register) sets register C to 1 if value A is greater than register B. Otherwise,
        register C is set to 0.
        """
        if instruction.a > self.registers[instruction.b]:
            self.set_register(instruction.output, 1)
        else:
            self.set_register(instruction.output, 0)

    def gtri(self, instruction):
        """
        gtri (greater-than register/immediate) sets register C to 1 if register A is greater than value B. Otherwise,
        register C is set to 0.
        """
        if self.registers[instruction.a] > instruction.b:
            self.set_register(instruction.output, 1)
        else:
            self.set_register(instruction.output, 0)

    def gtrr(self, instruction):
        """
        gtrr (greater-than register/register) sets register C to 1 if register A is greater than register B. Otherwise,
        register C is set to 0.
        """
        if self.registers[instruction.a] > self.registers[instruction.b]:
            self.set_register(instruction.output, 1)
        else:
            self.set_register(instruction.output, 0)

    def eqir(self, instruction):
        """
        eqir (equal immediate/register) sets register C to 1 if value A is equal to register B. Otherwise, register C is
        set to 0.
        """
        if instruction.a == self.registers[instruction.b]:
            self.set_register(instruction.output, 1)
        else:
            self.set_register(instruction.output, 0)

    def eqri(self, instruction):
        """
        eqri (equal register/immediate) sets register C to 1 if register A is equal to value B. Otherwise, register C is
        set to 0.
        """
        if self.registers[instruction.a] == instruction.b:
            self.set_register(instruction.output, 1)
        else:
            self.set_register(instruction.output, 0)

    def eqrr(self, instruction):
        """
        eqrr (equal register/register) sets register C to 1 if register A is equal to register B. Otherwise, register C
        is set to 0.
        """
        if self.registers[instruction.a] == self.registers[instruction.b]:
            self.set_register(instruction.output, 1)
        else:
            self.set_register(instruction.output, 0)


class ChronalDeviceWithJumps(ChronalDevice):

    def __init__(self, registers=None):
        super().__init__()

        self.program_register = 0
        if not registers:
            self.registers = [0] * 6
        else:
            self.registers = registers

    def execute_instructions(self, instructions):
        gen = self._execute_instructions(instructions)
        while True:
            try:
                next(gen)
            except StopIteration:
                break

    def execute_instructions_with_analysis(self, instructions):
        gen = self._execute_instructions(instructions)
        while True:
            try:
                yield next(gen)
            except StopIteration:
                yield None
                break

    @property
    def pc(self):
        return self.registers[self.program_register]

    @pc.setter
    def pc(self, i):
        self.registers[self.program_register] = i

    def inc_pc(self):
        self.registers[self.program_register] += 1

    def _execute_instructions(self, instructions):
        """
        When the instruction pointer is bound to a register, its value is written to that register just before each
        instruction is executed, and the value of that register is written back to the instruction pointer immediately
        after each instruction finishes execution. Afterward, move to the next instruction by adding one to the
        instruction pointer, even if the value in the instruction pointer was just updated by an instruction. (Because
        of this, instructions must effectively set the instruction pointer to the instruction before the one they want
        executed next.)
        """
        if type(instructions[0]) == JumpInstruction:
            self.program_register = instructions[0].program_register
            instructions.pop(0)
        else:
            raise Exception("Expected first instruction to set program register")

        while True:

            if self.pc >= len(instructions):
                break

            instruction = instructions[self.pc]

            self.execute(instruction)
            self.pc += 1

            yield instruction


class TestDeviceWithJumps(unittest.TestCase):

    def setUp(self):
        self.test_instructions = JumpInstruction.instructions_from_file("../input/day_19_test.txt")

    def test_execute_instructions(self):
        device = ChronalDeviceWithJumps()
        device.execute_instructions(self.test_instructions)

        assert device.registers == [7, 5, 6, 0, 0, 9]

    def test_execute_with_analysis(self):
        device = ChronalDeviceWithJumps()
        program = device.execute_instructions_with_analysis(self.test_instructions)

        instruction = next(program)
        while instruction:
            instruction = next(program)

        assert device.registers == [7, 5, 6, 0, 0, 9]
