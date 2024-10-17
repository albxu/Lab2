class ILOCNode:
    '''
    A node in a doubly linked list
    '''
    def __init__(self, data=None):
        self.data = data
        self.next = None
        self.prev = None 
    
    def print_mode(self, mode: str):
        '''
        Print the node's data in the specified mode
        '''
        if mode == "vr":
            self.data.print_vr()
        elif mode == "sr":
            self.data.print_sr()
    
    def get_data(self):
        return self.data

class DoublyLinkedList:
    '''
    A doubly linked list
    '''
    def __init__(self):
        self.head = None  # Start of the linked list
        self.tail = None  # End of the linked list
        self.length = 0

    def append(self, data):
        '''
        Append a new node with data to the end of the list
        '''
        new_node = ILOCNode(data)
        
        if self.head is None:  # Empty list
            self.head = new_node
            self.tail = new_node
            self.length += 1
        else:  # Append to the end of the list
            new_node.prev = self.tail
            self.tail.next = new_node
            self.tail = new_node
            self.length += 1

    def insert_before(self, data, node):
        '''
        Insert a new node with data before the specified node
        '''
        new_node = ILOCNode(data)
        new_node.prev = node.prev
        new_node.next = node
        if node.prev is not None:
            node.prev.next = new_node
        else:
            self.head = new_node
        node.prev = new_node
        self.length += 1

    def print_forward(self, mode: str):
        '''
        Print the list from the head to the tail
        Mode is either "vr" or "sr" for printing source registers or virtual registers
        '''
        current = self.head
        while current:
            current.print_mode(mode)
            current = current.next 