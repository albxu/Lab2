# Description: This file contains the scanner for the ILOC language.
import sys

# Global variables
eof = False # flag to indicate end of file
line_count = 0  # keep track of line number for printing and error messages
line_index = 0  # keep track of the index of the current line
next_line = False   # flag to indicate if scanner should go to the next line

def scan_line(file):
    global eof, line_count

    # Read the first line
    line = file.readline()

    # End of File
    if line == "":
        eof = True
        return (9, "")
    
    line = line + '\n'
    
    return line

def scan_word(input_string):
    global line_index, line_count, next_line

    def next_char():
        global line_index
        line_index += 1
        return input_string[line_index - 1]

    # Read the first character
    c = next_char()

    # get rid of whitespace
    while c == ' ' or c == '\t':
        c = next_char()

    # nop opcode
    if c == 'n':
        c = next_char()
        if c == 'o':
            c = next_char()
            if c == 'p':
                c = next_char()
                if c == ' ' or c == '\t':
                    return (4, 9)
                else:
                    return opcode_whitespace_error("nop")
            else:
                return not_a_word_error("no" + c)
        else:
            return not_a_word_error("n" + c)
    
    # lshift, load, and loadI opcodes
    if c == 'l':
        c = next_char()
        if c == 's':
            c = next_char()
            if c == 'h':
                c = next_char()
                if c == 'i':
                    c = next_char()
                    if c == 'f':
                        c = next_char()
                        if c == 't':
                            c = next_char()
                            if c == ' ' or c == '\t':
                                return (2, 6)
                            else:
                                return opcode_whitespace_error("lshift")
                        else:
                            return not_a_word_error("lshif" + c)
                    else:
                        return not_a_word_error("lshi" + c)
                else:
                    return not_a_word_error("lsh" + c)
            else:
                return  not_a_word_error("ls" + c)
        elif c == 'o':
            c = next_char()
            if c == 'a':
                c = next_char()
                if c == 'd':
                    c = next_char()
                    if c == ' ' or c == '\t':
                        return (0, 0)
                    if c == 'I':
                        c = next_char()
                        if c == ' ' or c == '\t':
                            return (1, 2)
                        else:
                            return opcode_whitespace_error("loadI")
                    else:
                        return not_a_word_error("load" + c)
                else:
                    return not_a_word_error("loa" + c)
            else:
                return not_a_word_error("lo" + c)
        else:
            return not_a_word_error("l" + c)
    
    elif c == 's':
        c = next_char()
        if c == 'u':
            c = next_char()
            if c == 'b':
                c = next_char()
                if c == ' ' or c == '\t':
                    return (2, 4)
                else:
                    return opcode_whitespace_error("sub")
            else:
                return not_a_word_error("su" + c)
        elif c == 't':
            c = next_char()
            if c == 'o':
                c = next_char()
                if c == 'r':
                    c = next_char()
                    if c == 'e':
                        c = next_char()
                        if c == ' ' or c == '\t':
                            return (0, 1)
                        else:
                            return opcode_whitespace_error("store")
                    else:
                        return not_a_word_error("stor" + c)
                else:
                    return not_a_word_error("sto" + c)
            else:
                return not_a_word_error("st" + c)
        else:
            return not_a_word_error("s" + c)
    
    # mult opcode
    elif c == 'm':
        c = next_char()
        if c == 'u':
            c = next_char()
            if c == 'l':
                c = next_char()
                if c == 't':
                    c = next_char()
                    if c == ' ' or c == '\t':
                        return (2, 5)
                    else:
                        return opcode_whitespace_error("mult")
                else:
                    return not_a_word_error("mul" + c)
            else:
                return not_a_word_error("mu" + c)
        else:
            return not_a_word_error("m" + c)    
        
    # add opcode
    elif c == 'a':
        c = next_char()
        if c == 'd':
            c = next_char()
            if c == 'd':
                c = next_char()
                if c == ' ' or c == '\t':
                    return (2, 3)
                else:
                    return opcode_whitespace_error("add")
            else:
                return not_a_word_error("ad" + c)
        else:
            return not_a_word_error("a" + c)
        
    # rshift opcode
    elif c == 'r':
        c = next_char()
        if c == 's':
            c = next_char()
            if c == 'h':
                c = next_char()
                if c == 'i':
                    c = next_char()
                    if c == 'f':
                        c = next_char()
                        if c == 't':
                            c == next_char()
                            if c == ' ' or c == '\t':
                                return (2, 7)
                            else:
                                return opcode_whitespace_error("rshift")
                        else:
                            return not_a_word_error("rshif" + c)
                    else:
                        return not_a_word_error("rshi" + c)
                else:
                    return not_a_word_error("rsh" + c)
            else:
                return not_a_word_error("rs" + c)
        elif c >= '0' and c <= '9':
            n = 0
            while c >= '0' and c <= '9':
                t = int(c)
                c = next_char()
                n = n * 10 + t
            line_index -= 1
            return (6, n)
    
        else:
            return not_a_word_error("r" + c)

    # output opcode
    elif c == 'o':
        c = next_char()
        if c == 'u':
            c = next_char()
            if c == 't':
                c = next_char()
                if c == 'p':
                    c = next_char()
                    if c == 'u':
                        c = next_char()
                        if c == 't':
                            c = next_char()
                            if c == ' ' or c == '\t':
                                return (3, 8)
                            else:
                                return opcode_whitespace_error("output")
                        else:
                            return not_a_word_error("outp" + c)
                    else:
                        return not_a_word_error("out" + c)
                else:
                    return not_a_word_error("ou" + c)
            else:
                return not_a_word_error("o" + c)
        else:
            return not_a_word_error("o" + c)
    
    # handle commas
    elif c == ',':
        return (7, ',')
    
    # handle into
    elif c == '=':
        c = next_char()
        if c == '>':
            return (8, "=>")
        else:
            return not_a_word_error("= " + c)

    # handle new lines
    elif c == '\n' or c == '\r\n':
        next_line = True
        return (10, 0)
    
    # handle comments
    elif c == '/':
        c = next_char()
        if c == '/':
            next_line = True
            return (10, 0)
        else:
            return not_a_word_error("/" + c)
        
    # handle numbers
    if (c < '0' or c > '9'):
        return not_a_word_error(c)
    else:
        n = 0
        while c >= '0' and c <= '9':
            t = int(c)
            c = next_char()
            n = n * 10 + t
        line_index -= 1
        return (5, n)
        
def opcode_whitespace_error(opcode: str):
    '''
    Print an error message for a missing whitespace after an opcode.
    Newline token with -1 lexeme means an error occurred.
    '''
    global line_index, next_line
    print(f'ERROR {line_count}: expected whitespace after opcode: "{opcode}"', file=sys.stderr)
    next_line = True
    line_index -= 1
    return (10, -1)

def not_a_word_error(word):
    '''
    Print an error message for an invalid word.
    '''
    global line_index, next_line
    print(f'ERROR {line_count}: {repr(word)} is not a valid word', file=sys.stderr)
    next_line = True
    line_index -= 1
    return (10, -1)



