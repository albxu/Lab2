# This file contains the allocator for the registers of the ILOC block.
from FrontEnd import iloc_operation, linked_list

# Maps to support allocation
VR_TO_PR = {}
PR_TO_VR = {}
VR_TO_SPILL = {}
PR_NU = {}
NEXT_SPILL_LOCATION = 32768

def allocate(ir: linked_list.DoublyLinkedList, k: int, maxlive: int):
    '''
    ir is the intermediate representation of the ILOC block
    k is the number of registers available
    maxlive is the maximum number of live registers
    '''
    if k > maxlive:
        spill = True
    else:
        spill = False

    # for each OP in the block, top to bottom
    current_node = ir.head
    while current_node != None:
        # for each use O in OP
        use_operands = current_node.data.get_uses()
        for use_operand in use_operands:
            # if (O.VR has no PR) then
            if VR_TO_PR.get(use_operand.get_vr()) is None:
                # get a PR, say x
                pr = get_pr(k, spill)
                # load O.VR into x
                PR_TO_VR[pr] = use_operand.get_vr()
                # set O.PR to x
                use_operand.set_pr(pr)
        
        # for each use O in OP
        for use_operand in use_operands:
            # if O is last use of O.VR, free its PR
            if use_operand.get_nu() == None:
                PR_TO_VR[use_operand.get_vr()] = None
            else:
                PR_NU[use_operand.get_pr()] = use_operand.get_nu()
        
        # for each def O in OP
        def_operands = current_node.data.get_defs()
        for def_operand in def_operands:
            # get a PR, say z
            pr = get_pr(k, spill)
            # set O.PR to z
            def_operand.set_pr(pr)
        
        current_node = current_node.next

def get_pr(k: int, spill: bool):
    '''
    Get a physical register
    '''
    if spill:
        end = k
    else:
        end = k - 1
    for i in range(0, end):
        if PR_TO_VR.get(i) is None:
            return i
        
    # Find the register with the furthest nu
    pr_with_max_nu = 0 
    for i in range(0, end):
        if PR_NU[i] > PR_NU[pr_with_max_nu]:
            pr_with_max_nu = i

    return pr_with_max_nu

def spill_insert(ir: linked_list.DoublyLinkedList, operation: linked_list.ILOCNode, reserved_register: int, register_to_spill: int):
    '''
    Insert the store and loadI operations for spilling
    '''

    # Create a loadI operation
    spill_load = iloc_operation.ILOCOperation(operation.get_data().get_line_number(), "loadI", reg1 = None, reg2=None, reg3=None)
    spill_load.operand1.set_vr(NEXT_SPILL_LOCATION)
    spill_load.operand1.set_pr(NEXT_SPILL_LOCATION)
    spill_load.operand3.set_pr(reserved_register)
    
    # Insert the load operation after the current operation
    ir.insert_before(spill_load, operation.next)

    # Create a store operation
    spill_loadI = iloc_operation.ILOCOperation(operation.get_data().get_line_number(), "store", reg1 = None, reg2=None, reg3=None)
    spill_loadI.operand1.set_pr(register_to_spill)
    spill_loadI.operand3.set_pr(reserved_register)

    # Insert the store operation before the current operation
    ir.insert_before(spill_loadI, operation)

    # Update the next spill location
    NEXT_SPILL_LOCATION += 4







    


    