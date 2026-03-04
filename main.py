program = []

#Get instructions, and convert from hex to binary.
with open("CPUMemory.txt", "r") as f:
    for line in f:
        stringCode = line[:4]   #Only capture the instructions, no comments.
        stringCode = list(stringCode)

        binCode = ""

        #Convert instruction to binary.
        for item in stringCode:
            num = int(item, 16)
            binItem = bin(num)
            binItem = str(binItem)
            binItem = binItem[2:]
            while len(binItem) < 4:
                binItem = "0" + binItem

            binCode = binCode + binItem

        #Add instruction to the program.
        program.append(binCode)

#Add halt to end of program
program.append("0000000000000000")

#Initialize the CPU as a class.
class CPU:
    halted = False
    currentLine = 1

    def __init__(self) -> None:
        #General Purpose Registers
        self.registers = {
            0: 0,  # A
            1: 0,  # B
            2: 0,  # C
            3: 0,  # D
            4: 0,  # E
            5: 0,  # F
            6: 0,  # G
            7: 0,  # H
            8: 0,  # I
            9: 0,  # J
            10: 0, # K
            11: 0, # L
        }

        #Special Purpose Register
        self.PC = 0
        self.Flags = 0
        self.ALU = 0

        #RAM
        self.Memory = [0] * (2**16) #16 bcuz 16-bit CPU

        #General Purpose Stack Pointer
        self.SP = []
        #Program Counter Stack Pointer
        self.PCSP = []

#Establish bitwise logic
logic_ops = {
    0: lambda x, y: x & y,
    1: lambda x, y: x | y,
    2: lambda x, y: ~x,
}

#Initialize CPU
cpu = CPU()

#Copy program into CPU memory.
for index, line in enumerate(program, start=0):
    cpu.Memory[index] = line

#Function design to check for flags.
def checkFlags(cpu):
    bit0 = 0
    bit1 = 0
    bit2 = 0
    bit3 = 0

    #Overflow Flag
    if cpu.ALU > 127 or cpu.ALU < -128:
        bit3 = 1

    #Zero Flag
    if cpu.ALU == 0:    
        bit0 = 1

    #Overflow Flag
    if cpu.ALU > 255:
        bit1 = 1
        cpu.ALU = cpu.ALU - 256

    #Negative Flag
    if cpu.ALU < 0:
        bit2 = 1
        cpu.ALU += 256

    #Update the CPU flags
    cpu.Flags = int((str(bit3) + str(bit2) + str(bit1) + str(bit0)), 2)

    return cpu.ALU

