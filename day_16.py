from dataclasses import dataclass, field
from copy import copy
from elfsembly.device import ChronalDevice
from elfsembly.instruction import Instruction
import re
import unittest


def number_grabber(string):
    return [int(s) for s in re.findall(r"\d+", string)]


class InstructionGuesser:

    @dataclass
    class Guess:
        opcode: int = -1
        guesses: set = field(default_factory=lambda: set())

    @classmethod
    def guess(cls, before, after, instruction):
        guess = InstructionGuesser.Guess(opcode=instruction.opcode)
        test_device = ChronalDevice()

        methods = [
            test_device.addi,
            test_device.addr,
            test_device.bani,
            test_device.banr,
            test_device.bori,
            test_device.borr,
            test_device.eqir,
            test_device.eqri,
            test_device.eqrr,
            test_device.gtir,
            test_device.gtri,
            test_device.gtrr,
            test_device.muli,
            test_device.mulr,
            test_device.seti,
            test_device.setr,
        ]

        for method in methods:
            test_device.registers = copy(before)
            method(instruction)
            if test_device.registers[instruction.output] == after[instruction.output]:
                guess.guesses.add(method.__name__)

        return guess

    @classmethod
    def guess_from_lines(cls, lines):
        before = number_grabber(lines[0])
        instruction = Instruction.instruction_from_string(lines[1])
        after = number_grabber(lines[2])

        return InstructionGuesser.guess(before=before, after=after, instruction=instruction)

    @classmethod
    def guesses_from_file(cls, filepath):
        with open(filepath) as f:
            lines = [line.strip() for line in f.readlines()]

        guesses = []
        for i in range(0, len(lines), 4):
            guesses.append(
                InstructionGuesser.guess_from_lines(lines[i: i + 3])
            )

        return guesses


class TestInstructionGuesser(unittest.TestCase):

    def test_guess_from_lines(self):
        lines = [
            "Before: [3, 2, 1, 1]",
            "9 2 1 2",
            "After:  [3, 2, 2, 1]",
        ]

        assert InstructionGuesser.guess_from_lines(lines).guesses == {'addi', 'mulr', 'seti'}

    def test_part_1(self):
        guesses = InstructionGuesser.guesses_from_file("input/day_16_pt1.txt")
        print("Part 1:", sum([1 for guess in guesses if len(guess.guesses) >= 3]))

    def test_part_2(self):
        pass

    def test_find_unique_results(self):
        """
        See ChronalDevice.opcode_map for results of this method
        """
        guesses = InstructionGuesser.guesses_from_file("input/day_16_pt1.txt")
        guesses.sort(key=lambda g: len(g.guesses))
        opcodes = dict()

        while True:
            for guess in guesses:
                if guess.opcode in opcodes:
                    continue

                if len(guess.guesses) == 1:
                    opcodes[guess.opcode] = guess.guesses.pop()

                for solved in opcodes.values():
                    if solved in guess.guesses:
                        guess.guesses.remove(solved)

            if len(opcodes) == 16:
                break

        # for item in sorted(opcodes.items(), key=lambda kv: kv[0]):
        #     print(item)


class TestChronalDevice(unittest.TestCase):

    def test_execute_instructions(self):
        instructions = Instruction.instructions_from_file("input/day_16_pt2.txt")
        device = ChronalDevice()
        device.execute_instructions(instructions)

        print("Part 2:", device.registers[0])


