import matplotlib.pyplot as plt
import os


def program_counter(pc: int) -> str:
    # Returns the binary representation of the PC
    return bin(pc)[2:].zfill(8)


def register(name: str) -> int:
    # Returns the address of that register
    return int(name.lstrip("R"))


def register_file(name: str) -> str:
    if name == "FLAGS":
        return REGISTER_FILE[7]
    else:
        return REGISTER_FILE[register(name)]


def get_instruction(pc: int) -> str:
    return MACHINE_CODE[pc]


def current_state() -> None:
    print(program_counter(PC), *REGISTER_FILE)


def handle_overflow() -> None:
    REGISTER_FILE[7] = "0"*12 + "1000"


def handle_comparison(value1: int, value2: int) -> None:
    if value1 == value2:
        REGISTER_FILE[7] = "0"*12 + "0001"
    elif value1 > value2:
        REGISTER_FILE[7] = "0"*12 + "0010"
    else:
        REGISTER_FILE[7] = "0"*12 + "0100"


def binf(immediate: float) -> str:
    mantissa = ""
    exponent = -5
    if not 1 <= immediate <= 252:
        handle_overflow()
        if immediate < 1:
            return "0"*8
        else:
            return "1"*8
    while 2**exponent <= immediate:
        exponent += 1
    exponent -= 1
    num = immediate / 2**exponent - 1
    for _ in range(5):
        num *= 2
        if num < 1:
            mantissa += "0"
        else:
            mantissa += "1"
            num -= 1
    if num != 0:
        handle_overflow()
    return bin(exponent)[2:] + mantissa


def handle_float(value: str) -> float:
    exponent, mantissa = value[:3], value[3:]
    value = 0
    for i in range(5):
        value += int(mantissa[i]) * 2**(-i-1)

    return (1 + value) * 2**int(exponent,base=2)

def type_A(instruction: str) -> list[str, str, str]:
    opcode = instruction[:5]
    reg1 = instruction[7:10]
    reg2 = instruction[10:13]
    reg3 = instruction[13:16]
    return REGISTERS[reg1], REGISTERS[reg2], REGISTERS[reg3]


def type_B(instruction: str) -> list[str, str]:
    opcode = instruction[:5]
    reg1 = instruction[5:8]
    imm = instruction[8:16]
    return REGISTERS[reg1], imm


def type_C(instruction: str) -> list[str, str]:
    opcode = instruction[:5]
    reg1 = instruction[10:13]
    reg2 = instruction[13:16]
    return REGISTERS[reg1], REGISTERS[reg2]


def type_D(instruction: str) -> list[str, str]:
    opcode = instruction[:5]
    reg1 = instruction[5:8]
    mem = instruction[8:16]
    return REGISTERS[reg1], mem


def type_E(instruction: str) -> str:
    opcode = instruction[:5]
    mem = instruction[8:16]
    return mem


