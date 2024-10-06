# Description: This file contains the parser for the ILOC language.
import sys
from FrontEnd import scanner
from FrontEnd import iloc_operation, linked_list

# Global variables
opcodes = ["load", "store", "loadI", "add", "sub", "mult", "lshift", "rshift", "output", "nop"] # list of opcodes for index mapping
grammar = ["MEMOP", "LOADI", "ARITHOP", "OUTPUT", "NOP", "CONSTANT", "REGISTER", "COMMA", "INTO", "ENDFILE", "NEWLINE"] # list of grammars for index mapping
line = "" # current line being scanned

def next_token(file):
    '''
    Returns the next token from the input file.
    '''
    global line
    if line == "" or scanner.next_line == True:
        scanner.line_count += 1
        scanner.line_index = 0
        scanner.next_line = False
        line = scanner.scan_line(file)
    
    if scanner.eof == True:
        return (9, "")
    
    token = scanner.scan_word(line)
    
    return token
    
def parse(file, build_ir: bool):
    '''
    Parses the input file.
    Builds and prints the IR if build_ir is True.
    '''
    error = False
    k_operations = 0
    max_sr = 0
    if build_ir == True:
        ir = linked_list.DoublyLinkedList()
    word = next_token(file)
    while word[0] != 9:
        if word[0] == 0:
            # MEMOP
            result = finish_memop(file)
            error = result[0] or error
            if build_ir == True and error == False:
                ir.append(iloc_operation.ILOCOperation(scanner.line_count, opcodes[word[1]], result[1], None, result[2]))
                if result[1] > max_sr:
                    max_sr = result[1]
                if result[2] > max_sr:
                    max_sr = result[2]
            k_operations += 1
        elif word[0] == 1:
            # LOADI
            result = finish_loadi(file)
            error = result[0] or error
            if build_ir == True and error == False:
                ir.append(iloc_operation.ILOCOperation(scanner.line_count, opcodes[word[1]], result[1], None, result[2]))
                if result[2] > max_sr:
                    max_sr = result[2]
            k_operations += 1
        elif word[0] == 2:
            # ARITHOP
            result = finish_arithop(file)
            error = result[0] or error
            if build_ir == True and error == False:
                ir.append(iloc_operation.ILOCOperation(scanner.line_count, opcodes[word[1]], result[1], result[2], result[3]))
                if result[1] > max_sr:
                    max_sr = result[1]
                if result[2] > max_sr:
                    max_sr = result[2]
                if result[3] > max_sr:
                    max_sr = result[3]
            k_operations += 1
        elif word[0] == 3:
            # OUTPUT
            result = finish_output(file)
            error = result[0] or error
            if build_ir == True and error == False:
                ir.append(iloc_operation.ILOCOperation(scanner.line_count, opcodes[word[1]], result[1], None, None))
            k_operations += 1
        elif word[0] == 4:
            # NOP
            result = finish_nop(file)
            error = result[0] or error
            if build_ir == True and error == False:
                ir.append(iloc_operation.ILOCOperation(scanner.line_count, opcodes[word[1]], None, None, None))
            k_operations += 1
        elif word[0] == 10:
            # NEWLINE
            word = next_token(file)
            continue
        else:
            scanner.next_line = True
        word = next_token(file)
    if error == False:
        if build_ir == True:
            return ir, k_operations, max_sr
        else:
            print(f"Parse succeeded. Processed {k_operations} operations.")
    else:
        print("Parse found errors.")