#Run the CPU
while not cpu.halted:

    #Fetch instructions
    instruction = cpu.Memory[cpu.PC]

    #Decode Instructions
    opcode = int(instruction[:4], 2)
    register1 = int(instruction[4:8], 2)
    register2 = int(instruction[8:12], 2)
    address1 = int(instruction[4:12], 2)
    address2 = int(instruction[8:16], 2)
    conditionals = int(instruction[12:16], 2)

    #Execute Instructions
    match opcode:
        case 0: #Halt
            cpu.halted = True
            print("Ended on line: " + str(cpu.PC))
            break
        case 1: #Add
            cpu.ALU = cpu.registers[register1] + cpu.registers[register2]
            cpu.ALU = checkFlags(cpu)
            cpu.registers[register1] = cpu.ALU
        case 2: #Subtract
            cpu.ALU = cpu.registers[register1] + cpu.registers[register2]
            cpu.ALU = checkFlags(cpu)
            cpu.registers[register1] = cpu.ALU
        case 3: #LOGIC
            cpu.ALU = logic_ops[conditionals](cpu.registers[register1], cpu.registers[register2])
            cpu.ALU = checkFlags(cpu)
            cpu.registers[register1] = cpu.ALU
            
        #Nothing for opcode 4 yet
            
        case 5: #Move
            cpu.registers[register1] = cpu.registers[register2]
        case 6: #Store
            cpu.Memory[address2] = cpu.registers[register1]
        case 7: #Load Address
            cpu.registers[register1] = cpu.Memory[address2]
        case 8: #Load Immediate
            cpu.registers[register1] = (address2)
        case 9: #Push
            if conditionals == 0:
                cpu.SP.append(cpu.registers[register1])
            elif conditionals == 1:
                cpu.SP.append(cpu.Memory[address1])
        case 10: #Pop
            if conditionals == 0:
                cpu.registers[register1] = cpu.SP.Pop()
            elif conditionals == 1:
                cpu.Memory[address1] = cpu.SP.Pop()
        case 11: #Increment
            if conditionals == 0:
                cpu.registers[register1] += 1
            elif conditionals == 1:
                cpu.Memory[address1] += 1
        case 12: #Decrement
            if conditionals == 0:
                cpu.registers[register1] -= 1
            elif conditionals == 1:
                cpu.Memory[address1] -= 1
        case 13: #Jump
            if (str(bin(conditionals))[5:6]) == "0": #Jump to Register value
                if (str(bin(conditionals))[2:5]) == "000":
                    cpu.SP = cpu.registers[register1]
                elif (str(bin(conditionals))[2:5]) == "001" and str(bin(cpu.Flags))[5:6] == "1":
                    cpu.SP = cpu.registers[register1]
                elif (str(bin(conditionals))[2:5]) == "010" and str(bin(cpu.Flags))[5:6] != "1":
                    cpu.SP = cpu.registers[register1]
                elif (str(bin(conditionals))[2:5]) == "011" and str(bin(cpu.Flags))[4:5] == "1":
                    cpu.SP = cpu.registers[register1]
                elif (str(bin(conditionals))[2:5]) == "100" and str(bin(cpu.Flags))[4:5] != "1":
                    cpu.SP = cpu.registers[register1]
                elif (str(bin(conditionals))[2:5]) == "101" and str(bin(cpu.Flags))[3:4] == "1":
                    cpu.SP = cpu.registers[register1]
                elif (str(bin(conditionals))[2:5]) == "110" and str(bin(cpu.Flags))[3:4] != "1":
                    cpu.SP = cpu.registers[register1]
                elif (str(bin(conditionals))[2:5]) == "111" and str(bin(cpu.Flags))[2:3] == "1":
                    cpu.SP = cpu.registers[register1]

            elif (str(bin(conditionals))[5:6]) == "1": #Jump to Address value
                if (str(bin(conditionals))[2:5]) == "000":
                    cpu.SP = cpu.Memory[address1]
                elif (str(bin(conditionals))[2:5]) == "001" and str(bin(cpu.Flags))[5:6] == "1":
                    cpu.SP = cpu.Memory[address1]
                elif (str(bin(conditionals))[2:5]) == "010" and str(bin(cpu.Flags))[5:6] != "1":
                    cpu.SP = cpu.Memory[address1]
                elif (str(bin(conditionals))[2:5]) == "011" and str(bin(cpu.Flags))[4:5] == "1":
                    cpu.SP = cpu.Memory[address1]
                elif (str(bin(conditionals))[2:5]) == "100" and str(bin(cpu.Flags))[4:5] != "1":
                    cpu.SP = cpu.Memory[address1]
                elif (str(bin(conditionals))[2:5]) == "101" and str(bin(cpu.Flags))[3:4] == "1":
                    cpu.SP = cpu.Memory[address1]
                elif (str(bin(conditionals))[2:5]) == "110" and str(bin(cpu.Flags))[3:4] != "1":
                    cpu.SP = cpu.Memory[address1]
                elif (str(bin(conditionals))[2:5]) == "111" and str(bin(cpu.Flags))[2:3] == "1":
                    cpu.SP = cpu.Memory[address1]

        case 14: #Call
            cpu.PCSP.append(cpu.PC)
            if conditionals == 0:
                cpu.PC = cpu.registers[register1]
            elif conditionals == 1:
                cpu.PC = cpu.Memory[address1]
        case 15: #Return
            cpu.PC = cpu.PCSP.pop()

    #Update program counter.
    cpu.PC = cpu.PC + 1