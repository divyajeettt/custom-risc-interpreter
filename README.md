# custom-risc-interpreter

## About custom-risc-interpreter

custom-risc-interpreter is an Interpreter (Assembler and Simulator) for a custom [Reduced Instruction Set Architecture](https://en.wikipedia.org/wiki/Reduced_instruction_set_computer) (for [Assembly](https://en.wikipedia.org/wiki/Assembly_language)). It is a command-line based project developed as a Project Assignment for the course [<b>CSE112: *Computer Organization*</b>](http://techtree.iiitd.edu.in/viewDescription/filename?=CSE112). The deliverables of the project have also been pushed to this repository. 

This project fetched an <b>A+</b> grade and passed all Run-Time Test Cases provided at the time of project demonstration.

## Some Key Features

### SimpleAssembler

The Simple-Assembler reads input (from stdin) until and EOF is encountered. It scans over and parses the input multiple times. If the code is syntactically correct, and error free, the code is translated into a binary (*machine code*). The generated machine code is given as output (to stdout).

It also raises errors like End-of-File, Syntax, or Memory-Overflow, if present in the file, along with a Traceback to the line where the issue was found. An erronous code cannot be *compiled* into machine code by the Assembler.

### SimpleSimulator

The Simple-Simulator reads input (from stdin) until the code for `hlt` instruction is encountered. It then simulates a 256-Byte long memory, which stores machine code, variable values and an instruction pointer according to the schematics. It keeps track of all 8 available registers, and outputs each register's state after an instruction is executed (to stdout). 

It also generates a Memory-Trace, a plot of the memory-addresses accessed during the run-time of the code.

### Memory

This part of the project is separate from the other two and deals with hardware details of a machine like number of pins in the CPU, and how to change between them.

## The Instruction Set Architecture

## Run

Clone the repository on your device and navigate to the folder.

To run the Assembler, run:
```
python3 .\Code-Files\SimpleAssembler.py
```

To run the Simulator, run:
```
python3 .\Code-Files\SimpleSimulator.py
```

To run the Memory file, run:
```
python3 .\Code-Files\Memory.py
```

## Future Plans

- Change Simple-Assembler and Simple-Simulator to be case-insensitive (easy fix)
- Addition of more (RISC) instructions
