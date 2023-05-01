class wakeup_logic:
    def __init__(self, table_len, reg_len):
        #instr_table: tuple (opCode, dest, src1, src2) at position i is logically represented as instruction i
        self.instr_table = []
        #reg_to_instr_idx: i in entry r means logic register r is being written to by instruction at position i
        #since more than one instruction can be writing to a register at some time, each entry r must be a list
        self.reg_to_instr_idx = [[] for i in range(reg_len)]
        #wakeup_regs; if (i,j) is 1, that means instruction i is waiting on instruction j to finish
        self.wakeup_regs = [[0 for i in range(table_len)] for i in range(table_len)]
        self.clock = 0
    #instr is a tuple (opCode, dest, src1, src2)
    def insertNewInstruction(self, instr):
        assert(len(instr)==4)
        instr_idx = len(instr_table)
        dest_reg, src1_reg, src2_reg = instr
        #update instr_table
        self.instr_table.append(instr)
        #update reg_to_instr_idx
        self.reg_to_instr_idx[dest_reg].append(instr_idx)
        #update wakeup_regs
        src1Writer = reg_to_instr_idx[src1_reg]
        self.wakeup_regs[]

    def checkForFinishedInstructions(self, finished_instr_idx):
        return None
    def checkIfReady():
        return False
    def readOutReadyInstruction(self):
        return None