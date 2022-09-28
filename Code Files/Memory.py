import math


PROMPT = "\n>>> "
UNITS = {"M": 2**20, "K": 2**10, "B": 1, "b": 1, "G": 2**30}

print("="*80, "WELCOME TO THE MEMORY MUMBO JUMBO!!", "="*80, sep="\n")

space = input(f"\nEnter the total size of memory {PROMPT}")
num, unit = space.split()
num = int(num)
if unit[0] in UNITS:
    num *= UNITS[unit[0]]
else:
    print("Invalid unit of Memory")
    quit()

num *= 8 if unit[-1] == "B" else 1
mem_size = """Please select how the memory is addressed:
    1. Bit addressable
    2. Nibble addressable
    3. Byte addressable
    4. Word addressable
"""

mode = int(input(f"\n{mem_size}Enter your choice {PROMPT}"))
if mode == 4:
    mode = int(input(f"\nEnter word size (in Bytes) {PROMPT}")) * 8

MODES = {1: 1, 2: 4, 3: 8}
num_addr = num / MODES.get(mode, mode)


while True:
    print("\n" + "="*80)
    qtype = input(f"\nEnter the type of Query (1 / 2) {PROMPT}")


    if qtype == "1":
        len_inst = int(input(f"\nEnter length of instruction {PROMPT}"))
        len_reg = int(input(f"\nEnter length of register {PROMPT}"))
        print()

        min_bits = math.ceil(math.log2(num_addr))
        len_opcode = len_inst - len_reg - min_bits
        filler = len_inst - len_opcode - 2*len_reg

        print(f"Minimum number of bits to represent memory (P): {min_bits} Bits")
        print(f"Number of bits for opcode (Q): {len_opcode} Bits")
        print(f"Number of filler bits for Instruction Type 2 (R): {filler} Bits")
        print(f"Maximum number of instructions: {2**len_opcode}")
        print(f"Maximum number of registers: {2**len_reg}")


    elif qtype == "2":
        sub_type = input(f"\nEnter the sub-type of Query (1 / 2) {PROMPT}")
        bits = int(input(f"\nEnter the size of CPU in Bits {PROMPT}"))

        if sub_type == "1":
            mode = int(input(f"\n{mem_size}Enter your choice {PROMPT}"))
            mode = MODES.get(mode, bits)
            l, r = math.ceil(math.log2(num_addr)), math.ceil(math.log2(num/mode))
            print(f"\nNumber of address pins saved or required: {'+' if l < r else '-'}{abs(l-r)}")

        elif sub_type == "2":
            pins = int(input(f"\nEnter the number of address pins in the CPU {PROMPT}"))
            mode = int(input(f"\n{mem_size}Enter your choice {PROMPT}"))

            mode = MODES.get(mode, bits)
            total_mem = 2**pins * mode / 8
            unit = "B"
            copy_mem, copy_unit = total_mem, unit

            if copy_mem > 2**30:
                copy_mem /= 2**30
                copy_unit = "GB"
            elif copy_mem > 2**20:
                copy_mem /= 2**20
                copy_unit = "MB"
            elif copy_mem > 2**10:
                total_mem /= 2**10
                copy_unit = "KB"

            if copy_unit == unit:
                print("\nTotal Memory:", total_mem, unit)
            else:
                print("\nTotal Memory:", total_mem, unit, "or", copy_mem, copy_unit)

        else:
            print("\nInvalid sub-type of Query. Please try again!")

    else:
        print("\nInvalid type of Query. Please try again!")
        continue

    to_continue = input(f"\nDo you wish to continue? (Y / N) {PROMPT}")
    if to_continue.casefold() == "n":
        break


print("\n" + "="*80, "THANKS FOR USING THE MEMORY MUMBO JUMBO!!", "="*80, sep="\n")