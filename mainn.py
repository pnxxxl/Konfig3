import re
import json
import argparse
import sys

# Структура для представления токена (не нужна в Python, но для аналогии с C++)
class Token:
    NUMBER = 1
    STRING = 2
    NAME = 3
    ASSIGN = 4
    ARRAY_START = 5
    ARRAY_END = 6
    COMMENT = 7
    ERROR = 8

    def __init__(self, type, value):
        self.type = type
        self.value = value

# Лексер
def lex(input):
    tokens = []
    for line in input.splitlines():
        line = line.strip()
        if not line or line.startswith(';'):
            continue

        parts = line.split(":=")
        if len(parts) != 2:
            tokens.append(Token(Token.ERROR, line))
            continue

        name = parts[0].strip()
        value = parts[1].strip()

        tokens.append(Token(Token.NAME, name))
        tokens.append(Token(Token.ASSIGN, ":="))

        match = re.match(r'q\((.*?)\)', value)
        if match:
            tokens.append(Token(Token.STRING, match.group(1)))
        elif re.match(r'^\d+$', value):
            tokens.append(Token(Token.NUMBER, value))
        elif value.startswith('{') and value.endswith('}'):
            tokens.append(Token(Token.ARRAY_START, '{'))
            for elem in re.findall(r'\w+', value[1:-1]):
                tokens.append(Token(Token.STRING, elem))
            tokens.append(Token(Token.ARRAY_END, '}'))
        else:
            tokens.append(Token(Token.STRING, value))

    print(f"Все токены: {[t.value for t in tokens]}") #Вывод всех токенов после обработки
    return tokens


def parse(tokens):
    constants = {}
    i = 0
    while i < len(tokens):
        if tokens[i].type == Token.NAME:
            name = tokens[i].value
            if i + 1 < len(tokens) and tokens[i + 1].type == Token.ASSIGN:
                i += 2  # Пропускаем токен ASSIGN
                if tokens[i].type == Token.ARRAY_START:
                    array_values = []
                    i += 1
                    while i < len(tokens) and tokens[i].type != Token.ARRAY_END:
                        array_values.append(tokens[i].value)
                        i += 1
                    constants[name] = array_values
                    i += 1
                elif tokens[i].type in (Token.NUMBER, Token.STRING, Token.NAME):
                    constants[name] = tokens[i].value
                    i += 1
                else:
                    raise ValueError(f"Неожиданный токен после оператора присваивания для {name} на строке {get_line_number(i,tokens)}")
            else:
                raise ValueError(f"Ожидается оператор присваивания после имени {name} на строке {get_line_number(i,tokens)}")
        else:
            i += 1
    return constants

def get_line_number(token_index, tokens):
    # (приблизительная реализация, если нет информации о номерах строк)
    return token_index + 1

def interpret(constants):
    interpreted_constants = {}
    for name, value in constants.items():
        if isinstance(value, list):
            interpreted_value = [interpret_value(v, constants) for v in value]
        else:
            interpreted_value = interpret_value(value, constants)
        interpreted_constants[name] = interpreted_value
    return interpreted_constants

def interpret_value(value, constants):
    match = re.match(r'^\$(\w+)$', value)
    if match:
        referenced_name = match.group(1)
        if referenced_name in constants:
            return interpret_value(constants[referenced_name], constants) # Рекурсивный вызов для вложенных переменных
        else:
            raise ValueError(f"Константа ${referenced_name} не определена")
    return value



def main():
    parser = argparse.ArgumentParser(description='Переводчик конфигурационного языка')
    parser.add_argument('output_file', help='Путь к выходному файлу')
    args = parser.parse_args()

    try:
        input_text = sys.stdin.read() # Чтение из стандартного ввода
        tokens = lex(input_text)
        parsed_constants = parse(tokens)
        interpreted_constants = interpret(parsed_constants)

        with open(args.output_file, 'w') as f:
            json.dump(interpreted_constants, f, indent=4)
    except FileNotFoundError:
        print(f"Ошибка: Файл не найден", file=sys.stderr)
        sys.exit(1)
    except UnicodeDecodeError:
        print(f"Ошибка: Не удалось декодировать файл. Проверьте кодировку.", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Ошибка обработки: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Непредвиденная ошибка: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()