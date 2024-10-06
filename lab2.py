import sys

def print_help():
    print("""
        Valid command-line arguments:
        -h                : Show this help message.
        -s <name>         : prints tokens in token stream
        -p <name>         : invokes parser and reports on success or failure
        -r <name>         : prints human readable version of parser's IR
            """)

def main():
    argc = len(sys.argv)
    flag = sys.argv[1]

    if flag == '-h':
        print_help()
        return
    
    

if __name__ == "__main__":

    main()