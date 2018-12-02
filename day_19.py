from collections import Counter, deque

from elfsembly.device import ChronalDeviceWithJumps
from elfsembly.instruction import JumpInstruction

import unittest


def fastforward_state(device):
    """
    Just gonna let python do the factoring instead of the elfcode.
    """
    r0, r1, r2, r3, r4, r5 = device.registers
    while r4 <= r2:
        if r2 % r4 == 0:
            r0 += r4
        r4 += 1
    device.registers = [r0, r1, r2, r3, r4, r5]
    device.pc = 13


class TestSpeculativeElfsecution(unittest.TestCase):

    def setUp(self):
        self.instructions = JumpInstruction.instructions_from_file("input/day_19.txt")

    def test_part_1(self):
        device = ChronalDeviceWithJumps()
        program = device.execute_instructions_with_analysis(self.instructions)

        instruction = next(program)
        while instruction:

            if device.pc == 2 and device.registers[4] != 0:
                fastforward_state(device)
                continue

            instruction = next(program)

        print("Part 1:", device.registers[0])

    def test_part_2(self):
        device = ChronalDeviceWithJumps([1, 0, 0, 0, 0, 0])
        program = device.execute_instructions_with_analysis(self.instructions)

        instruction = next(program)
        while instruction:

            if device.pc == 2 and device.registers[4] != 0:
                fastforward_state(device)
                continue

            instruction = next(program)

        print("Part 2:", device.registers[0])


"""
PRELOOP
seti 1 5 3  # immediately sets R3 to 1

LOOOP
3  mulr 4 3 1  # saves R4 * R3 to R1
4  eqrr 1 2 1  # compares R1 (R4 * R3) to R2, saves to R1
5  addr 1 5 5  # Adds R1 to R5 (THIS SKIPS 7, make this a conditional?)
6  addi 5 1 5  # Adds 1
7  addr 4 0 0  # Adds R1 and R0, saves to R0
8  addi 3 1 3  # Adds 1 to R3
9  gtrr 3 2 1  # Checks to see if R3 is > R2, saves 1 or 0 to R1
10 addr 5 1 5  # Adds R1 (0 or 1) to PC -- If the prior gtrr is 0, we're going back to the beginning
11 seti 2 5 5  # Sets R5 (PC) to 2+1, so we go back to mulr 



---------
R3 = 1 # seti 1 5 3
while R3 <= R2 # gtrr 3 2 1  
LOOP
R1 = R4 * R3
R1 = 
    if R4 * R3 == R2:  # mulr 4 3 1, eqrr 1 2 1 

        R1 = 1
    else:
        R1 = 0
    R3 += 1
END 

OH. Oh oh oh. This thing is just summing factored numbers. 
If 3 * 4 == 2, 0 += 4. That's the loop.  

[1, 2, 5, 10, 1055143, 2110286, 5275715, 10551430]

"""

