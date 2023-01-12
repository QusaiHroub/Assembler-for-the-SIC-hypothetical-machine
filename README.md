# Assembler for the SIC hypothetical machine

## Objective of this project
The project is a simulation to the assembler of the SIC hypothetical machine. This project implement both Pass1 and Pass2 of the SIC assembler language.

## This assembler consider all the following issues:

* **Directives**: START, END, BYTE, WORD, RESB, RESW, LTORG
* **Comments**: If a source line contains a period (.) in the first byte, the entire line is treated as a comment.
* **Addressing modes**: Simple, Indirect
* **Instruction Set**
* **Literals**:
* **Errors**: This Assembler flag all expected the errors

### The output of Pass 1 is:
1. Symbol Table SYBTAB: Displayed on the screen.
2. LOCCTR, PRGLTH, PRGNAME, ...
3. Intermediate file (.mdt): Stored on the secondary storage.
### The output of Pass 2:
1. The object file (.obj)
2. The listing file (.lst): listing.lst
3. List of errors if happened (duplicate labels, invalid mnemonic, inappropriate operand...).
### This assembler expeced source code to have a fixed format, so your code should be committed to the following dimensions:
#### Columns:
```
1-10 Label
11-11 Blank
12-20 Operation code (or Assembler directive)
21-21 Blank
22-39 Operand
40-70 Comment
```

## Use
### To run pass1:
```
python main.py pass1 ./test.asm test.mdt  
```
### To run pass2:
```
python main.py pass2 ./test.mdt test.obj
```
