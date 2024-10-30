# This file contains the renamer for the registers of the ILOC block.
import sys
from FrontEnd import parser


def rename(file):
    # Parse the input file to get the IR
    result = parser.parse(file, True)
    ir = result[0]
    num_operations = result[1]
    max_sr = result[2]

    if ir is None:
        return
    
    vr_name = 0
    sr_to_vr = {}
    lu = {}
    maxlive = 0
    currentlive = 0
    live = []
    # for i ← 0 to max SR number
    # SRToVR[i] ← invalid
    # LU[i] ← ∞
    # index ← block length
    for i in range(0, max_sr + 1):
        sr_to_vr[i] = None
        lu[i] = sys.maxsize
    index = num_operations - 1
    #print(f'lu: {lu}')

    # for each operation in the block in reverse order
    current_node = ir.tail
    while current_node != None:
        # for each def in the operation
        def_operands = current_node.data.get_defs()
        for def_operand in def_operands:
            # if SRToVR[def] is invalid meaning unused def
            operand_sr = def_operand.get_sr()
            if sr_to_vr[operand_sr] is None:
                sr_to_vr[operand_sr] = vr_name
                vr_name += 1
            def_operand.set_vr(sr_to_vr[operand_sr])
            def_operand.set_nu(lu[operand_sr])
            sr_to_vr[operand_sr] = None
            lu[operand_sr] = sys.maxsize
            if def_operand.get_vr() in live:
                live.remove(def_operand.get_vr())

        use_operands = current_node.data.get_uses()
        for use_operand in use_operands:
            operand_sr = use_operand.get_sr()
            if sr_to_vr[operand_sr] is None:
                sr_to_vr[operand_sr] = vr_name
                vr_name += 1
            use_operand.set_vr(sr_to_vr[operand_sr])
            use_operand.set_nu(lu[operand_sr])
            currentlive += 1
            if use_operand.get_vr() not in live:
                live.append(use_operand.get_vr())
        if len(live) > maxlive:
            maxlive = len(live)

        for use_operand in use_operands:
            lu[use_operand.get_sr()] = index

        current_node = current_node.prev
        index -= 1

    return ir, maxlive


