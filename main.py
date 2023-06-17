from src.reader import BytecodeReader
from src.enums import ConstantTypes

from colorama import Fore, just_fix_windows_console

just_fix_windows_console()

# Bad code incoming

constantInstructions = [
    "LOADK",
    "GETGLOBAL"
]

def loadBytecode(filePath):
    with open(filePath, "rb") as file:
        return file.read()

def tableFormat(POS = "", OPCODE = "", A = "", B = "", C = "", CONSTANT = "", lengthDifference = 0):
    return ("|{!s:^5}|{:20}|{!s:^5}|{!s:^5}|{!s:^5}|{!s:50}" + (" "*lengthDifference) + "|").format(POS, f" {OPCODE}", A, B, C, f" {CONSTANT}")

def clearLine():
    return ("{:-^97}").format("")

def formatChunk(chunk):
    chunkName = chunk.name if chunk.name != "" else "[UNNAMED]"
    print("")
    print(f"CHUNK: {chunkName}\n")
    print(clearLine())
    print(tableFormat("POS", "OPCODE", "A", "B", "C", "CONSTANT"))
    print(clearLine())
    print(tableFormat())

    instructions = chunk.instructions
    stack = chunk.constants

    for instruction in instructions:
        constant = ""
        lengthDifference = 0
        if (instruction.name in constantInstructions):
            constantObject = stack[instruction.B]

            constString = str(constantObject.object)
            
            constant = f"{Fore.LIGHTBLUE_EX}\"{constString}\"{Fore.RESET}" if stack[instruction.B].type == ConstantTypes.STRING else f"{Fore.LIGHTMAGENTA_EX}{constString}{Fore.RESET}"

            lengthDifference = len(constant) - len(constString)
            lengthDifference = (lengthDifference - 1) if constantObject.type == ConstantTypes.STRING else lengthDifference


        print(tableFormat(
            instruction.POS, 
            instruction.name, 
            instruction.A, 
            instruction.B, 
            instruction.C or 0, 
            constant,
            lengthDifference
        ))
        print(tableFormat())

    print(clearLine())

    for prototype in chunk.prototypes:
        formatChunk(prototype)


rawBytecode = loadBytecode("./luac.out")

parsedBytecode = BytecodeReader(rawBytecode)

print(f"Signature: {hex(parsedBytecode.signature)}")
print(f"Version: {hex(parsedBytecode.version)}")

# Output
formatChunk(parsedBytecode.topChunk)

input()