# C.O.A.L. : Computer Organization Assembly Lanugage

**COAL** is a python program For the University of Utah's CS 3810 Computer Organization course. It turns MIPS style assembly code into machine code useable in Circuitverse RAM blocks. **COAL** Requires Python 3.

### How to Use:
Navigate to the folder that holds `coal.py` inside a terminal. Easiest way to do this on windows is to open the folder that holds it, right click the folder, and choose "open in terminal". To run the program, type:
```shell
python coal.py -i [FILE PATH HERE]
```

If you wish to output to a file, add `-o [OUTPUT PATH HERE]`. To run with debug, add `-d`.

**COAL** has support for 4 registers, `r0` through `r3`. No need to add a `$` before registers. Additionally, there is support for labels, defined as `label:` on its own line. **COAL** does not care about capitalization anywhere, so `label:` and `LABEL:` will both be the same entry, so will `r0` and `R0`, and `add` and `ADD`. For comments, the `#` symbol marks the start of a comment. Comments persist through the rest of the line.

## Examples: (Pulled from Assignment 8 page)
```
  andi  r0, r0, 0 
  addi  r2, r0, 5  
  addi  r1, r0, 1  
loop:
  add   r0, r0, r1 
  addi  r1, r1, 1  
  blt   r1, r2, loop
  halt
```
```
0x0011,0x0955,0x0455,0x0414,0x1455,0x18ce,0x000f
```
#
```
andi r0, r0, 0  # put 0 into r0
addi r1, r0, 1  # put 1 into r1
addi r2, r0, 5  # put 5 into r2
sw   r2, 3(r1)  # store 5 into address 4 (r1 + 3)
lw   r3, 3(r1)  # loads from address 4
halt
```
```
0x0011,0x0455,0x0955,0x18e5,0x1cf5,0x000f
```