def finish_memop(file):
    '''
    Finish parsing a MEMOP.
    Return a tuple:
    - the first element is a boolean indicating if there was an error
    - the second element is a tuple with the values for the ir representation if there was no error
    '''
    word = next_token(file)
    if word[0] != 6:
        print(f"ERROR {scanner.line_count}: Missing first source register in load or store", file = sys.stderr)
        return True, None
    else:
        reg1 = word[1]
        word = next_token(file)
        if word[0] != 8:
            print(f"ERROR {scanner.line_count}: Missing => in load or store", file = sys.stderr)
            return True, None
        else:
            word = next_token(file)
            if word[0] != 6:
                print(f"ERROR {scanner.line_count}: Missing second register in load or store", file = sys.stderr)
                return True, None
            else:
                reg2 = word[1]
                word = next_token(file)
                if word[0] == 10:
                    if word[1] == 0:
                        return False, reg1, reg2
                    else:
                        return True, None
                else:
                    print(f"ERROR {scanner.line_count}: Extra token after load or store", file = sys.stderr)
                    scanner.next_line = True
                    return True, None

def finish_loadi(file):
    '''
    Finish parsing a LOADI.
    '''
    word = next_token(file)
    if word[0] != 5:
        print(f"ERROR {scanner.line_count}: Missing constant in loadI", file = sys.stderr)
        return True, None
    else:
        constant = word[1]
        word = next_token(file)
        if word[0] != 8:
            print(f"ERROR {scanner.line_count}: Missing => in loadI", file = sys.stderr)
            return True, None
        else:
            word = next_token(file)
            if word[0] != 6:
                print(f"ERROR {scanner.line_count}: Missing register in loadI", file = sys.stderr)
                return True, None
            else:
                reg = word[1]
                word = next_token(file)
                if word[0] == 10:
                    if word[1] == 0:
                        return False, constant, reg
                    else:
                        return True, None
                else:
                    print(f"ERROR {scanner.line_count}: Extra token after loadI", file = sys.stderr)
                    scanner.next_line = True
                    return True, None

def finish_arithop(file):
    '''
    Finish parsing an ARITHOP.
    '''
    word = next_token(file)
    error = False
    if word[0] != 6:
        print(f"ERROR {scanner.line_count}: Missing register 1 in arithop", file = sys.stderr)
        return True, next_token
    else:
        reg1 = word[1]
        word = next_token(file)
        if word[0] != 7:
            print(f"ERROR {scanner.line_count}: Missing comma in arithop", file = sys.stderr)
            return True, None
        else:
            word = next_token(file)
            if word[0] != 6:
                print(f"ERROR {scanner.line_count}: Missing register 2 in arithop", file = sys.stderr)
                return True, None
            else:
                reg2 = word[1]
                word = next_token(file)
                if word[0] != 8:
                    print(f"ERROR {scanner.line_count}: Missing => in arithop", file = sys.stderr)
                    return True, None
                else:
                    word = next_token(file)
                    if word[0] != 6:
                        print(f"ERROR {scanner.line_count}: Missing register 3 in arithop", file = sys.stderr)
                        return True, None
                    else:
                        reg3 = word[1]
                        word = next_token(file)
                        if word[0] == 10:
                            if word[1] == 0:
                                return False, reg1, reg2, reg3
                            else:
                                return True, None
                        else:
                            print(f"ERROR {scanner.line_count}: Extra token after arithop", file = sys.stderr)
                            scanner.next_line = True
                            return True, None

def finish_output(file):
    '''
    Finish parsing an OUTPUT.
    '''
    word = next_token(file)
    if word[0] != 5:
        print(f"ERROR {scanner.line_count}: Missing constant in output", file = sys.stderr)
        return True, None
    else:
        constant = word[1]
        word = next_token(file)
        if word[0] == 10:
            if word[1] == 0:
                return False, constant
            else:
                return True, None
        else:
            print(f"ERROR {scanner.line_count}: Extra token after output", file = sys.stderr)
            scanner.next_line = True
            return True, None


def finish_nop(file):
    '''
    Finish parsing a NOP.
    '''
    word = next_token(file)
    if word[0] == 10:
        if word[1] == 0:
            return False, None
        else:
            return True, None
    else:
        print(f"ERROR {scanner.line_count}: Extra token after nop", file = sys.stderr)
        scanner.next_line = True
        return True, None

            