import sys

class CPU:

    def __init__(self):
        self.ram = [0] * 256
        self.reg = [0] * 8 
        self.sp = 7
        self.reg[self.sp] = 0xF4
        self.pc = 0
        self.ir = 0
        self.fl = 6
        self.op_table = {
                        0b10000010 : self.ldi, 
                        0b01000111 : self.prn, 
                        0b10100010 : self.mult,
                        0b00000001 : self.hlt,
                        0b01000101 : self.push,
                        0b01000110 : self.pop,
                        0b01010000 : self.call, 
                        0b00010001 : self.ret,
                        0b10100000 : self.add, 
                        0b01010110 : self.jne,
                        0b01010100 : self.jmp,
                        0b01010101 : self.jeq, 
                        0b10100111 : self.cmpp}

    def load(self):

        address = 0

        file = open('sctest.ls8',  "r")
        for line in file.readlines():
            try:
                x = line[:line.index("#")]
            except ValueError:
                x = line

            try: 
                y = int(x, 2)
                self.ram[address] = y
            except ValueError:
                continue
            address+=1

    def ldi(self, operand_a, operand_b):
        self.reg[operand_a] = operand_b

    def mult(self, operand_a, operand_b):
        self.reg[operand_a] = self.reg[operand_a] * self.reg[operand_b]

    # Push the value in the given register on the stack.
    def push(self, operand_a, operand_b):        
        self.reg[self.sp] -= 1
        self.ram[self.reg[self.sp]] = self.reg[operand_a]

    # Pop the value at the top of the stack into the given register.
    def pop(self, operand_a, operand_b):
        self.reg[operand_a] = self.ram[self.reg[self.sp]]
        self.reg[self.sp] += 1

    # Sets the PC to the register value
    def call(self, operand_a, operand_b):
        self.reg[self.sp] -= 1
        self.ram[self.reg[self.sp]] = self.pc + 2
        self.pc = self.reg[operand_a]
        return True

    def ret(self, operand_a, operand_b):
        self.pop(operand_a, 0)
        self.pc = self.reg[operand_a]
        return True

    def add(self, operand_a, operand_b):
        self.reg[operand_a] = self.reg[operand_a] + self.reg[operand_b]

    def cmpp(self, operand_a, operand_b):
        value_a = self.reg[operand_a]
        value_b = self.reg[operand_b]

        if value_a == value_b:
            self.reg[self.fl] = 1
        elif value_a > value_b:
            self.reg[self.fl] = 2
        else:
            self.reg[self.fl] = 4


    def jne(self, operand_a, operand_b):
        value = self.reg[self.fl]
        if value == 2 or value == 4:
            return self.jmp(operand_a, 0)

    def jmp(self, operand_a, operand_b):
        self.pc = self.reg[operand_a]
        return True

    def jeq(self, operand_a, operand_b):
        if self.reg[self.fl] == 1:
            return self.jmp(operand_a, 0)

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, value, address):
        self.ram[address] = value

    def prn(self, operand_a, operand_b):
        print(self.reg[operand_a])

    def hlt(self, operand_a, operand_b):
        sys.exit()

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        else:
            raise Exception("ALU operation undefined")

    def run(self):
        """Run the CPU."""
        while True:
            self.ir = self.ram[self.pc]
            operand_a = self.ram[self.pc + 1]
            operand_b = self.ram[self.pc + 2]

            willJump = self.op_table[self.ir](operand_a, operand_b)
            if not willJump:
                self.pc += (self.ir >> 6) + 1