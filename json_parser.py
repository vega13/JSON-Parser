from enum import Enum


# utils
def log(*args):
    print(*args)


def ensure(condition, message):
    # 条件成立
    if not condition:
        log('测试失败:', message)


class Stack(object):
    def __init__(self):
        super(Stack, self).__init__()
        self.list = []
        self.length = 0

    def push(self, data):
        self.list.append(data)
        self.length += 1

    def pop(self):
        data = self.list.pop(-1)
        self.length -= 1
        return data

    def __repr__(self):
        s = str(self.list)
        return s


class Type(Enum):
    auto = 0                # auto 就是 6个特殊符号
    colon = 1               # :
    comma = 2               # ,
    braceLeft = 3           # {
    braceRight = 4          # }
    bracketLeft = 5         # [
    bracketRight = 6        # ]
    number = 7              # 123
    string = 8              # "nice"
    true = 9                # 真
    false = 10              # 假
    null = 11               # None


class Token(object):
    def __init__(self, token_type, token_value):
        super(Token, self).__init__()
        d = {
            ':': Type.colon,
            ',': Type.comma,
            '{': Type.braceLeft,
            '}': Type.braceRight,
            '[': Type.bracketLeft,
            ']': Type.bracketRight,
        }
        if token_type == Type.auto:
            self.type = d[token_value]
        else:
            self.type = token_type
        self.value = token_value

    def __repr__(self):
        if self.type == Type.string:
            s = '("{}")'.format(self.value)
        else:
            s = '({})'.format(self.value)
        return s

    @staticmethod
    def eval(token):
        if type(token) == Token:
            if token.type == Type.number:
                return int(token.value)
            elif token.type == Type.true:
                return True
            elif token.type == Type.false:
                return False
            elif token.type == Type.null:
                return None
            else:
                return token.value
        else:
            return token


def string_end(code, index):
    escape_symbol = ['\\', '"']
    s = ''
    i = index

    while i < len(code):
        c = code[i]
        i += 1
        if c == '"':
            break
        elif c == '\\':
            c = code[i]
            if c in escape_symbol:
                s += c
                i += 1
            elif c == 't':
                s += '\t'
                i += 1
            elif code[i] == 'n':
                s += '\n'
                i += 1
            else:
                # 未定义转义，应报错
                pass
        else:
            s += c

    return s, i


def number_end(code, index):
    digits = '0123456789'
    n = code[index-1]

    while code[index] in digits:
        n += code[index]
        index += 1

    return n, index


def json_tokens(code):
    op_tokens = ['[', ']', '{', '}', ':', ',']
    spaces = [' ', '\n', '\r', '\t']
    digits = '0123456789'

    tokens = []
    i = 0

    while i < len(code):
        c = code[i]
        i += 1

        if c in spaces:
            continue
        elif c in op_tokens:
            t = Token(Type.auto, c)
            tokens.append(t)
        elif c == '\"':
            s, end = string_end(code, i)
            i = end
            t = Token(Type.string, s)
            tokens.append(t)
        elif c in digits:
            n, end = number_end(code, i)
            i = end
            t = Token(Type.number, n)
            tokens.append(t)
        elif c == 't':
            i += 3
            t = Token(Type.true, 'true')
            tokens.append(t)
        elif c == 'f':
            i += 4
            t = Token(Type.false, 'false')
            tokens.append(t)
        elif c == 'n':
            i += 3
            t = Token(Type.null, 'null')
            tokens.append(t)

    # log('json_tokens', tokens)
    return tokens


def filter_tokens(stack, s, return_token):
    op_tokens = [Type.colon, Type.comma]
    t = stack.pop()

    while True:
        if type(t) == Token:
            # 当遇到 [ 或 { 时结束
            if t.type == return_token:
                break
            # 遇到 : 或 , 直接过滤
            elif t.type in op_tokens:
                t = stack.pop()
                continue

        t = Token.eval(t)
        s.push(t)
        t = stack.pop()


def parsed_list(stack):
    l = []
    s = Stack()

    filter_tokens(stack, s, Type.bracketLeft)

    for i in range(s.length):
        l.append(s.pop())

    return l


def parsed_dict(stack):
    d = {}
    s = Stack()

    filter_tokens(stack, s, Type.braceLeft)

    while s.length != 0:
        k = s.pop()
        v = s.pop()
        d[k] = v

    return d


def parsed_json(tokens):
    stack = Stack()

    for i in range(len(tokens)):
        t = tokens[i]
        if t.type == Type.bracketRight:
            l = parsed_list(stack)
            stack.push(l)
        elif t.type == Type.braceRight:
            d = parsed_dict(stack)
            stack.push(d)
        else:
            stack.push(t)

    obj = stack.pop()
    # log('parsed_json', obj)
    return obj
