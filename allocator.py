# This file contains the allocator for the registers of the ILOC block.
from FrontEnd import iloc_operation, linked_list
import sys

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
    if maxlive > k:
        end = k - 1
    else:
        end = k

    for i in range(0, end):
        PR_NU[i] = sys.maxsize

    # for each OP in the block, top to bottom
    current_node = ir.head
    index = 0
    while current_node != None:
        #print(f'current index: {index}')
        # for each use O in OP
        use_operands = current_node.data.get_uses()
        for use_operand in use_operands:
            # if (O.VR has no PR) then
            #print(use_operand.get_vr())
            if VR_TO_PR.get(use_operand.get_vr()) is None:
                pr, spilled = get_pr(end)
                if VR_TO_SPILL.get(use_operand.get_vr()) is not None:
                    #print("RESTORED")
                    # Restore the register
                    restore_insert(end, ir, current_node, pr, use_operand.get_vr())
                    VR_TO_SPILL[use_operand.get_vr()] = None
                # get a PR, say x
                if spilled:
                    # Spill the register
                    spill_insert(ir, current_node, end, pr, PR_TO_VR[pr])
                # load O.VR into x
                PR_TO_VR[pr] = use_operand.get_vr()
                VR_TO_PR[use_operand.get_vr()] = pr
                PR_NU[pr] = use_operand.get_nu()
                # set O.PR to x
                use_operand.set_pr(pr)
            else:
                # set O.PR to O.VR's PR
                use_operand.set_pr(VR_TO_PR[use_operand.get_vr()])
        # for each use O in OP
        for use_operand in use_operands:
            # if O is last use of O.VR, free its PR
            if use_operand.get_nu() == sys.maxsize:
                pr_to_free = VR_TO_PR[use_operand.get_vr()]
                PR_TO_VR[pr_to_free] = None
                VR_TO_PR[use_operand.get_vr()] = None
            else:
                PR_NU[use_operand.get_pr()] = use_operand.get_nu()
        # for each def O in OP
        def_operands = current_node.data.get_defs()
        for def_operand in def_operands:
            pr, spilled = get_pr(end)
            if VR_TO_SPILL.get(def_operand.get_vr()) is not None:
                # Restore the register
                restore_insert(end, ir, current_node, pr, def_operand.get_vr())
                VR_TO_SPILL[def_operand.get_vr()] = None
            # get a PR, say z
            if spilled:
                # Spill the register
                spill_insert(ir, current_node, end, pr, PR_TO_VR[pr])
            PR_TO_VR[pr] = def_operand.get_vr()
            VR_TO_PR[def_operand.get_vr()] = pr
            #print(f'nu: {def_operand.get_nu()}')
            PR_NU[pr] = def_operand.get_nu()
            # set O.PR to z
            def_operand.set_pr(pr)

        current_node = current_node.next
        index += 1
        # print(f'PR_TO_VR: {PR_TO_VR}')
        # print(f'VR_TO_PR: {VR_TO_PR}')
        # print(f'PR_NU: {PR_NU}')
        # print(f'VR_TO_SPILL: {VR_TO_SPILL}')

    return ir

def get_pr(end: int):
    '''
    Get a physical register
    '''
    for i in range(0, end):
        if PR_TO_VR.get(i) is None:
            return i, False
        
    # Find the register with the furthest nu
    pr_with_max_nu = 0
    for i in range(0, end):
        if PR_NU[i] > PR_NU[pr_with_max_nu]:
            pr_with_max_nu = i
    spilled = True

    return pr_with_max_nu, spilled

def spill_insert(ir: linked_list.DoublyLinkedList, operation: linked_list.ILOCNode, reserved_register: int, pr_to_spill: int, vr_to_spill: int):
    '''
    Insert the store and loadI operations for spilling
    '''
    global NEXT_SPILL_LOCATION
    VR_TO_SPILL[vr_to_spill] = NEXT_SPILL_LOCATION
    # Create a loadI operation
    spill_load = iloc_operation.ILOCOperation(operation.get_data().get_line_number(), "loadI", reg1 = None, reg2=None, reg3=None)
    spill_load.operand1.set_vr(NEXT_SPILL_LOCATION)
    spill_load.operand1.set_pr(NEXT_SPILL_LOCATION)
    spill_load.operand3.set_pr(reserved_register)
    
    # Insert the loadI operation before the current operation
    ir.insert_before(spill_load, operation)

    # Create a store operation
    spill_loadI = iloc_operation.ILOCOperation(operation.get_data().get_line_number(), "store", reg1 = None, reg2=None, reg3=None)
    spill_loadI.operand1.set_pr(pr_to_spill)
    spill_loadI.operand3.set_pr(reserved_register)

    # Insert the store operation before the current operation
    ir.insert_before(spill_loadI, operation)

    VR_TO_PR[vr_to_spill] = None
    # Update the next spill location
    NEXT_SPILL_LOCATION += 4

def restore_insert(end, ir: linked_list.DoublyLinkedList, operation: linked_list.ILOCNode, allocated_pr: int, vr_to_restore: int):
    '''
    Insert the load and loadI operations for restoring
    '''

    # Create a loadI operation
    restore_load = iloc_operation.ILOCOperation(operation.get_data().get_line_number(), "loadI", reg1 = None, reg2=None, reg3=None)
    spilled_location = VR_TO_SPILL[vr_to_restore]
    restore_load.operand1.set_vr(spilled_location)
    restore_load.operand1.set_pr(spilled_location)
    restore_load.operand3.set_pr(end)

    # Insert the loadI operation before the current operation
    ir.insert_before(restore_load, operation)

    # Create a load operation
    restore_loadI = iloc_operation.ILOCOperation(operation.get_data().get_line_number(), "load", reg1 = None, reg2=None, reg3=None)
    restore_loadI.operand1.set_pr(end)
    restore_loadI.operand3.set_pr(allocated_pr)

    # Insert the load operation before the current operation
    ir.insert_before(restore_loadI, operation)








    