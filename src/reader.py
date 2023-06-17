from src.classes import LuaInstruction, LuaChunk, LuaConstant, OP
from src.enums import ConstantTypes

import struct

def readBits(integer, start, size):
    mask = (1 << size) - 1 << start

    bits = (integer & mask) >> start
    
    return bits

opMap = [
    OP("ABC", "MOVE"), 
    OP("ABx", "LOADK"), 
    OP("ABC", "LOADBOOL"),
    OP("ABC", "LOADNIL"), 
    OP("ABC", "GETUPVAL"), 
    OP("ABx", "GETGLOBAL"),
    OP("ABC", "GETTABLE"), 
    OP("ABx", "SETGLOBAL"), 
    OP("ABC", "SETUPVAL"),
    OP("ABC", "SETTABLE"), 
    OP("ABC", "NEWTABLE"), 
    OP("ABC", "SELF"),
    OP("ABC", "ADD"), 
    OP("ABC", "SUB"), 
    OP("ABC", "MUL"),
    OP("ABC", "DIV"), 
    OP("ABC", "MOD"), 
    OP("ABC", "POW"),
    OP("ABC", "UNM"), 
    OP("ABC", "NOT"), 
    OP("ABC", "LEN"),
    OP("ABC", "CONCAT"), 
    OP("AsBx", "JMP"), 
    OP("ABC", "EQ"),
    OP("ABC", "LT"), 
    OP("ABC", "LE"), 
    OP("ABC", "TEST"),
    OP("ABC", "TESTSET"), 
    OP("ABC", "CALL"), 
    OP("ABC", "TAILCALL"),
    OP("ABC", "RETURN"), 
    OP("AsBx", "FORLOOP"), 
    OP("AsBx", "FORPREP"),
    OP("ABC", "TFORLOOP"), 
    OP("ABC", "SETLIST"), 
    OP("ABC", "CLOSE"),
    OP("ABx", "CLOSURE"), 
    OP("ABC", "VARARG")
]

class BytecodeReader:
    def __init__(self, bytecode):
        self.bytecode = bytearray(bytecode)
        self.pos = 0

        # Headers
        self.signature = self.readBytes(4)
        self.version = self.readBytes()
        self.formatVersion = self.readBytes()
        self.endianFlag = self.readBytes()
        
        self.intSize = self.readBytes()
        self.size_t = self.readBytes()
        self.instructionSize = self.readBytes()
        self.lua_NumberSize = self.readBytes()
        self.integralFlag = self.readBytes()

        assert self.version == 0x51, "Version doesn't match Lua 5.1"

        # Top Chunk
        topChunk = self.readChunk()
        topChunk.topLevel = True

        self.topChunk = topChunk
        self.sourceName = topChunk.name
    
    def getEndian(self):
        return "little"
        # return (self.endianFlag == 0 and "big") or "little"

    def getBytes(self, amount):
        newPos = self.pos + amount
        byteList = self.bytecode[self.pos:newPos]

        self.pos = newPos
    
        return byteList

    def readBytes(self, amount = 1):
        endian = self.getEndian()
        byte = int.from_bytes(self.getBytes(amount), byteorder=endian)

        return byte

    def readString(self):
        size = self.readBytes(self.size_t)
        string = ""

        if (size == 0): 
            return ""

        for i in range(size):
            string += chr(self.readBytes())

        return string

    def readInteger(self):
        return self.readBytes(self.intSize)

    def readDouble(self):
        luaNum = self.getBytes(self.lua_NumberSize)
        return struct.unpack("d", luaNum)[0]

    def readInstruction(self, data, POS):
        instruction = LuaInstruction()

        # lopcodes.h
        SIZE_C = 9
        SIZE_B = 9
        SIZE_Bx = SIZE_C + SIZE_B
        SIZE_A = 8

        SIZE_OP = 6

        POS_OP = 0
        POS_A = POS_OP + SIZE_OP
        POS_C = POS_A + SIZE_A
        POS_B = POS_C + SIZE_C
        POS_Bx = POS_C

        MAX_INT18 = 131071

        opcode = opMap[readBits(data, POS_OP, SIZE_OP)]

        instruction.opcode = opcode
        instruction.name = opcode.name
        instruction.POS = POS

        instruction.A = readBits(data, POS_A, SIZE_A)

        if opcode.argType == "ABC":
            instruction.B = readBits(data, POS_B, SIZE_B)
            instruction.C = readBits(data, POS_C, SIZE_C)
        elif opcode.argType == "ABx":
            instruction.B = readBits(data, POS_Bx, SIZE_Bx)
        elif opcode.argType == "AsBx":
            instruction.B = readBits(data, POS_Bx, SIZE_Bx) - MAX_INT18

        return instruction

    def readChunk(self): 
        chunk = LuaChunk()
        chunk.name = self.readString()
        chunk.lineDefined = self.readInteger()
        chunk.lastLineDefined = self.readInteger()
        chunk.numberOfUpvalues = self.readBytes()
        chunk.numberOfParameters = self.readBytes()
        chunk.isVarargFlag = self.readBytes()
        chunk.stackSize = self.readBytes()

        sizeCode = self.readInteger()

        for i in range(sizeCode):
            instructionData = self.readBytes(self.instructionSize)
            chunk.instructions.append(self.readInstruction(instructionData, i))
        
        sizeK = self.readInteger()

        for i in range(sizeK):
            constant = LuaConstant()
            constantType = self.readBytes()
            if constantType == ConstantTypes.BOOLEAN.value:
                luaBoolean = self.readBytes() == 0

                constant.type = ConstantTypes.BOOLEAN
                constant.object = luaBoolean
            elif constantType == ConstantTypes.NUMBER.value:
                constant.type = ConstantTypes.NUMBER
                constant.object = self.readDouble()
            elif constantType == ConstantTypes.STRING.value:
                constant.type = ConstantTypes.STRING
                constant.object = self.readString()
        
            chunk.constants.append(constant)
        
        sizeP = self.readInteger()
    
        for i in range(sizeP):
            chunk.prototypes.append(self.readChunk())
        
        sizeLineInfo = self.readInteger()
        sizeLocVars = self.readInteger()
        sizeUpvalues = self.readInteger()

        return chunk
