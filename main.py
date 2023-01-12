import sys
import numpy as np
import pandas as pd
import math
from os import path


def error(error_msg, op1='\0'):
    print("error:", error_msg, op1)
    exit(-1)


def msg(_msg):
    print("msg:", _msg)


class SymTabItem(object):
    def __init__(self):
        self.mnemonic = ''
        self.location = ''

    def __str__(self):
        return str(self.mnemonic).ljust(20) + str(self.location)


class Item(object):
    def __init__(self):
        self.address = ''
        self.objcode = ''

    def __str__(self):
        return str(self.address).ljust(20) + str(self.objcode)


msg("initializing")

MnemonicOpcode = pd.read_csv('MnemonicOpcode.csv')
Mnemonic = np.asarray(pd.DataFrame(MnemonicOpcode, columns=['Mnemonic']))
Opcode = np.asarray(pd.DataFrame(MnemonicOpcode, columns=['Opcode']))


column_lengths = [11, 10, 18, 31]
result_column_lengths = [5, 11, 10, 18]
result2_column_lengths = [5, 11, 10, 18, 10]

msg("initialize [OK]")


def mnemonic_exist(mnemonic):
    exist = np.where(Mnemonic == mnemonic)
    return len(exist[0]) != 0


def sym_exist(sym_tab, sym):
    exist = np.where(sym_tab == sym)
    return len(exist[0]) != 0


def literal_exist(literals, literal):
    exist = np.where(literals == literal)
    return len(exist[0]) != 0


def star(sym_tab):
    exist = np.where(sym_tab == '*')
    if len(exist[0]) == 0:
        return -1
    else:
        return exist[0][0]


def to_decimal(hix):
    return int(hix, 16)


def chunk_string(string, lengths):
    return (string[pos:pos+length].strip()
            for idx, length in enumerate(lengths)
            for pos in [sum(map(int, lengths[:idx]))])


def obj_code_of_string(string):
    return ''.join(hex(int(str(ord(c))))[2:].upper() for c in string)


def opcode_of_mnemonic(x):
    exist = np.where(Mnemonic == x)
    return str(Opcode[exist[0][0]][0]).zfill(2)


def add_literal(aux, x):
    for itr in aux:
        if len(itr) >= 3:
            if itr[1] == '*' and itr[2] == x:
                return itr[0]
    return -1


def add_mnemonic(aux, x):
    for itr in aux:
        if len(itr) == 4:
            if itr[1] == x:
                return itr[0]
    return -1


def indirect_addressing(aux, x, mask):
    if mask & 1 == 1:
        address = add_mnemonic(aux, x)
    else:
        address = add_literal(aux, x)

    if address != -1:
        d_address = to_decimal(str(address))
        b_address = bin(d_address)
        b_address = b_address[2:].zfill(16)
        if mask & 2 == 1:
            b_address = '1' + b_address[1:]
        else:
            b_address = '0' + b_address[1:]
        return hex(int(b_address, 2))[2:].upper()
    else:
        return -1


