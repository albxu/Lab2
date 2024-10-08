import sys
import renamer

def print_help():
    print("""
        Valid command-line arguments:
        -h                : Show this help message.
        -x <name>         : scan and parse then input block, and then rename registers printing results to stdout
        k <name>          : k is the number of registers available, name is the name of file with the input block
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
        renamer.rename(input_file)
        return
    
if __name__ == "__main__":

    main()