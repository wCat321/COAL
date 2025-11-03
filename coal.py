import argparse
import re

INSTRUCTION_SET = {
    "AND":  {"opcode": "010000", "type": "R"},
    "OR":   {"opcode": "010010", "type": "R"},
    "ADD":  {"opcode": "010100", "type": "R"},
    "SUB":  {"opcode": "011100", "type": "R"},
    "ANDI": {"opcode": "010001", "type": "I"},
    "ORI":  {"opcode": "010011", "type": "I"},
    "ADDI": {"opcode": "010101", "type": "I"},
    "SUBI": {"opcode": "011101", "type": "I"},
    "SLT":  {"opcode": "011110", "type": "R"},
    "LW":   {"opcode": "110101", "type": "I"},
    "SW":   {"opcode": "100101", "type": "I"},
    "BLT":  {"opcode": "001110", "type": "J"},
    "HALT": {"opcode": "001111", "type": "H"},
}

REGISTER_MAP = {
    "R0": "00",
    "R1": "01",
    "R2": "10",
    "R3": "11"
}

def strip_comment(line: str) -> str:
    """Remove any text after '#' (comments)."""
    return line.split('#', 1)[0].strip()

def encode_r_type(rs, rt, rd, opcode, debug=False):
    output = f"{REGISTER_MAP[rs]}{REGISTER_MAP[rt]}{REGISTER_MAP[rd]}00{opcode}"
    if debug:
        print(f"\t\t\tR-type Encoding -> 0b{output}")
    return output

def encode_i_type(rs, rt, immediate, opcode, debug=False):
    imm_bin = format(int(immediate), "04b")  # 4-bit immediate
    output = f"{REGISTER_MAP[rs]}{REGISTER_MAP[rt]}{imm_bin}{opcode}"
    if debug:
        print(f"\t\t\tI-type Encoding -> 0b{output}")
    return output

def encode_j_type(rs, rt, target, opcode, debug=False):
    target_bin = format(int(target), "04b")
    output = f"{REGISTER_MAP[rs]}{REGISTER_MAP[rt]}{target_bin}{opcode}"
    if debug:
        print(f"\t\t\tJ-type Encoding -> 0b{output}")
    return output

def encode_halt(opcode, debug=False):
    if debug:
        print(f"\tHalt Encoding -> 0b0000000000{opcode}")
    return f"0000000000{opcode}"

def find_labels(filename, debug=False):
    """
    First pass: find all labels and their instruction addresses.
    """
    labels = {}
    address = 0

    with open(filename) as f:
        for raw_line in f:
            line = strip_comment(raw_line)
            if not line:
                continue

            parts = [p.upper() for p in re.split(r'[\s,]+', line.strip()) if p]
            if not parts:
                continue

            # If the first part ends with ':', it's a label
            if parts[0].endswith(":"):
                label_name = parts[0][:-1].upper()
                labels[label_name] = address
                if debug:
                    print(f"Label found: {label_name} -> address {address}")
                # If there's code after the label, it counts as the same line
                if len(parts) == 1:
                    continue
                else:
                    # Remove the label from the line and count instruction
                    address += 1
            else:
                address += 1

    return labels

def assemble_line_with_labels(parts, labels, debug=False):
    instr = parts[0]
    info = INSTRUCTION_SET[instr]
    opcode = info["opcode"]

    if debug:
        print(f"Assembling: {' '.join(parts)} | Opcode: 0b{opcode} | Type: {info['type']}")

    if info["type"] == "R":
        rs, rt, rd = parts[2], parts[3], parts[1]
        if debug:
            print(f"\tR-type instruction with:\n\t\trs = {rs} | 0b{REGISTER_MAP[rs]}"
                f"\n\t\trt = {rt} | 0b{REGISTER_MAP[rt]}"
                f"\n\t\trd = {rd} | 0b{REGISTER_MAP[rd]}")        
        binary = encode_r_type(rs, rt, rd, opcode, debug)

    elif info["type"] == "I":
        rs, rt, imm = parts[2], parts[1], parts[3]
        if debug:
            print(f"\tI-type instruction with:\n\t\trs = {rs} | 0b{REGISTER_MAP[rs]}"
                f"\n\t\trt = {rt} | 0b{REGISTER_MAP[rt]}"
                f"\n\t\tIMM = {imm} | 0b{format(int(imm) & 0xF, '04b')}")        
        binary = encode_i_type(rs, rt, imm, opcode, debug)

    elif info["type"] == "J":
        rs, rt, target = parts[1], parts[2], parts[3]
        if not target.isdigit():
            # Resolve label to address
            target_upper = target.upper()
            if labels is None or target_upper not in labels:
                raise ValueError(f"Unknown label '{target}'")
            target_val = labels[target_upper]
            if debug:
                print(f"\tResolved label '{target_upper}' to address 0b{labels[target_upper]:04b}")
            target = target_val
        if debug:
            print(f"\tJ-type instruction with:\n\t\trs = {rs} | 0b{REGISTER_MAP[rs]}"
                  f"\n\t\trt = {rt} | 0b{REGISTER_MAP[rt]}"
                  f"\n\t\tTARGET = {target} | 0b{format(int(target) & 0xF, '04b')}")
        binary = encode_j_type(rs, rt, target, opcode, debug)
    
    elif info["type"] == "H":
        binary = encode_halt(opcode, debug)
    
    else:
        raise ValueError(f"Unknown instruction type for {instr}")

    return f"0x{int(binary, 2):04x}"


def assemble_file(filename, debug=False):
    output = []
    labels = find_labels(filename, debug)

    if debug:
        print("\n--- LABEL TABLE ---")
        for k, v in labels.items():
            print(f"{k}: 0b{v:04b}")
        print("-------------------\n")

    with open(filename) as f:
        for raw_line in f:
            line = strip_comment(raw_line)
            if not line:
                continue

            parts = [p.upper() for p in re.split(r'[\s,]+', line.strip()) if p]
            if not parts:
                continue

            # Skip label-only lines
            if parts[0].endswith(":"):
                parts = parts[1:]
                if not parts:
                    continue

            encoded = assemble_line_with_labels(parts, labels, debug)
            if encoded:
                output.append(encoded)
                if debug:
                    print(f"\n\tEncoded Machine Code: {encoded}\n")
    return ",".join(output)

def main():
    parser = argparse.ArgumentParser(description="Computer Organization Assembly Language. Turns COAL text to machine code.")
    parser.add_argument('-i', type=str, required=True, help='Input file path.')
    parser.add_argument('-o', type=str, required=False, help='Output file path. If not provided, defaults to printing to console.')
    parser.add_argument('-d', action='store_true', help='Debug mode, prints process to console.')
    args = parser.parse_args()

    if args.d:
        print(f"\nInput File: {args.i}")
        if args.o:
            print(f"Output File: {args.o}")
        print("Starting assembly process...\n")

    machine_code = assemble_file(args.i, args.d)

    instruction_count = machine_code.count("0x")
    if instruction_count > 16:
        print(f"\n\033[91mWarning: Program contains {instruction_count} instructions, "
            "which exceeds the 16-instruction limit of the target CPU.\033[0m\n")

    if args.o:
        with open(args.o, 'w') as out_file:
            out_file.write(machine_code)
    else:
        print(machine_code)
    

if __name__ == "__main__":
    main()