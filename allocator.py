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
    # maps vrs to loadIs for rematerialization
    rematerializable = {}
    # for each OP in the block, top to bottom
    current_node = ir.head
    index = 0
    while current_node != None:
        use_operands = current_node.data.get_uses()
        used_prs = []
        for use_operand in use_operands:
            if VR_TO_PR.get(use_operand.get_vr()) is None:
                # get a PR, say x
                pr, spilled = get_pr(end, used_prs)
                used_prs.append(pr)
                # check if the register is spilled
                if spilled:
                    # Spill a register if it can't be rematerialized
                    if rematerializable.get(pr) is None:
                        spill_insert(ir, current_node, end, pr, PR_TO_VR[pr])
                    else:
                        VR_TO_SPILL[use_operand.get_vr()] = NEXT_SPILL_LOCATION
                if VR_TO_SPILL.get(use_operand.get_vr()) is not None:
                    # Restore the register
                    restore_insert(end, ir, current_node, pr, use_operand.get_vr(), rematerializable)
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

            # print(f"-------------------- AFTER USES IN ITERATION {index} --------------------")
            # print(f'PR_TO_VR: {PR_TO_VR}')
            # print(f'VR_TO_PR: {VR_TO_PR}')
            # print(f'PR_NU: {PR_NU}')
            # print(f'VR_TO_SPILL: {VR_TO_SPILL}')
        used_prs = []
        for use_operand in use_operands:
            #if O is last use of O.VR, free its PR
            if use_operand.get_nu() == sys.maxsize:
                PR_TO_VR[use_operand.get_pr()] = None
                VR_TO_PR[use_operand.get_vr()] = None
                PR_NU[use_operand.get_pr()] = sys.maxsize
            else:
                PR_NU[use_operand.get_pr()] = use_operand.get_nu()

        for def_operand in current_node.data.get_defs():
            if current_node.data.get_opcode() == "loadI":
                rematerializable[def_operand.get_vr()] = current_node.data.get_operand1().get_pr()
            # get a PR, say z
            pr, spilled = get_pr(end, used_prs)
            if spilled:
                # Spill a register if it can't be rematerialized
                if rematerializable.get(pr) is None:
                    spill_insert(ir, current_node, end, pr, PR_TO_VR[pr])
                else:
                    VR_TO_SPILL[use_operand.get_vr()] = NEXT_SPILL_LOCATION
            # set O.PR to z
            PR_TO_VR[pr] = def_operand.get_vr()
            VR_TO_PR[def_operand.get_vr()] = pr
            PR_NU[pr] = def_operand.get_nu()
            def_operand.set_pr(pr)

        # print(f"-------------------- AFTER ITERATION {index} --------------------")
        # current_node.data.print_pr()
        # print(f'PR_TO_VR: {PR_TO_VR}')
        # print(f'VR_TO_PR: {VR_TO_PR}')
        # print(f'PR_NU: {PR_NU}')
        # print(f'VR_TO_SPILL: {VR_TO_SPILL}')
        # check_maps(index)

        current_node = current_node.next
        index += 1

    return ir

def get_pr(end, used_prs):
    for i in range(0, end):
        if PR_TO_VR.get(i) is None and i not in used_prs:
            return i, False
        
    # no open registers
    pr_with_max_nu = 0
    for i in range(0, end):
        if PR_TO_VR.get(i) is not None and i not in used_prs:
            if PR_NU[i] > PR_NU[pr_with_max_nu]:
                pr_with_max_nu = i
        else:
            continue
    return pr_with_max_nu, True

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

def restore_insert(reserved_register, ir: linked_list.DoublyLinkedList, operation: linked_list.ILOCNode, allocated_pr: int, vr_to_restore: int, rematerializable: dict):
    '''
    Insert the load and loadI operations for restoring
    '''
    if rematerializable.get(vr_to_restore) is not None:
        # Create a loadI operation
        restore_loadI = iloc_operation.ILOCOperation(operation.get_data().get_line_number(), "loadI", reg1 = None, reg2=None, reg3=None)
        restore_loadI.operand1.set_pr(rematerializable[vr_to_restore])
        restore_loadI.operand3.set_pr(allocated_pr)

        # Insert the loadI operation before the current operation
        ir.insert_before(restore_loadI, operation)
        return

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
    