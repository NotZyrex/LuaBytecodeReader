class LuaInstruction:
    def __init__(self):
        self.opcode = None
        self.A = None
        self.B = None
        self.C = None
        self.pos = 0
        self.name = None

class LuaChunk:
    def __init__(self):
        self.name = ""
        self.lineDefined = 0
        self.lastLineDefined = 0
        self.numberOfUpvalues = 0
        self.numberOfParameters = 0
        self.isVarargFlag = 1
        self.stackSize = 1

        self.instructions = []
        self.constants = []
        self.prototypes = []
        self.sourceLinePositions = []
        self.locals = []
        self.upvalues = []

        self.POS = 0
        self.topLevel = False

class LuaConstant:
    def __init__(self):
        self.object = None
        self.type = None

        self.POS = 0

class OP:
    def __init__(self, argType, name):
        self.name = name
        self.argType = argType