def pass1(pass1_input):
    pc_loc = 0
    result = []
    sym_tab_item = SymTabItem()
    sym_tab = np.array([])
    literals = np.array([])
    initial_locator = -1

    for line in pass1_input:
        if line[0] == '.' or line.strip() == '':
            continue

        columns = list(chunk_string(line, column_lengths))

        for it in range(len(columns)):
            columns[it] = columns[it].strip()

        if columns[1] == 'START':
            initial_locator = to_decimal(columns[2])
            pc_loc = initial_locator

        if columns[0] != '':
            if sym_exist(sym_tab, columns[0]):
                error("Duplicated symbol")

            sym_tab_item = SymTabItem()
            sym_tab_item.mnemonic = columns[0]
            sym_tab_item.location = hex(pc_loc)[2:].upper()
            sym_tab = np.append(sym_tab, sym_tab_item)

            immediate_line = []

            immediate_line.append(hex(pc_loc)[2:].upper())
            immediate_line.append(columns[0])
            immediate_line.append(columns[1])
            immediate_line.append(columns[2])
            result = np.append(result, immediate_line)

            if mnemonic_exist(columns[1]):
                pc_loc = pc_loc + 3
                if len(columns[2]) and columns[2][0] == '=':
                    literals = np.append(literals, columns[2])

            elif columns[1] == "WORD":
                pc_loc = pc_loc + 3
            elif columns[1] == "RESW":
                pc_loc += (3 * int(columns[2]))
            elif columns[1] == "RESB":
                pc_loc += int(columns[2])
            elif columns[1] == "BYTE":
                if columns[2][0] == 'C':
                    pc_loc += len(columns[2]) - 3
                else:
                    pc_loc += int((len(columns[2]) - 3) / 2)
            elif columns[1] == 'START':
                continue
            elif columns[1] == 'END':
                result[len(result) - 4] = ''
                for literal in literals:
                    if star(sym_tab) == -1:
                        sym_tab_item = SymTabItem()
                        sym_tab_item.mnemonic = '*'
                        sym_tab_item.location = hex(pc_loc)[2:].upper()
                        sym_tab = np.append(sym_tab, sym_tab_item)
                    else:
                        sym_tab[star(sym_tab) + 1] = hex(pc_loc)[2:].upper()

                    immediate_line = []

                    immediate_line.append(hex(pc_loc)[2:].upper())
                    immediate_line.append('*')
                    immediate_line.append(literal)
                    immediate_line.append('')
                    result = np.append(result, immediate_line)

                    if literal[1] == 'C':
                        pc_loc += len(literal) - 4
                    else:
                        pc_loc += int((len(literal) - 4) / 2)

                literals = np.array([])
            else:
                error("Invalid operation code", columns[1])
        else:
            if columns[1] == 'LTORG':

                immediate_line = []
                immediate_line.append('')
                immediate_line.append('')
                immediate_line.append("LTORG")
                immediate_line.append('')
                result = np.append(result, immediate_line)

                for literal in literals:
                    if star(sym_tab) == -1:
                        sym_tab_item = SymTabItem()
                        sym_tab_item.mnemonic = '*'
                        sym_tab_item.location = hex(pc_loc)[2:].upper()
                        sym_tab = np.append(sym_tab, sym_tab_item)
                    else:
                        sym_tab[star(sym_tab) + 1] = hex(pc_loc)[2:].upper()

                    immediate_line = []
                    immediate_line.append(hex(pc_loc)[2:].upper())
                    immediate_line.append('*')
                    immediate_line.append(literal)
                    immediate_line.append('')
                    result = np.append(result, immediate_line)
                    if literal[1] == 'C':
                        pc_loc += len(literal) - 4
                    else:
                        pc_loc += int(math.ceil((len(literal) - 4) / 2))
                literals = np.array([])
            else:
                immediate_line = []
                immediate_line.append(hex(pc_loc)[2:].upper())
                immediate_line.append('')
                immediate_line.append(columns[1])
                if columns[1] == 'RSUB':
                    immediate_line.append('')
                else:
                    immediate_line.append(columns[2])

                result = np.append(result, immediate_line)
                if mnemonic_exist(columns[1]):
                    pc_loc = pc_loc + 3
                    if columns[1] == 'RSUB':
                        result[len(result) - 1] = ''
                    elif len(columns[2]) and columns[2][0] == '=':
                        if not literal_exist(literals, columns[2]):
                            literals = np.append(literals, columns[2])

                elif columns[1] == "WORD":
                    pc_loc = pc_loc + 3
                elif columns[1] == "RESW":
                    pc_loc += (3 * columns[2])
                elif columns[1] == "RESB":
                    pc_loc += columns[2]
                elif columns[1] == "BYTE":
                    if columns[2][0] == 'C':
                        pc_loc += len(columns[2]) - 3
                    else:
                        pc_loc += int(math.ceil((len(columns[2]) - 3) / 2))

                elif columns[1] == 'END':
                    result[len(result) - 4] = ''

                    for literal in literals:
                        if star(sym_tab) == -1:
                            sym_tab_item = SymTabItem()
                            sym_tab_item.mnemonic = '*'
                            sym_tab_item.location = hex(pc_loc)[2:].upper()
                            sym_tab = np.append(sym_tab, sym_tab_item)
                        else:
                            sym_tab[star(sym_tab) +
                                    1] = hex(pc_loc)[2:].upper()
                        immediate_line = []
                        immediate_line.append(hex(pc_loc)[2:].upper())
                        immediate_line.append('*')
                        immediate_line.append(literal)
                        immediate_line.append('')
                        result = np.append(result, immediate_line)

                        if literal[1] == 'C':
                            pc_loc += len(literal) - 4
                        else:
                            pc_loc += (len(literal) - 4) / 2
                    literals = np.array([])
                else:
                    error("Invalid operation code")
    return result, sym_tab, pc_loc, initial_locator