"""
PRE


2: R3 = 1 [0, 10550400, 10551430, 1, 1, 3]

LOOP

 3: R1 = R4 * R3
 4: R1 = R1 == R2 (0 or 1)
 5: PC += R1 (this will mostly be 0)
 6: PC += 1 (skips 7)
 7: R0 += R4
 8: R3 += 1
 9: R1 = R3 > R2 (0 or 1)
10: PC += R1 (stop if R3 > R2)
11: PC = 2

if PC == 2 and R4 != 0:
    R1 = R4 * R3 == R2
    if R4 * R3 == R2:
        R0 += R4
    R1 = 1
    R3 = R2
    PC = 12
    continue
    

factors = [10551430]
for i in range(1, 10551430):
    if 10551430 % i == 0:
        factors.append(i)
        
print("RO:", sum(factors))

^^ that's the program

Notes: 
- Program starts immediately jumps to 17 and executes from 17 to 35
- The debug output below has the PC too low by 1 due to when I yield in the loop
- First internal loop is 3 to 11 

Flow: 
program counter register is 5 
------------
0: [1, 0, 0, 0, 0, 0] [addi, a=5, b=16, output=5] [1, 0, 0, 0, 0, 17]
add 16 to register 5 (0), landing us at 16, and then incrementing by 1

1: [1, 0, 0, 0, 0, 17] [addi, a=2, b=2, output=2] [1, 0, 2, 0, 0, 18]
add 2 to register 2 (2), setting register 2 to 4

2: [1, 0, 2, 0, 0, 18] [mulr, a=2, b=2, output=2] [1, 0, 4, 0, 0, 19]
multiply register 2 (2) by register 2 (2), set register 2 to 4

3: [1, 0, 4, 0, 0, 19] [mulr, a=5, b=2, output=2] [1, 0, 76, 0, 0, 20]
multiply register 5 (19) by register 2 (4), set register 2 to 76

4: [1, 0, 76, 0, 0, 20] [muli, a=2, b=11, output=2] [1, 0, 836, 0, 0, 21]
multiply register 2 (76) by value b (11), set register 2 to 836

5: [1, 0, 836, 0, 0, 21] [addi, a=1, b=8, output=1] [1, 8, 836, 0, 0, 22]
add register 1 (0) with value b (8), set register 1 to 8

6: [1, 8, 836, 0, 0, 22] [mulr, a=1, b=5, output=1] [1, 176, 836, 0, 0, 23]
multiply register 1 (8) with register 5 (23), set register 1 to 176

7: [1, 176, 836, 0, 0, 23] [addi, a=1, b=18, output=1] [1, 194, 836, 0, 0, 24]
add register 1 (176) to value b (18), set register 1 to 194

8: [1, 194, 836, 0, 0, 24] [addr, a=2, b=1, output=2] [1, 194, 1030, 0, 0, 25]
add register 2 (836) to register 1 (194), set register 2 to 1030

9: [1, 194, 1030, 0, 0, 25] [addr, a=5, b=0, output=5] [1, 194, 1030, 0, 0, 27]
add register 5 (25) to register 0 (1), set register 5 to 26 + 1 (this just skips one instruction)

10: [1, 194, 1030, 0, 0, 27] [setr, a=5, b=0, output=1] [1, 27, 1030, 0, 0, 28]
copy register 5 (27) to register 1 

11: [1, 27, 1030, 0, 0, 28] [mulr, a=1, b=5, output=1] [1, 756, 1030, 0, 0, 29]
multiply register 1 (27) by register 5 (28), set register 1 to 756

12: [1, 756, 1030, 0, 0, 29] [addr, a=5, b=1, output=1] [1, 785, 1030, 0, 0, 30]
add register 5 (29) to register 1 (756), set register 1 to 785

13: [1, 785, 1030, 0, 0, 30] [mulr, a=5, b=1, output=1] [1, 23550, 1030, 0, 0, 31]
multiply register 5 (30) by register 1 (785), set register 1 to 23550

14: [1, 23550, 1030, 0, 0, 31] [muli, a=1, b=14, output=1] [1, 329700, 1030, 0, 0, 32]
multiply register 1 (23550) by value b (14), set register 1 to 329700

15: [1, 329700, 1030, 0, 0, 32] [mulr, a=1, b=5, output=1] [1, 10550400, 1030, 0, 0, 33]
multiply register 1 (329700) by register 5 (32), set register 1 to 10550400

16: [1, 10550400, 1030, 0, 0, 33] [addr, a=2, b=1, output=2] [1, 10550400, 10551430, 0, 0, 34]
add register 2 (1030) to register 1 (10550400), set register 2 to 10551430

17: [1, 10550400, 10551430, 0, 0, 34] [seti, a=0, b=0, output=0] [0, 10550400, 10551430, 0, 0, 35]
set register 0 (1) to value a (0), set register 0 to 0 

18: [0, 10550400, 10551430, 0, 0, 35] [seti, a=0, b=9, output=5] [0, 10550400, 10551430, 0, 0, 1]
set register 5 (35) to value a (0) + 1 for pc increment  

19: [0, 10550400, 10551430, 0, 0, 1] [seti, a=1, b=8, output=4] [0, 10550400, 10551430, 0, 1, 2]
set register 4 (0) to value a (1), set register 4 to 1

20: [0, 10550400, 10551430, 0, 1, 2] [seti, a=1, b=5, output=3] [0, 10550400, 10551430, 1, 1, 3]
set register 3 (0) to value a (1), set register 3 to 1

21: [0, 10550400, 10551430, 1, 1, 3] [mulr, a=4, b=3, output=1] [0, 1, 10551430, 1, 1, 4]
multiply register 4 (1) by register 3 (1), set register 1 to 1

** This is the start of a loop ** 

22: [0, 1, 10551430, 1, 1, 4] [eqrr, a=1, b=2, output=1] [0, 0, 10551430, 1, 1, 5]
check if register 1 (1) is equal to register 2 (10551430), it is not, set register 1 to 0

*** This check is important; it's what is keeping us in this loop ***

23: [0, 0, 10551430, 1, 1, 5] [addr, a=1, b=5, output=5] [0, 0, 10551430, 1, 1, 6]
add register 1 (0) to register 5 (5), set register 5 to 5 + 1 for PC

If register 0 was 1, we would have set the PC to 6 + 1 for PC and ended up at the instruction we skip, which
is: addr 4 0 0. In that case, we'd set += register 0 with register 4, adding 1 to register 0. 

24: [0, 0, 10551430, 1, 1, 6] [addi, a=5, b=1, output=5] [0, 0, 10551430, 1, 1, 8]
add register 5 (6) to value b (1), set register 5 to 7 + 1 for PC

25: [0, 0, 10551430, 1, 1, 8] [addi, a=3, b=1, output=3] [0, 0, 10551430, 2, 1, 9]
add register 3 (1) to value b (1), set register 3 to 2

26: [0, 0, 10551430, 2, 1, 9] [gtrr, a=3, b=2, output=1] [0, 0, 10551430, 2, 1, 10]
check if register 3 (2) is greater than register 2 (10551430), it is not, set register 1 to 0

*** Second part of the check to see if we can escape the loop? ***

27: [0, 0, 10551430, 2, 1, 10] [addr, a=5, b=1, output=5] [0, 0, 10551430, 2, 1, 11]
add register 5 (10) to register 1 (0), set register 5 to 10 + 1 for PC 

If register 0 was 1, we'd end up at seti 2 5 5, which would add 2 to register 5, landing us at 
13 + 1 for 14, which is gtrr 4 2 1... I think. 

28: [0, 0, 10551430, 2, 1, 11] [seti, a=2, b=5, output=5] [0, 0, 10551430, 2, 1, 3]
set register 5 to value a (2) + 1 for PC, landing us back at 3

** This sends us back to the beginning of our loop **

29: [0, 0, 10551430, 2, 1, 3] [mulr, a=4, b=3, output=1] [0, 2, 10551430, 2, 1, 4]
heyyyy, we're back at the beginning of our loop.

----------------

** Run Two **

We're gonna set the starting memory to the beginning of one of these mulr loops but with 
register 3 set to the same value as register 2 so that when instruction 9 (gtrr) compares
the two we end up skipping out of this section to what I assume is the second loop. 

Setting the starting registers to: [0, 0, 10551430, 10551430, 1, 3]


0: [0, 0, 10551430, 10551430, 1, 3] [mulr, a=4, b=3, output=1] [0, 10551430, 10551430, 10551430, 1, 4]
Alright, back to our good buddy instruction 3. Going through our loop as usual.

1: [0, 10551430, 10551430, 10551430, 1, 4] [eqrr, a=1, b=2, output=1] [0, 1, 10551430, 10551430, 1, 5]
This is different from the other times we've done this loop; register 1 is holding our incrementing value,
and we've moved it to register 1. This time it IS equal to register 2, so we'll set register 1 to 1. New
territory here. 

2: [0, 1, 10551430, 10551430, 1, 5] [addr, a=1, b=5, output=5] [0, 1, 10551430, 10551430, 1, 7]
Add register 1 (1) to register 5 (5), save 6 + 1 to register 5. 

3: [0, 1, 10551430, 10551430, 1, 7] [addr, a=4, b=0, output=0] [1, 1, 10551430, 10551430, 1, 8]
Hey, instruction 7, that's new. += register 4 (1) to register 0(0).  

4: [1, 1, 10551430, 10551430, 1, 8] [addi, a=3, b=1, output=3] [1, 1, 10551430, 10551431, 1, 9]
At this point register 3 is finally higher than register 2. 

5: [1, 1, 10551430, 10551431, 1, 9] [gtrr, a=3, b=2, output=1] [1, 1, 10551430, 10551431, 1, 10]
We're checking to see if 3 is greater than 2, and it is. Save 1 to register 1.

6: [1, 1, 10551430, 10551431, 1, 10] [addr, a=5, b=1, output=5] [1, 1, 10551430, 10551431, 1, 12]
Adding register 5 (10) to register 1 (1), which skips 11 and gets us to 12, which is a new area of the 
program! We skip 11 here. 

7: [1, 1, 10551430, 10551431, 1, 12] [addi, a=4, b=1, output=4] [1, 1, 10551430, 10551431, 2, 13]
Now we're immediately adding 1 to register 4 (1), so register 4 is now 2. 

8: [1, 1, 10551430, 10551431, 2, 13] [gtrr, a=4, b=2, output=1] [1, 0, 10551430, 10551431, 2, 14]
We're seeing if register 4 (2) is greater than register 2 (10551430) and it is not. Save 0 to 
register 1. We're gonna keep doing this shit until register 4 is greater than register 2. When register 2
is finally greater than register 1, we will save 1 to register 1.

9: [1, 0, 10551430, 10551431, 2, 14] [addr, a=1, b=5, output=5] [1, 0, 10551430, 10551431, 2, 15]
Add register 1 to register 5; this gets us nothing, since register 1 is zero. 

*** This would be how we escape the loop.** 

If register 1 was one, we would skip to instruction 16, which squares register 5 and is guaranteed
to stop execution by setting the PC to 256. What register 0 is set to depends on instruction 7.

10: [1, 0, 10551430, 10551431, 2, 15] [seti, a=1, b=2, output=5] [1, 0, 10551430, 10551431, 2, 2]
Set register 5 to 1, plus 1 for PC. We're back to the early part of the program that slides into
our initial 3 -> 11 loop. (Except now we're skipping 7 again.)

11: [1, 0, 10551430, 10551431, 2, 2] [seti, a=1, b=5, output=3] [1, 0, 10551430, 1, 2, 3]
We're immediately setting register 3 (10551431) to 1, and then we're gonna start counting again.
This is kind of the instruction that restarts the whole loop. (And starts it the first time.) 

12: [1, 0, 10551430, 1, 2, 3] [mulr, a=4, b=3, output=1] [1, 2, 10551430, 1, 2, 4]
Yooo, buddy. Back to instruction 3. 

13: [1, 2, 10551430, 1, 2, 4] [eqrr, a=1, b=2, output=1] [1, 0, 10551430, 1, 2, 5]
14: [1, 0, 10551430, 1, 2, 5] [addr, a=1, b=5, output=5] [1, 0, 10551430, 1, 2, 6]
15: [1, 0, 10551430, 1, 2, 6] [addi, a=5, b=1, output=5] [1, 0, 10551430, 1, 2, 8]
16: [1, 0, 10551430, 1, 2, 8] [addi, a=3, b=1, output=3] [1, 0, 10551430, 2, 2, 9]
17: [1, 0, 10551430, 2, 2, 9] [gtrr, a=3, b=2, output=1] [1, 0, 10551430, 2, 2, 10]
18: [1, 0, 10551430, 2, 2, 10] [addr, a=5, b=1, output=5] [1, 0, 10551430, 2, 2, 11]
19: [1, 0, 10551430, 2, 2, 11] [seti, a=2, b=5, output=5] [1, 0, 10551430, 2, 2, 3]
... you get the idea

20: [1, 0, 10551430, 2, 2, 3] [mulr, a=4, b=3, output=1] [1, 4, 10551430, 2, 2, 4]
21: [1, 4, 10551430, 2, 2, 4] [eqrr, a=1, b=2, output=1] [1, 0, 10551430, 2, 2, 5]
22: [1, 0, 10551430, 2, 2, 5] [addr, a=1, b=5, output=5] [1, 0, 10551430, 2, 2, 6]
23: [1, 0, 10551430, 2, 2, 6] [addi, a=5, b=1, output=5] [1, 0, 10551430, 2, 2, 8]
24: [1, 0, 10551430, 2, 2, 8] [addi, a=3, b=1, output=3] [1, 0, 10551430, 3, 2, 9]

-------

** Run Three **

I let let this fucker run for a while. Here's our semi-incremented state.

49996: [1, 0, 10551430, 6249, 2, 3] [mulr, a=4, b=3, output=1] [1, 12498, 10551430, 6249, 2, 4]

Note that register 4 is still hanging out at 2, which means it's gonna be a damned long time before it's 
greater than register 2. We're in the middle of our normal loop trying to increment register 3, so I'm just 
gonna set that to a big number and watch it roll over. 

Starting with: [1, 0, 10551430, 10551430, 10551430, 3]
"""



