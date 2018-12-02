from dataclasses import dataclass
from util import number_grabber
import unittest


@dataclass
class Instruction:

    opcode: int = 0
    a: int = 0
    b: int = 0
    output: int = 0

    str_to_int = {
         "gtir": 0,
         "mulr": 1,
         "seti": 2,
         "gtrr": 3,
         "bori": 4,
         "borr": 5,
         "banr": 6,
         "eqri": 7,
         "bani": 8,
         "addr": 9,
         "addi": 10,
         "eqrr": 11,
         "gtri": 12,
         "eqir": 13,
         "setr": 14,
         "muli": 15,
    }

    int_to_str = {
         0: "gtir",
         1: "mulr",
         2: "seti",
         3: "gtrr",
         4: "bori",
         5: "borr",
         6: "banr",
         7: "eqri",
         8: "bani",
         9: "addr",
         10: "addi",
         11: "eqrr",
         12: "gtri",
         13: "eqir",
         14: "setr",
         15: "muli",
    }

    @classmethod
    def instruction_from_string(cls, string):
        return Instruction(*number_grabber(string))

    @classmethod
    def instructions_from_file(cls, filename):
        with open(filename) as f:
            instructions = [
                Instruction.instruction_from_string(line.strip())
                for line in f.readlines()
            ]

        return instructions

    def __str__(self):
        return f"[" \
            f"{Instruction.int_to_str[self.opcode]}, " \
            f"a={self.a:3d}, b={self.b:3d}, " \
            f"output={self.output:3d}]"

    def __hash__(self):
        return hash(self.inst_to_tuple())

    def inst_to_tuple(self):
        return self.opcode, self.a, self.b, self.output


@dataclass
class JumpInstruction(Instruction):

    program_register: int = 0

    @classmethod
    def instruction_from_string(cls, string):
        if string[:3] == '#ip':
            return JumpInstruction(program_register=number_grabber(string)[0])
        else:
            opcode = Instruction.str_to_int[string[:4]]
            numbers = number_grabber(string)
            return Instruction(
                opcode=opcode,
                a=numbers[0],
                b=numbers[1],
                output=numbers[2],
            )

    @classmethod
    def is_jump_instruction(cls, line):
        return line[:3] == "#ip"

    @classmethod
    def instructions_from_file(cls, filename):
        instructions = list()
        with open(filename) as f:
            for line in f.readlines():
                instruction = JumpInstruction.instruction_from_string(line)
                instructions.append(instruction)

        return instructions


class TestJumpInstruction(unittest.TestCase):

    def test_instructions_from_file(self):
        instructions = JumpInstruction.instructions_from_file("../input/day_19.txt")

        assert len(instructions) == 8