"""
--- Day 16: Chronal Classification ---

As you see the Elves defend their hot chocolate successfully, you go back to falling through time. This is going to
become a problem.

If you're ever going to return to your own time, you need to understand how this device on your wrist works. You have a
little while before you reach your next destination, and with a bit of trial and error, you manage to pull up a
programming manual on the device's tiny screen.

According to the manual, the device has four registers (numbered 0 through 3) that can be manipulated by instructions
containing one of 16 opcodes. The registers start with the value 0.

Every instruction consists of four values: an opcode, two inputs (named A and B), and an output (named C), in that
order. The opcode specifies the behavior of the instruction and how the inputs are interpreted. The output, C, is always
treated as a register.

In the opcode descriptions below, if something says "value A", it means to take the number given as A literally. (This
is also called an "immediate" value.) If something says "register A", it means to use the number given as A to read from
(or write to) the register with that number. So, if the opcode addi adds register A and value B, storing the result in
register C, and the instruction addi 0 7 3 is encountered, it would add 7 to the value contained by register 0 and store
the sum in register 3, never modifying registers 0, 1, or 2 in the process.

Many opcodes are similar except for how they interpret their arguments. The opcodes fall into seven general categories:

Addition:

addr (add register) stores into register C the result of adding register A and register B.
addi (add immediate) stores into register C the result of adding register A and value B.
Multiplication:

mulr (multiply register) stores into register C the result of multiplying register A and register B.
muli (multiply immediate) stores into register C the result of multiplying register A and value B.
Bitwise AND:

banr (bitwise AND register) stores into register C the result of the bitwise AND of register A and register B.
bani (bitwise AND immediate) stores into register C the result of the bitwise AND of register A and value B.
Bitwise OR:

borr (bitwise OR register) stores into register C the result of the bitwise OR of register A and register B.
bori (bitwise OR immediate) stores into register C the result of the bitwise OR of register A and value B.
Assignment:

setr (set register) copies the contents of register A into register C. (Input B is ignored.)
seti (set immediate) stores value A into register C. (Input B is ignored.)
Greater-than testing:

gtir (greater-than immediate/register) sets register C to 1 if value A is greater than register B. Otherwise, register C
is set to 0.
gtri (greater-than register/immediate) sets register C to 1 if register A is greater than value B. Otherwise, register C
is set to 0.
gtrr (greater-than register/register) sets register C to 1 if register A is greater than register B. Otherwise, register
C is set to 0.
Equality testing:

eqir (equal immediate/register) sets register C to 1 if value A is equal to register B. Otherwise, register C is set to
0.
eqri (equal register/immediate) sets register C to 1 if register A is equal to value B. Otherwise, register C is set to
0.
eqrr (equal register/register) sets register C to 1 if register A is equal to register B. Otherwise, register C is set
to 0.
Unfortunately, while the manual gives the name of each opcode, it doesn't seem to indicate the number. However, you can
monitor the CPU to see the contents of the registers before and after instructions are executed to try to work them out.
Each opcode has a number from 0 through 15, but the manual doesn't say which is which. For example, suppose you capture
the following sample:

Before: [3, 2, 1, 1]
9 2 1 2
After:  [3, 2, 2, 1]

This sample shows the effect of the instruction 9 2 1 2 on the registers. Before the instruction is executed, register 0
has value 3, register 1 has value 2, and registers 2 and 3 have value 1. After the instruction is executed, register 2's
value becomes 2.

The instruction itself, 9 2 1 2, means that opcode 9 was executed with A=2, B=1, and C=2. Opcode 9 could be any of the
16 opcodes listed above, but only three of them behave in a way that would cause the result shown in the sample:

Opcode 9 could be mulr: register 2 (which has a value of 1) times register 1 (which has a value of 2) produces 2, which
matches the value stored in the output register, register 2.
Opcode 9 could be addi: register 2 (which has a value of 1) plus value 1 produces 2, which matches the value stored in
the output register, register 2.
Opcode 9 could be seti: value 2 matches the value stored in the output register, register 2; the number given for B is
irrelevant.

None of the other opcodes produce the result captured in the sample. Because of this, the sample above behaves like
three opcodes.

You collect many of these samples (the first section of your puzzle input). The manual also includes a small test
program (the second section of your puzzle input) - you can ignore it for now.

Ignoring the opcode numbers, how many samples in your puzzle input behave like three or more opcodes?
"""