"""
--- Day 19: Go With The Flow ---

Foo. With the Elves well on their way constructing the North Pole base, you turn your attention back to understanding
the inner workings of programming the device.

You can't help but notice that the device's opcodes don't contain any flow control like jump instructions. The device's
manual goes on to explain:

"In programs where flow control is required, the instruction pointer can be bound to a register so that it can be
manipulated directly. This way, setr/seti can function as absolute jumps, addr/addi can function as relative jumps, and
other opcodes can cause truly fascinating effects."

This mechanism is achieved through a declaration like #ip 1, which would modify register 1 so that accesses to it let
the program indirectly access the instruction pointer itself. To compensate for this kind of binding, there are now six
registers (numbered 0 through 5); the five not bound to the instruction pointer behave as normal. Otherwise, the same
rules apply as the last time you worked with this device.

When the instruction pointer is bound to a register, its value is written to that register just before each instruction
is executed, and the value of that register is written back to the instruction pointer immediately after each
instruction finishes execution. Afterward, move to the next instruction by adding one to the instruction pointer, even
if the value in the instruction pointer was just updated by an instruction. (Because of this, instructions must
effectively set the instruction pointer to the instruction before the one they want executed next.)

The instruction pointer is 0 during the first instruction, 1 during the second, and so on. If the instruction pointer
ever causes the device to attempt to load an instruction outside the instructions defined in the program, the program
instead immediately halts. The instruction pointer starts at 0.

It turns out that this new information is already proving useful: the CPU in the device is not very powerful, and a
background process is occupying most of its time. You dump the background process' declarations and instructions to a
file (your puzzle input), making sure to use the names of the opcodes rather than the numbers.

For example, suppose you have the following program:

#ip 0
seti 5 0 1
seti 6 0 2
addi 0 1 0
addr 1 2 3
setr 1 0 0
seti 8 0 4
seti 9 0 5

When executed, the following instructions are executed. Each line contains the value of the instruction pointer at the
time the instruction started, the values of the six registers before executing the instructions (in square brackets),
the instruction itself, and the values of the six registers after executing the instruction (also in square brackets).

ip=0 [0, 0, 0, 0, 0, 0] seti 5 0 1 [0, 5, 0, 0, 0, 0]
ip=1 [1, 5, 0, 0, 0, 0] seti 6 0 2 [1, 5, 6, 0, 0, 0]
ip=2 [2, 5, 6, 0, 0, 0] addi 0 1 0 [3, 5, 6, 0, 0, 0]
ip=4 [4, 5, 6, 0, 0, 0] setr 1 0 0 [5, 5, 6, 0, 0, 0]
ip=6 [6, 5, 6, 0, 0, 0] seti 9 0 5 [6, 5, 6, 0, 0, 9]

In detail, when running this program, the following events occur:

The first line (#ip 0) indicates that the instruction pointer should be bound to register 0 in this program. This is not
an instruction, and so the value of the instruction pointer does not change during the processing of this line.

The instruction pointer contains 0, and so the first instruction is executed (seti 5 0 1). It updates register 0 to the
current instruction pointer value (0), sets register 1 to 5, sets the instruction pointer to the value of register 0
(which has no effect, as the instruction did not modify register 0), and then adds one to the instruction pointer.

The instruction pointer contains 1, and so the second instruction, seti 6 0 2, is executed. This is very similar to the
instruction before it: 6 is stored in register 2, and the instruction pointer is left with the value 2.

The instruction pointer is 2, which points at the instruction addi 0 1 0. This is like a relative jump: the value of the
instruction pointer, 2, is loaded into register 0. Then, addi finds the result of adding the value in register 0 and the
value 1, storing the result, 3, back in register 0. Register 0 is then copied back to the instruction pointer, which
will cause it to end up 1 larger than it would have otherwise and skip the next instruction (addr 1 2 3) entirely.
Finally, 1 is added to the instruction pointer.

The instruction pointer is 4, so the instruction setr 1 0 0 is run. This is like an absolute jump: it copies the value
contained in register 1, 5, into register 0, which causes it to end up in the instruction pointer. The instruction
pointer is then incremented, leaving it at 6.

The instruction pointer is 6, so the instruction seti 9 0 5 stores 9 into register 5. The instruction pointer is
incremented, causing it to point outside the program, and so the program ends.

What value is left in register 0 when the background process halts?
"""

