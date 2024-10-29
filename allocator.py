# This file contains the allocator for the registers of the ILOC block.
from FrontEnd import iloc_operation, linked_list
import sys

# Maps to support allocation
VR_TO_PR = {}
PR_TO_VR = {}
VR_TO_SPILL = {}
PR_NU = {}
# NEXT_SPILL_LOCATION = 32768
NEXT_SPILL_LOCATION = 65536

def allocate(ir: linked_list.DoublyLinkedList, k: int, maxlive: int):
    if maxlive > k:
        # reserve last register for spillage
        end = k - 1
    else:
        end = k

    # for each OP in the block, top to bottom
    current_node = ir.head
    index = 0
    while current_node != None:
        use_operands = current_node.data.get_uses()
        for use_operand in use_operands:
            if VR_TO_PR.get(use_operand.get_vr()) is None:
                # get a PR, say x
                pr, spilled = get_pr(end)
                # check if the register is spilled
                if spilled:
                    # Spill a register
                    spill_insert(ir, current_node, end, pr, PR_TO_VR[pr])
                if VR_TO_SPILL.get(use_operand.get_vr()) is not None:
                    # Restore the register
                    restore_insert(end, ir, current_node, pr, use_operand.get_vr())
                    VR_TO_SPILL[use_operand.get_vr()] = None

                #load O.VR into x
                PR_TO_VR[pr] = use_operand.get_vr()
                VR_TO_PR[use_operand.get_vr()] = pr
                PR_NU[pr] = use_operand.get_nu()
                # set O.PR to x
                use_operand.set_pr(pr)
            else:
                # set O.PR to O.VR's PR
                use_operand.set_pr(VR_TO_PR[use_operand.get_vr()])
        
        for use_operand in use_operands:
            #if O is last use of O.VR, free its PR
            if use_operand.get_nu() == sys.maxsize:
                PR_TO_VR[use_operand.get_pr()] = None
                VR_TO_PR[use_operand.get_vr()] = None
                PR_NU[use_operand.get_pr()] = sys.maxsize
            else:
                PR_NU[use_operand.get_pr()] = use_operand.get_nu()

        for def_operand in current_node.data.get_defs():
            # get a PR, say z
            pr, spilled = get_pr(end)
            if spilled:
                # Spill the register
                spill_insert(ir, current_node, end, pr, PR_TO_VR[pr])
            # set O.PR to z
            PR_TO_VR[pr] = def_operand.get_vr()
            VR_TO_PR[def_operand.get_vr()] = pr
            PR_NU[pr] = def_operand.get_nu()
            def_operand.set_pr(pr)

        print(f"-------------------- AFTER ITERATION {index} --------------------")
        print(f'PR_TO_VR: {PR_TO_VR}')
        print(f'VR_TO_PR: {VR_TO_PR}')
        print(f'PR_NU: {PR_NU}')
        print(f'VR_TO_SPILL: {VR_TO_SPILL}')
        check_maps(index)

        current_node = current_node.next
        index += 1

    return ir

def get_pr(end):
    for i in range(0, end):
        if PR_TO_VR.get(i) is None:
            return i, False
        
    # no open registers
    pr_with_max_nu = 0
    for i in range(0, end):
        if PR_TO_VR.get(i) is not None:
            if PR_NU[i] > PR_NU[pr_with_max_nu]:
                pr_with_max_nu = i
        else:
            continue
    return pr_with_max_nu, True
        
# def allocate(ir: linked_list.DoublyLinkedList, k: int, maxlive: int):
#     '''
#     ir is the intermediate representation of the ILOC block
#     k is the number of registers available
#     maxlive is the maximum number of live registers
#     '''
#     if maxlive > k:
#         end = k - 1
#     else:
#         end = k

#     for i in range(0, end):
#         PR_NU[i] = sys.maxsize

#     # for each OP in the block, top to bottom
#     current_node = ir.head
#     index = 0
#     while current_node != None:
#         # print(f'current index: {index}')
#         # for each use O in OP
#         use_operands = current_node.data.get_uses()
#         for use_operand in use_operands:
#             # if (O.VR has no PR) then
#             #print(use_operand.get_vr())
#             if VR_TO_PR.get(use_operand.get_vr()) is None:
#                 pr, spilled = get_pr(end)
#                 if VR_TO_SPILL.get(use_operand.get_vr()) is not None:
#                     #print("RESTORED")
#                     # Restore the register
#                     restore_insert(end, ir, current_node, pr, use_operand.get_vr())
#                     VR_TO_SPILL[use_operand.get_vr()] = None
#                 # get a PR, say x
#                 if spilled:
#                     # Spill the register
#                     spill_insert(ir, current_node, end, pr, PR_TO_VR[pr])
#                 # load O.VR into x
#                 PR_TO_VR[pr] = use_operand.get_vr()
#                 VR_TO_PR[use_operand.get_vr()] = pr
#                 PR_NU[pr] = use_operand.get_nu()
#                 # set O.PR to x
#                 use_operand.set_pr(pr)
#             else:
#                 # set O.PR to O.VR's PR
#                 use_operand.set_pr(VR_TO_PR[use_operand.get_vr()])
#         # for each use O in OP
#         for use_operand in use_operands:
#             # if O is last use of O.VR, free its PR
#             if use_operand.get_nu() == sys.maxsize:
#                 pr_to_free = VR_TO_PR[use_operand.get_vr()]
#                 PR_TO_VR[pr_to_free] = None
#                 VR_TO_PR[use_operand.get_vr()] = None
#                 PR_NU[pr_to_free] = sys.maxsize
#             else:
#                 PR_NU[use_operand.get_pr()] = use_operand.get_nu()
#         # for each def O in OP
#         def_operands = current_node.data.get_defs()
#         for def_operand in def_operands:
#             pr, spilled = get_pr(end)
#             # print(PR_TO_VR)
#             # print(pr)
#             if VR_TO_SPILL.get(def_operand.get_vr()) is not None:
#                 # Restore the register
#                 restore_insert(end, ir, current_node, pr, def_operand.get_vr())
#                 VR_TO_SPILL[def_operand.get_vr()] = None
#             # get a PR, say z
#             if spilled:
#                 # Spill the register
#                 spill_insert(ir, current_node, end, pr, PR_TO_VR[pr])
#             PR_TO_VR[pr] = def_operand.get_vr()
#             VR_TO_PR[def_operand.get_vr()] = pr
#             #print(f'nu: {def_operand.get_nu()}')
#             PR_NU[pr] = def_operand.get_nu()
#             # set O.PR to z
#             def_operand.set_pr(pr)

