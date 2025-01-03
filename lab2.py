import sys
import renamer, allocator
from FrontEnd import parser

def print_help():
    print("""
        Valid command-line arguments:
        -h                : Show this help message.
        -x <name>         : scan and parse the input block, and then rename registers printing results to stdout
        k <name>          : k is the number of registers available, name is the name of file with the input block, allocate physical registers and print results to stdout
            """)

def main():
    argc = len(sys.argv)
    flag = sys.argv[1]

    if flag == '-h':
        print_help()
        return
    
    if argc == 2:
        print('''ERROR: Not enough command line arguments found.
              Try running with '-h' for help.''')
        return
    
    if argc == 3:
        f_name = sys.argv[2]
    try:
        input_file = open(f_name,'r')
    except:
        print ("ERROR: Could not open file '"+f_name+"'. Exiting early.")
        exit(0)

    if flag == '-x':
        ir, maxlive = renamer.rename(input_file)
        ir.print_forward("vr")
        print("Maxlive: ", maxlive)
        return
    
    try:
        k = int(flag)
    except:
        print ("ERROR: Invalid number of registers '"+flag+"'. Exiting early.")
        exit(0)

    ir, maxlive = renamer.rename(input_file)
    ir = allocator.allocate(ir, k, maxlive)
    ir.print_forward("pr")
    return

    
if __name__ == "__main__":

    main()