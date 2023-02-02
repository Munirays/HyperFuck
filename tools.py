# 寻找上一个字符
def find_prev_char(string:str, position: int, char: str) -> int:
    current_char = ""
    if position == 0 or not char in string[:position - 1]:
        return -1
    while current_char != char:
        position -= 1
        current_char = string[position]
    return position

# 寻找下一个字符
def find_next_char(string:str, position: int, char: str) -> int:
    current_char = ""
    if not char in string[position:]:
        return -1
    while current_char != char:
        position += 1
        current_char = string[position]
    return position

# 图形化寄存器与堆栈
def diagram(registers: dict, stack: list) -> str:
    text = f""" 数据    Q={registers["q"]}   W={registers["w"]}   E={registers["e"]}   R={registers["r"]}
寄存器   T={registers["t"]}   Y={registers["y"]}   U={registers["u"]}   I={registers["i"]}
指针寄存器   A={registers["a"]}   S={registers["s"]}   D={registers["d"]}   F={registers["f"]}   结果寄存器   ?={registers["?"]}
"""
    stack_text = [
        "┌──────┐",
        "│      │",
        "│  栈  │",
        "│      │",
        "└──────┘"
    ]
    if len(stack) == 0:
        stack_text[2] += "  无内容  "
    else:
        for x in stack:
            stack_text[2] += f" {x} "
            for i in range(5):
                if i == 2:
                    stack_text[i] += "│"
                else:
                    stack_text[i] += " " * (2 + len(str(x))) + "│"
    for line in stack_text:
        text += "\n" + line
    return text
            
# 获取引用
def get_references(ref_lines: list) -> dict:
    ref_functions = {
        "o": None, "p": None, "h": None, "j": None, "k": None, "l": None, 
    }
    keys = "ophjkl"
    key_index = 0
    # 读取信息
    for l in ref_lines:
        file, func_text = l.split(" ")
        functions = func_text.split(",")
        module = __import__(file)
        for f in functions:
            ref_functions[keys[key_index]] = eval(f"module.{f}")
            key_index += 1
            if key_index == 6:
                break
    return ref_functions