#         current_node = current_node.next
#         index += 1
#         # print(f'PR_TO_VR: {PR_TO_VR}')
#         # print(f'VR_TO_PR: {VR_TO_PR}')
#         # print(f'PR_NU: {PR_NU}')
#         # print(f'VR_TO_SPILL: {VR_TO_SPILL}')


#     return ir

# def get_pr(end: int):
#     '''
#     Get a physical register
#     '''
#     for i in range(0, end):
#         if PR_TO_VR.get(i) is None:
#             return i, False
        
#     # Find the register with the furthest nu
#     pr_with_max_nu = 0
#     for i in range(0, end):
#         if PR_NU[i] > PR_NU[pr_with_max_nu]:
#             pr_with_max_nu = i
#     spilled = True

#     return pr_with_max_nu, spilled

def spill_insert(ir: linked_list.DoublyLinkedList, operation: linked_list.ILOCNode, reserved_register: int, allocated_pr: int, vr_to_spill: int):
    '''
    Insert the store and loadI operations for spilling
    '''
    global NEXT_SPILL_LOCATION
    VR_TO_SPILL[vr_to_spill] = NEXT_SPILL_LOCATION
    # Create a loadI operation
    spill_loadI = iloc_operation.ILOCOperation(operation.get_data().get_line_number(), "loadI", reg1 = None, reg2=None, reg3=None)
    spill_loadI.operand1.set_vr(NEXT_SPILL_LOCATION)
    spill_loadI.operand1.set_pr(NEXT_SPILL_LOCATION)
    spill_loadI.operand3.set_pr(reserved_register)
    
    # Insert the loadI operation before the current operation
    ir.insert_before(spill_loadI, operation)

    # Create a store operation
    spill_store = iloc_operation.ILOCOperation(operation.get_data().get_line_number(), "store", reg1 = None, reg2=None, reg3=None)
    spill_store.operand1.set_pr(allocated_pr)
    spill_store.operand3.set_pr(reserved_register)

    # Insert the store operation before the current operation
    ir.insert_before(spill_store, operation)

    VR_TO_PR[vr_to_spill] = None
    # Update the next spill location
    NEXT_SPILL_LOCATION += 4

def restore_insert(reserved_register, ir: linked_list.DoublyLinkedList, operation: linked_list.ILOCNode, allocated_pr: int, vr_to_restore: int):
    '''
    Insert the load and loadI operations for restoring
    '''

    # Create a loadI operation
    restore_loadI = iloc_operation.ILOCOperation(operation.get_data().get_line_number(), "loadI", reg1 = None, reg2=None, reg3=None)
    spilled_location = VR_TO_SPILL[vr_to_restore]
    restore_loadI.operand1.set_vr(spilled_location)
    restore_loadI.operand1.set_pr(spilled_location)
    restore_loadI.operand3.set_pr(allocated_pr)

    # Insert the loadI operation before the current operation
    ir.insert_before(restore_loadI, operation)

    # Create a load operation
    restore_load = iloc_operation.ILOCOperation(operation.get_data().get_line_number(), "load", reg1 = None, reg2=None, reg3=None)
    restore_load.operand1.set_pr(allocated_pr)
    restore_load.operand3.set_pr(allocated_pr)

    # Insert the load operation before the current operation
    ir.insert_before(restore_load, operation)


def check_maps(x):
    #For each PR p, VR-to-PR[ PR-to-VR[ p ] ] = p
    for i in range(0, len(PR_TO_VR)):
        if PR_TO_VR.get(i) is not None:
            if VR_TO_PR.get(PR_TO_VR[i]) != i:
                print(f"ERROR: VR_TO_PR[PR_TO_VR[{i}]] != {i}")
                return False
    #For each VR v, if VR-to-PR[ v ] is defined, PR-to-VR[ VR-to-PR[ v ] ] = v
    for i in range(0, len(VR_TO_PR)):
        if VR_TO_PR.get(i) is not None:
            if PR_TO_VR.get(VR_TO_PR[i]) != i:
                print(f"ERROR: PR_TO_VR[VR_TO_PR[{i}]] != {i}")
                return False
    #At operation x, for each PR p, NextUse[ p ] > x
    for i in range(0, len(PR_NU)):
        if PR_NU.get(i) is not None:
            if PR_NU[i] <= x:
                print(f"ERROR: NextUse[{i}] <= {x}")
                return False
    return True
    