def pass2(input):
    lst = np.array([])
    lst_result = np.array([])
    for line in input:
        columns = list(chunk_string(line, result_column_lengths))
        lst = np.append(lst, columns)

    lst = lst.reshape(-1, 4)
    proglen = lst[0][0]
    lst = lst[1:]
    for columns in lst:
        operand = ""
        opcode = ""
        if len(columns) == 4 and columns[3] != '':
            if columns[2] == 'START' or columns[2] == 'END':
                columns = np.append(columns, '')
                lst_result = np.append(lst_result, columns)
                continue
            elif columns[2] == 'RESB' or columns[2] == 'RESW':
                columns = np.append(columns, '')
                lst_result = np.append(lst_result, columns)
                continue
            elif columns[2] == 'WORD' or columns[2] == 'BYTE':
                if len(columns[3]) > 1 and columns[3].startswith('=C'):
                    operand = obj_code_of_string(columns[3][3:-1])
                elif len(columns[3]) > 1 and columns[3].startswith('=X'):
                    operand = columns[3][3:-1]
                else:
                    c_int = str(columns[3])
                    if not c_int.isnumeric():
                        error("Not Integer", c_int)
                    operand = str(hex(int(c_int))[2:]).zfill(6)
            else:
                if mnemonic_exist(columns[2]):
                    opcode = opcode_of_mnemonic(columns[2])
                    if columns[3][-1] == 'X' and columns[3][-2]:
                        result = indirect_addressing(lst, columns[3][:-2], 3)
                        if result != -1:
                            opcode = opcode + result
                        else:
                            error("Invalid operand ", columns[3])
                    elif columns[3][0] == '=':
                        result = indirect_addressing(lst, columns[3], 0)
                        if result != -1:
                            opcode = opcode + result
                        else:
                            error("Invalid operand ", columns[3])
                    else:
                        result = indirect_addressing(lst, columns[3], 1)
                        if result != -1:
                            opcode = opcode + result
                        else:
                            error("Invalid operand ", columns[3])

        elif columns[2] == 'RSUB':
            operand = '4C0000'

        else:
            if mnemonic_exist(columns[1]):
                opcode = opcode_of_mnemonic(columns[1])
                if columns[2][-1] == 'X' and columns[2][-2]:
                    result = indirect_addressing(lst, columns[2][:-2], 3)
                    if result != -1:
                        opcode = opcode + result
                    else:
                        error("Invalid Symbol ", columns[2])
                elif columns[2][0] == '=':
                    result = indirect_addressing(lst, columns[2], 0)
                    if result != -1:
                        opcode = opcode + result
                    else:
                        error("Invalid Symbol ", columns[2])
                else:
                    result = indirect_addressing(lst, columns[2], 1)
                    if result != -1:
                        opcode = opcode + result
                    else:
                        error("Invalid Symbol ", columns[2])
            else:
                if columns[1] == '*':
                    if columns[2].startswith('=C'):
                        operand = obj_code_of_string(columns[2][3:-1])
                    elif columns[2].startswith('=X'):
                        operand = columns[2][3:-1]
                    else:
                        c_int = columns[2][1:]
                        if not c_int.isnumeric():
                            error("Not Integer", c_int)
                        operand = str(hex(int(c_int))[2:]).zfill(6)

        if operand != '':
            columns = np.append(columns, operand)
        elif opcode != '':
            columns = np.append(columns, opcode)
        else:
            columns = np.append(columns, '')

        lst_result = np.append(lst_result, columns)
    lst_result = lst_result.reshape(-1, 5)

    final_objcode = np.array([])
    _list = np.array([])
    c = 0
    for columns in lst_result:
        line = ''
        if columns[2] == "START":
            line = 'H^' + columns[1] + '^' + \
                columns[0].zfill(6) + '^' + proglen.zfill(6) + '\n'
        elif columns[2] == 'END':
            line = 'E^' + lst_result[0][0].zfill(6) + '\n'
        else:
            if len(columns) == 1 or len(columns) == 2:
                continue
            elif columns[2] == "RESW" or columns[2] == 'RESB':
                if len(_list) == 0:
                    continue
                else:
                    line = 'T^' + \
                        _list[0].zfill(6) + '^' + hex(int(c * 0.5)
                                                      )[2:].zfill(2).upper() + '^'
                    c = 0
                    len_list = len(_list)
                    for index in range(1, len_list):
                        if index == len_list - 1:
                            line += _list[index] + ' \n'
                        else:
                            line += _list[index] + '^'
                    _list = np.array([])
            elif len(_list) == 0:
                column_length = len(columns)
                _list = np.append(_list, columns[0])
                _list = np.append(_list, columns[column_length - 1])
                c = c + len(columns[column_length - 1])
                continue
            else:
                column_length = len(columns)
                if c + len(columns[column_length - 1]) <= 60:
                    _list = np.append(_list, columns[column_length - 1])
                    c = c + len(columns[column_length - 1])
                    continue
                else:
                    line = 'T^' + \
                        _list[0].zfill(6) + '^' + hex(int(c * 0.5)
                                                      )[2:].zfill(2).upper() + '^'
                    c = 0
                    len_list = len(_list)
                    for index in range(1, len_list):
                        if index == len_list - 1:
                            line += _list[index] + '\n'
                        else:
                            line += _list[index] + '^'
                    _list = np.array([])
        final_objcode = np.append(final_objcode, line)
    return lst_result, final_objcode


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) != 3:
        error("Args missing or invalid")
        exit(-1)

    if not path.exists(args[1]):
        error("Input file is not exists")
    if args[0] == 'pass1':
        input = open(args[1], "r")
        result, symTab, pc_loc, initial_locator = pass1(input)
        input.close()

        program_len = hex(pc_loc - initial_locator)[2:].upper()
        print("LOCCTR:", pc_loc)
        print("PRGLTH:", program_len)
        print("PRGNAME:", result[1])
        print("SYMTAB:")
        for item in symTab:
            print(item)

        result = result.reshape(-4, 4)

        output = open(args[2], "w")
        output.write(str(program_len) + '\n')
        for line in result:
            str_line = ''
            index = 0
            for col in line:
                str_line += col.ljust(result_column_lengths[index])
                index += 1
            output.write(str_line + '\n')
        output.close()
    elif args[0] == 'pass2':
        input = open(args[1], "r")
        lst, obj_code = pass2(input)
        lst_output = open("listing.lst", "w")
        for line in lst:
            str_line = ''
            index = 0
            for col in line:
                str_line += col.ljust(result2_column_lengths[index])
                index += 1
            lst_output.write(str_line + '\n')
        lst_output.close()

        output = open(args[2], "w")
        for line in obj_code:
            output.write(line)
        output.close()