def execution_engine(instruction: str, pc: int) -> tuple[int, bool]:
    opcode = instruction[:5]

    if opcode == "00000": # float addition
        reg1, reg2, reg3 = type_A(instruction)
        value1 = handle_float(register_file(reg1)[8:])
        value2 = handle_float(register_file(reg2)[8:])
        value = value1 + value2
        if not 1 <= value <= 256:
            handle_overflow()
            REGISTER_FILE[register(reg3)] = value % 2**8
        else:
            REGISTER_FILE[register(reg3)] = binf(value).zfill(16)
            REGISTER_FILE[7] = "0" * 16

        CYCLES.append(CYCLE)
        MEMORY_ACCESS.append(pc)
        pc += 1


    elif opcode == "00001": # float subtraction
        reg1, reg2, reg3 = type_A(instruction)
        value1 = handle_float(register_file(reg1)[8:])
        value2 = handle_float(register_file(reg2)[8:])

        value = value1 - value2

        if value1 < value2 - 1:
            handle_overflow()
            value = 0
        else:
            REGISTER_FILE[7] = "0" * 16

        REGISTER_FILE[register(reg3)] = binf(value).zfill(16) if value != 0 else "0"*16
        CYCLES.append(CYCLE)
        MEMORY_ACCESS.append(pc)
        pc += 1


    elif opcode == "10000": # addition
        reg1, reg2, reg3 = type_A(instruction)
        value1 = int(register_file(reg1), base=2)
        value2 = int(register_file(reg2), base=2)

        value = bin(value1 + value2)[2:].zfill(16)

        if len(value) > 16:
            handle_overflow()
            value = "1" * 16
        else:
            REGISTER_FILE[7] = "0" * 16

        REGISTER_FILE[register(reg3)] = value
        CYCLES.append(CYCLE)
        MEMORY_ACCESS.append(pc)
        pc += 1


    elif opcode == "10001": # subtraction
        reg1, reg2, reg3 = type_A(instruction)
        value1 = int(register_file(reg1), base=2)
        value2 = int(register_file(reg2), base=2)

        value = bin(value1 - value2)[2:].zfill(16)
        if value1 < value2:
            handle_overflow()
            value = "0" * 16
        else:
            REGISTER_FILE[7] = "0" * 16

        REGISTER_FILE[register(reg3)] = value
        CYCLES.append(CYCLE)
        MEMORY_ACCESS.append(pc)
        pc += 1


    elif opcode in {"10010", "00010"}: # move immediate or float
        reg1, imm = type_B(instruction)
        REGISTER_FILE[register(reg1)] = "0"*8 + imm
        REGISTER_FILE[7] = "0" * 16
        CYCLES.append(CYCLE)
        MEMORY_ACCESS.append(pc)
        pc += 1


    elif opcode == "10011": # move register
        reg1, reg2 = type_C(instruction)
        REGISTER_FILE[register(reg2)] = register_file(reg1)
        REGISTER_FILE[7] = "0" * 16
        CYCLES.append(CYCLE)
        MEMORY_ACCESS.append(pc)
        pc += 1


    elif opcode == "10100": # load
        reg1, mem = type_D(instruction)
        REGISTER_FILE[register(reg1)] = MEMORY[int(mem, base=2)]
        REGISTER_FILE[7] = "0" * 16

        CYCLES.append(CYCLE)
        CYCLES.append(CYCLE)
        MEMORY_ACCESS.append(pc)
        MEMORY_ACCESS.append(int(mem, base=2))

        pc += 1


    elif opcode == "10101": # store
        reg1, mem = type_D(instruction)
        MEMORY[int(mem, base=2)] = register_file(reg1)
        REGISTER_FILE[7] = "0" * 16

        CYCLES.append(CYCLE)
        CYCLES.append(CYCLE)
        MEMORY_ACCESS.append(pc)
        MEMORY_ACCESS.append(int(mem, base=2))

        pc += 1


    elif opcode == "10110": # multiply
        reg1, reg2, reg3 = type_A(instruction)
        value1 = int(register_file(reg1), base=2)
        value2 = int(register_file(reg2), base=2)

        value = bin(value1 * value2)[2:].zfill(16)

        if len(value) > 16:
            handle_overflow()
            value = "1" * 16
        else:
            REGISTER_FILE[7] = "0" * 16

        REGISTER_FILE[register(reg3)] = value
        CYCLES.append(CYCLE)
        MEMORY_ACCESS.append(pc)
        pc += 1


    elif opcode == "10111": # divide
        reg3, reg4 = type_C(instruction)
        value3 = int(register_file(reg3), base=2)
        value4 = int(register_file(reg4), base=2)

        REGISTER_FILE[0] = bin(value3 // value4)[2:].zfill(16)
        REGISTER_FILE[1] = bin(value3 % value4)[2:].zfill(16)
        REGISTER_FILE[7] = "0" * 16
        CYCLES.append(CYCLE)
        MEMORY_ACCESS.append(pc)
        pc += 1


    elif opcode == "11000": # right shift
        reg1, imm = type_B(instruction)
        value1 = int(register_file(reg1), base=2)
        value1 >>= int(imm, base=2)
        REGISTER_FILE[register(reg1)] = bin(value1)[2:].zfill(16)
        REGISTER_FILE[7] = "0" * 16
        CYCLES.append(CYCLE)
        MEMORY_ACCESS.append(pc)
        pc += 1


    elif opcode == "11001": # left shift
        reg1, imm = type_B(instruction)
        value1 = int(register_file(reg1), base=2)
        value1 <<= int(imm, base=2)
        REGISTER_FILE[register(reg1)] = bin(value1)[2:].zfill(16)
        REGISTER_FILE[7] = "0" * 16
        CYCLES.append(CYCLE)
        MEMORY_ACCESS.append(pc)
        pc += 1


    elif opcode == "11010": # XOR
        reg1, reg2, reg3 = type_A(instruction)
        value1 = int(register_file(reg1), base=2)
        value2 = int(register_file(reg2), base=2)

        value = bin(value1 ^ value2)[2:].zfill(16)

        REGISTER_FILE[register(reg3)] = value
        REGISTER_FILE[7] = "0" * 16
        CYCLES.append(CYCLE)
        MEMORY_ACCESS.append(pc)
        pc += 1


    elif opcode == "11011": # OR
        reg1, reg2, reg3 = type_A(instruction)
        value1 = int(register_file(reg1), base=2)
        value2 = int(register_file(reg2), base=2)

        value = bin(value1 | value2)[2:].zfill(16)

        REGISTER_FILE[register(reg3)] = value
        REGISTER_FILE[7] = "0" * 16
        CYCLES.append(CYCLE)
        MEMORY_ACCESS.append(pc)
        pc += 1


    elif opcode == "11100": # AND
        reg1, reg2, reg3 = type_A(instruction)
        value1 = int(register_file(reg1), base=2)
        value2 = int(register_file(reg2), base=2)

        value = bin(value1 & value2)[2:].zfill(16)

        REGISTER_FILE[register(reg3)] = value
        REGISTER_FILE[7] = "0" * 16
        CYCLES.append(CYCLE)
        MEMORY_ACCESS.append(pc)
        pc += 1


    elif opcode == "11101": # invert
        reg1, reg2 = type_C(instruction)
        value1 = register_file(reg1).replace("0", "_").replace("1", "0").replace("_", "1")
        REGISTER_FILE[register(reg2)] = value1.zfill(16)
        REGISTER_FILE[7] = "0" * 16
        CYCLES.append(CYCLE)
        MEMORY_ACCESS.append(pc)
        pc += 1


    elif opcode == "11110": # compare
        reg1, reg2 = type_C(instruction)
        value1 = int(register_file(reg1), base=2)
        value2 = int(register_file(reg2), base=2)
        handle_comparison(value1, value2)
        CYCLES.append(CYCLE)
        MEMORY_ACCESS.append(pc)
        pc += 1


    elif opcode == "11111": # unconditional jump
        mem = type_E(instruction)
        CYCLES.extend([CYCLE] * 2)
        MEMORY_ACCESS.extend([pc, int(mem, base=2)])
        pc = int(mem, base=2)
        REGISTER_FILE[7] = "0" * 16


    elif opcode == "01100": # jump if less than
        mem = type_E(instruction)
        CYCLES.append(CYCLE)
        MEMORY_ACCESS.append(pc)

        if REGISTER_FILE[7][-3] == "1":
            CYCLES.append(CYCLE)
            MEMORY_ACCESS.append(int(mem, base=2))

        pc = int(mem, base=2) if REGISTER_FILE[7][-3] == "1" else pc + 1
        REGISTER_FILE[7] = "0" * 16


    elif opcode == "01101": # jump if greater than
        mem = type_E(instruction)
        CYCLES.append(CYCLE)
        MEMORY_ACCESS.append(pc)

        if REGISTER_FILE[7][-2] == "1":
            CYCLES.append(CYCLE)
            MEMORY_ACCESS.append(int(mem, base=2))

        pc = int(mem, base=2) if REGISTER_FILE[7][-2] == "1" else pc + 1
        REGISTER_FILE[7] = "0" * 16


    elif opcode == "01111": # jump if equal
        mem = type_E(instruction)
        CYCLES.append(CYCLE)
        MEMORY_ACCESS.append(pc)

        if REGISTER_FILE[7][-1] == "1":
            CYCLES.append(CYCLE)
            MEMORY_ACCESS.append(int(mem, base=2))

        pc = int(mem, base=2) if REGISTER_FILE[7][-1] == "1" else pc + 1
        REGISTER_FILE[7] = "0" * 16


    else: #  HALT => stop program
        REGISTER_FILE[7] = "0" * 16
        CYCLES.append(CYCLE)
        MEMORY_ACCESS.append(pc)
        return True, pc

    return False, pc


MACHINE_CODE: list[str] = []
line = None
counter = 0
while line != "0101000000000000":
    MACHINE_CODE.append(line := input())
    counter += 1
    if counter > 256:
        print("Error//Memory-Overflow: 256 Bytes Memory Limit Exceeded")
        quit()


MEMORY: list[str] = MACHINE_CODE.copy()
while len(MEMORY) != 256:
    MEMORY.append("0" * 16)


REGISTER_FILE: list[str] = ["0" * 16] * 8
HALTED: bool = False
PC: int = 0
PC_REGISTER: str = program_counter(PC)

REGISTERS: dict[str, str] = {
    "000": "R0", "001": "R1", "010": "R2", "011": "R3",
    "100": "R4", "101": "R5", "110": "R6", "111": "FLAGS"
}

CYCLE = 0
CYCLES: list[int] = []
MEMORY_ACCESS: list[int] = []

while not HALTED:
    INSTRUCTION: str = get_instruction(PC)
    HALTED, new_PC = execution_engine(INSTRUCTION, PC)
    current_state()
    PC = new_PC
    CYCLE += 1


for mem in MEMORY:
    print(mem)


axes = plt.axes()
y_range = range(min(MEMORY_ACCESS), max(MEMORY_ACCESS)+1)

axes.axhline(y=0, color="black", linewidth=2, zorder=2)
axes.axvline(x=0, color="black", linewidth=2, zorder=3)

axes.scatter(CYCLES, MEMORY_ACCESS, linewidths=1.5, zorder=4)
axes.set_xlabel("Cycle Number")
axes.set_ylabel("Memory Addresses Accessed")

axes.set_xticks(CYCLES)
axes.set_yticks(y_range)
axes.set_yticklabels([bin(i)[2:].zfill(8) for i in y_range])
axes.grid(True, zorder=1)

if not os.path.exists(os.path.join(os.getcwd(), "Graphs")):
    os.mkdir(os.path.join(os.getcwd(), "Graphs"))

TEST_CASE: int = 1
while os.path.exists(f"./Graphs/Test-Case-{str(TEST_CASE).zfill(2)}.jpg"):
    TEST_CASE += 1
plt.savefig(f"./Graphs/Test-Case-{str(TEST_CASE).zfill(2)}.jpg")