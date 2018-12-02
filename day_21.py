from elfsembly.device import ChronalDeviceWithJumps, JumpInstruction
import unittest


class TestConversion(unittest.TestCase):

    def test_part_1(self):
        """
        I figured out part 1 by just watching the registers; 103548 is the first value that is compared
        with r0, so if r0 is 103548 then it just stops quickly after the first runthrough.
        """
        device = ChronalDeviceWithJumps([103548, 0, 0, 0, 0, 0])
        program = device.execute_instructions_with_analysis(
            JumpInstruction.instructions_from_file("input/day_21.txt"))

        instruction = next(program)
        while instruction:
            instruction = next(program)

            # optimization
            if device.pc == 19:
                device.registers[5] = device.registers[3] // 256

    def test_part_2(self):
        device = ChronalDeviceWithJumps([0, 0, 0, 0, 0, 0])
        program = device.execute_instructions_with_analysis(
            JumpInstruction.instructions_from_file("input/day_21.txt"))

        instruction = next(program)
        seen = set()
        last = device.registers[4]

        while instruction:
            instruction = next(program)

            # optimization
            if device.pc == 19:
                device.registers[5] = device.registers[3] // 256

            # keep track of what we're comparing with r0 and find a loop
            if device.pc == 29:
                if device.registers[4] in seen:
                    break
                else:
                    seen.add(device.registers[4])
                    last = device.registers[4]

        print("Part 2:", last)
        assert last == 14256686



"""
Notes:

  #ip 1                     # pc = r1
  0: seti 123 0 4           # r4 = 123
  1: bani 4 456 4           # r4 &= 456 (72)
  2: eqri 4 72 4            # r4 = r4 == 72
  3: addr 4 1 1             # r1 = r4 + r1
  4: seti 0 0 1             # r1 = 0
  5: seti 0 2 4             # r4 = 0
  6: bori 4 65536 3         # r3 = r4 | 65536
  7: seti 10552971 1 4      # r4 = 10552971
  8: bani 3 255 5           # r5 = r3 & 255
  9: addr 4 5 4             # r4 += r5
 10: bani 4 16777215 4      # r4 &= 16777215    wat
 11: muli 4 65899 4         # r4 *= 65899       wat
 12: bani 4 16777215 4      # r4 &= 16777215    wat
 13: gtir 256 3 5           # r5 = r3 > 256  CONDITIONAL
 14: addr 5 1 1             # pc += r5, skip line 15
 15: addi 1 1 1             # pc += 1, skip line 16
 16: seti 27 7 1            # pc = 27, I bet this is the exit
 17: seti 0 1 5             # r5 = 0          
 18: addi 5 1 2             # r2 = r5 + 1 LOOP START
 19: muli 2 256 2           # r2 *= 256
 20: gtrr 2 3 2             # r2 = r2 > r3  EXIT LOOP IF R2 > R3
 21: addr 2 1 1             # pc += r2, this is a skip
 22: addi 1 1 1             # pc += 1
 23: seti 25 0 1            # pc = 25  
 24: addi 5 1 5             # r5 += 1
 25: seti 17 2 1            # pc = 17  LOOP END
 26: setr 5 7 3             # r3 = r5 
 27: seti 7 8 1             # pc = 7  LOOP
 28: eqrr 4 0 5             # r5 = r4 == r0  CONDITIONAL
 29: addr 5 1 1             # pc += r5  SKIP (this is a guaranteed exit) 
 30: seti 5 0 1             # pc = 5  LOOP

--- Day 21: Chronal Conversion ---
You should have been watching where you were going, because as you wander the new North Pole base, you trip and fall
into a very deep hole!

Just kidding. You're falling through time again.

If you keep up your current pace, you should have resolved all of the temporal anomalies by the next time the device
activates. Since you have very little interest in browsing history in 500-year increments for the rest of your life, you
need to find a way to get back to your present time.

After a little research, you discover two important facts about the behavior of the device:

First, you discover that the device is hard-wired to always send you back in time in 500-year increments. Changing this
is probably not feasible.

Second, you discover the activation system (your puzzle input) for the time travel module. Currently, it appears to run
forever without halting.

If you can cause the activation system to halt at a specific moment, maybe you can make the device send you so far back
in time that you cause an integer underflow in time itself and wrap around back to your current time!

The device executes the program as specified in manual section one and manual section two.

Your goal is to figure out how the program works and cause it to halt. You can only control register 0; every other
register begins at 0 as usual.

Because time travel is a dangerous activity, the activation system begins with a few instructions which verify that
bitwise AND (via bani) does a numeric operation and not an operation as if the inputs were interpreted as strings. If
the test fails, it enters an infinite loop re-running the test instead of allowing the program to execute normally. If
the test passes, the program continues, and assumes that all other bitwise operations (banr, bori, and borr) also
interpret their inputs as numbers. (Clearly, the Elves who wrote this system were worried that someone might introduce a
bug while trying to emulate this system with a scripting language.)

What is the lowest non-negative integer value for register 0 that causes the program to halt after executing the fewest
instructions? (Executing the same instruction multiple times counts as multiple instructions executed.)
"""
