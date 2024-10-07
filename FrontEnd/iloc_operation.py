# Description: This file contains the ILOCOperation class which is used to represent an ILOC operation.
class ILOCOperation:
    def __init__(self, line_number, opcode, reg1 = None, reg2=None, reg3=None):
        self.line_number = line_number  # Line
        self.opcode = opcode            # Opcode
        
        # Operand 1
        self.operand1 = Operand(reg1, None, None, None)
        
        # Operand 2
        self.operand2 = Operand(reg2, None, None, None)  
        
        # Operand 3
        self.operand3 = Operand(reg3, None, None, None)

    def get_defs(self):
        '''Get all the defined registers'''
        if self.opcode in ['load', 'loadI', 'add', 'sub', 'mult', 'lshift', 'rshift']:
            return [self.operand3]
        else:
            return []
        
    def get_uses(self):
        '''Get all the used registers'''
        if self.opcode in ['add', 'sub', 'mult', 'lshift', 'rshift']:
            return [self.operand1, self.operand2]
        elif self.opcode in ['load']:   
            return [self.operand1]
        elif self.opcode in ['store']:
            return [self.operand3, self.operand1]
        else:
            return []
        
    def print_vr(self):
        '''Print the iloc block using the renamed registers'''
        if self.opcode in ['output']:
            print(f"{self.opcode}\t{self.operand1.sr} ")
        elif self.opcode in ['nop']:
            print(f"{self.opcode}")
        elif self.opcode in ['loadI']:
            print(f"{self.opcode}\t{self.operand1.sr} => r{self.operand3.vr}")
        elif self.opcode in ['load', 'store']:
            print(f"{self.opcode}\tr{self.operand1.vr} => r{self.operand3.vr}")
        elif self.opcode in ['add', 'sub', 'mult', 'lshift', 'rshift']:
            print(f"{self.opcode}\tr{self.operand1.vr}, r{self.operand2.vr} => r{self.operand3.vr}")
            

    # def __repr__(self):
    #     # Format the operands using the format methods
    #     reg1 = self.format_op1(self.reg1_sr)
    #     reg2 = self.format_op2(self.reg2_sr)
    #     reg3 = self.format_op3(self.reg3_sr)

    #     # Format the operation into the desired style
    #     return (f"{self.opcode}\t"
    #             f"[ {reg1} ], "
    #             f"[ {reg2} ], "
    #             f"[ {reg3} ]")

    # def format_op1(self):
    #     '''
    #     Format the first operand
    #     '''
    #     operand1_vr = self.operand1.vr
    #     if self.operand1.vr is None:
    #         return ''
    #     if self.opcode in ['loadI', 'output']:
    #         return f"val {operand1_vr}"
    #     else:
    #         return f"vr{operand1_vr}"
        
    # def format_op2(self, register):
    #     '''
    #     Format the second operand
    #     '''
    #     operand2_vr = self.operand2.vr
    #     if operand2_vr is None:
    #         return ''
    #     else:
    #         return f"vr{operand2_vr}"
    
    # def format_op3(self, register):
    #     '''
    #     Format the third operand
    #     '''
    #     operand3_vr = self.operand3.vr
    #     if operand3_vr is None:
    #         return ''
    #     else:
    #         return f"vr{register}"
        
class Operand:
    def __init__(self, sr, vr, pr, nu):
        self.sr = sr
        self.vr = vr
        self.pr = pr
        self.nu = nu
    
    def get_sr(self):
        return self.sr
    
    def set_vr(self, vr):
        self.vr = vr

    def set_nu(self, nu):
        self.nu = nu

        

        



        