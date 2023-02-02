import tools
import msvcrt

# 类型
# 寄存器 跳跃字符 引用字符 一元运算符 二元运算符 命令 语句块
REG = 0; JMP = 1; REF = 2; UNOP = 3; BINOP = 4; CMD = 5; STMT = 6

# 语法错误
class HFSyntaxError(Exception):
    error_exp = None
    def __init__(self) -> None:
        super().__init__()
        
# 运行时错误（基类）
class RuntimeException(Exception):
    error_exp = None
    error_type = "运行时错误"
    def __init__(self) -> None:
        super().__init__()
        
# 栈
class Stack():
    def __init__(self, error_func) -> None:
        self.__stack = []
        self.__error_func = error_func
    
    def to_list(self) -> list:
        return self.__stack
    
    def push(self, data) -> None:
        self.__stack.append(data)
    
    def pop(self):
        try:
            data = self.__stack[-1]
            self.__stack.pop(len(self.__stack) - 1)
        except IndexError:
            self.__error_func("栈指针异常")
        return data
        
# 解释器
class Interpreter:
    def __init__(self, lines: list) -> None:
        # 忽略注释和空白
        self.codes = ""
        for l in lines:
            if l[0] == "#":
                continue
            self.codes += l

        self.codes += "\0"
        self.position = -1
        self.jump_countinue = -1 # 跳跃后执行了几步
        self.jump_stack = Stack(self.runtime_error) # 跳跃栈
        self.while_stack = Stack(self.runtime_error) # 循环栈
        self.while_reg_stack = Stack(self.runtime_error) # 循环使用的寄存器栈
        
        # 寄存器
        self.registers = {
            "q": 0, "w": 0, "e": 0, "r": 0, "t": 0, "y": 0, "u": 0, "i": 0, 
            "a": 0, "s": 0, "d": 0, "f": 0, "?": 0
        }
        # 跳跃字符位置
        self.jump_positions = {
            "z": -1, "x": -1, "c": -1, "b": -1, "n": -1, "m": -1
        }
        # 引用字符函数
        self.ref_functions = {
            "o": None, "p": None, "h": None, "j": None, "k": None, "l": None, 
        }
        # 栈
        self.stack = Stack(self.runtime_error)
        # 选中的寄存器
        self.selected_register = ""
        # 选中的跳跃字符
        self.selected_jump = ""
        # 选中的引用字符
        self.selected_ref = ""
    
    # 下一个
    def next(self) -> str:
        # 最后一个
        if self.codes[self.position + 1] == "\0":
            raise EOFError()
        return self.codes[self.position + 1].lower()
    
    # 判断下一个
    # 如果指定了type，则遇到不对的就报错
    # 没有指定type，返回下一个的type
    def check_next(self, type = None) -> int:
        char = self.next()
        current_type = None
        if char in "qwertyuiasdf?":
            current_type = REG 
        elif char in "zxcbnm":
            current_type = JMP
        elif char in "ophjkl":
            current_type = REF
        elif char in "^v][',.@!$:`/*":
            current_type = UNOP
        elif char in "+-~<>=&|":
            current_type = BINOP
        elif char in "\\0":
            current_type = CMD
        elif char in "{}()":
            current_type = STMT
        if type == None:
            return current_type
        if current_type != type:
            self.syntax_error()
    
    def eat(self) -> str:
        # 最后一个
        if self.codes[self.position + 1] == "\0":
            raise EOFError()
        self.position += 1
        return self.codes[self.position].lower()
        
    # 报错（语法）
    def syntax_error(self) -> None:
        if self.position == -1:
            self.position += 1
        error = HFSyntaxError()
        error.error_exp = self.codes[
            tools.find_prev_char(self.codes, self.position, "\n") + 1: 
            tools.find_next_char(self.codes, self.position, "\n")
        ]
        raise error
    
    # 报错（运行时）
    def runtime_error(self, type: str) -> None:
        if self.position == -1:
            self.position += 1
        error = RuntimeException()
        error.error_exp = self.codes[
            tools.find_prev_char(self.codes, self.position, "\n") + 1: 
            tools.find_next_char(self.codes, self.position, "\n")
        ]
        error.error_type = type
        raise error
    
    # 检查是否选中
    def check_selected(self, type: int) -> None:
        if type == REG:
            if self.selected_register == "":
                self.runtime_error("未选中对象")
        elif type == JMP:
            if self.selected_jump == "":
                self.runtime_error("未选中对象")
        elif type == REF:
            if self.selected_ref == "":
                self.runtime_error("未选中对象")
            
    # 开始解释
    def interpret(self) -> None:
        while True:
            char = self.next()
            type = self.check_next()
            if self.jump_countinue >= 0:
                self.jump_countinue += 1
            if self.jump_countinue > 1:
                self.jump_countinue = -1
            
            # 跳过空白
            if char in " \n\t\0":
                self.eat()
                continue
            
            # 选中寄存器
            if type == REG:
                self.eat()
                self.selected_register = char
                continue
            # 选中跳跃字符
            if type == JMP:
                self.eat()
                self.selected_jump = char
                continue
            # 选中引用字符
            if type == REF:
                self.eat()
                self.selected_ref = char
                continue
            
            # 一元运算
            if type == UNOP:
                # 加1
                if char == "^":
                    self.check_selected(REG)
                    self.eat()
                    self.registers[self.selected_register] += 1
                    continue
                # 减1
                if char == "v":
                    self.check_selected(REG)
                    self.eat()
                    self.registers[self.selected_register] -= 1
                    continue
                # 归零
                if char == "*":
                    self.check_selected(REG)
                    self.eat()
                    self.registers[self.selected_register] = 0
                    continue
                # 输出
                if char == ".":
                    self.check_selected(REG)
                    self.eat()
                    print(chr(self.registers[self.selected_register]), end = "")
                    continue
                # 输出数字
                if char == ":":
                    self.check_selected(REG)
                    self.eat()
                    print(self.registers[self.selected_register], end = "")
                    continue
                # 输入
                if char == "@":
                    self.check_selected(REG)
                    self.eat()
                    data = msvcrt.getwch()
                    print(data, end = "")
                    self.registers[self.selected_register] = ord(data)
                    continue
                # 入栈
                if char == "]":
                    self.check_selected(REG)
                    self.eat()
                    self.stack.push(self.registers[self.selected_register])
                    continue
                # 出栈
                if char == "[":
                    self.check_selected(REG)
                    self.eat()
                    data = self.stack.pop()
                    self.registers[self.selected_register] = data
                    continue
                # 取反
                if char == "!":
                    self.check_selected(REG)
                    self.eat()
                    if self.registers[self.selected_register] == 0:
                        self.registers["?"] = 1
                    else:
                        self.registers["?"] = 0
                    continue
                # 记录此处语句块
                if char == "'":
                    self.check_selected(JMP)
                    self.eat()
                    self.jump_positions[self.selected_jump] = self.position
                    continue
                # 跳到语句块
                if char == ",":
                    self.check_selected(JMP)
                    if self.jump_positions[self.selected_jump] == -1:
                        self.runtime_error("空的语句块指针")
                    self.eat()
                    self.jump_stack.push(self.position)
                    self.jump_countinue = 0
                    self.position = self.jump_positions[self.selected_jump]
                    continue
                # 记录此处内存地址
                if char == "`":
                    self.check_selected(REG)
                    self.eat()
                    self.registers[self.selected_register] = self.position
                    continue
                # 跳到内存
                if char == "/":
                    self.check_selected(REG)
                    if self.registers[self.selected_register] >= len(self.codes):
                        self.runtime_error("空的内存地址指针")
                    self.eat()
                    self.position = self.registers[self.selected_register]
                    continue
                # 跳到引用
                if char == "$":
                    self.check_selected(REF)
                    if self.ref_functions[self.selected_ref] == None:
                        self.runtime_error("空的引用")
                    self.eat()
                    stack_list = self.stack.to_list()
                    self.ref_functions[self.selected_ref](self.registers, stack_list)
                    self.stack.__stack = stack_list
                    continue
                    
            # 二元运算
            if type == BINOP:
                # 加寄存器
                if char == "+":
                    self.check_selected(REG)
                    self.eat()
                    self.check_next(REG)
                    source = self.eat()
                    self.registers[self.selected_register] += self.registers[source]
                    self.selected_register = source
                    continue
                # 减寄存器
                if char == "-":
                    self.check_selected(REG)
                    self.eat()
                    self.check_next(REG)
                    source = self.eat()
                    self.registers[self.selected_register] -= self.registers[source]
                    self.selected_register = source
                    continue
                # 传送数据
                if char == "~":
                    self.check_selected(REG)
                    self.eat()
                    self.check_next(REG)
                    source = self.eat()
                    self.registers[self.selected_register] = self.registers[source]
                    self.selected_register = source
                    continue
                # 大于
                if char == ">":
                    self.check_selected(REG)
                    self.eat()
                    self.check_next(REG)
                    source = self.eat()
                    data = self.registers[self.selected_register] > self.registers[source]
                    if data:
                        data = 1
                    else:
                        data = 0
                    self.selected_register = source
                    self.registers["?"] = data
                    continue
                # 小于
                if char == "<":
                    self.check_selected(REG)
                    self.eat()
                    self.check_next(REG)
                    source = self.eat()
                    data = self.registers[self.selected_register] < self.registers[source]
                    if data:
                        data = 1
                    else:
                        data = 0
                    self.selected_register = source
                    self.registers["?"] = data
                    continue
                # 等于
                if char == "=":
                    self.check_selected(REG)
                    self.eat()
                    self.check_next(REG)
                    source = self.eat()
                    data = self.registers[self.selected_register] == self.registers[source]
                    if data:
                        data = 1
                    else:
                        data = 0
                    self.selected_register = source
                    self.registers["?"] = data
                    continue
                # 与
                if char == "&":
                    self.check_selected(REG)
                    self.eat()
                    self.check_next(REG)
                    source = self.eat()
                    if self.registers[self.selected_register] != 0 and self.registers[source] != 0:
                        data = 1
                    else:
                        data = 0
                    self.selected_register = source
                    self.registers["?"] = data
                    continue
                # 或
                if char == "|":
                    self.check_selected(REG)
                    self.eat()
                    self.check_next(REG)
                    source = self.eat()
                    if self.registers[self.selected_register] != 0 or self.registers[source] != 0:
                        data = 1
                    else:
                        data = 0
                    self.selected_register = source
                    self.registers["?"] = data
                    continue
            
            # 语句块
            if type == STMT:
                # 语句
                if char == "{":
                    if self.jump_countinue == 1:
                        self.eat()
                    else:
                        self.position = tools.find_next_char(
                            self.codes, self.position, "}"
                        )
                    continue
                elif char == "}":
                    self.position = self.jump_stack.pop()
                    continue
                # 循环
                if char == "(":
                    self.check_selected(REG)
                    self.eat()
                    # 如果不符合条件，直接跳到循环结束
                    if self.registers[self.selected_register] == 0:
                        # 寻找循环结束部分
                        token = 1
                        while token != 0:
                            char = self.eat()
                            if char == "(":
                                token += 1
                            elif char == ")":
                                token -= 1
                        continue
                    
                    self.while_reg_stack.push(self.selected_register)
                    self.while_stack.push(self.position)
                    continue
                elif char == ")":
                    reg = self.while_reg_stack.to_list()[-1]
                    data = self.registers[reg]
                    if data != 0:
                        self.position = self.while_stack.to_list()[-1]
                        continue
                    else:
                        self.eat()
                        self.while_stack.pop()
                        self.while_reg_stack.pop()
                        continue
            
            # 命令
            if type == CMD:
                if char == "\\":
                    self.eat()
                    print()
                    continue
                if char == "0":
                    self.eat()
                    print(tools.diagram(self.registers, self.stack.to_list()))
                    continue
            
            # 没有任何一个匹配
            self.syntax_error()
            
            
            
            
        