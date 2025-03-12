

import gc
gc.collect()


def get_single_operator(operator: str):
    if operator == "!=":
        return lambda x, y: x != y
    elif operator == "<":
        return lambda x, y: x > y
    elif operator == ">":
        return lambda x, y: x < y
    elif operator == "<=":
        return lambda x, y: x >= y
    elif operator == ">=":
        return lambda x, y: x <= y
    else:
        return lambda x, y: x == y

def get_double_operator(operator: str):
    if operator == "<>":
        return lambda x, y, z: x < z < y
    elif operator == "<=>":
        return lambda x, y, z: x <= z <= y
    elif operator == "<>=":
        return lambda x, y, z: x < z <= y
    elif operator == "=<>":
        return lambda x, y, z: x <= z < y

    elif operator == "><":
        return lambda x, y, z: z < x or z > y
    elif operator == ">=<":
        return lambda x, y, z: z <= x or z >= y
    elif operator == "><=":
        return lambda x, y, z: z < x or z >= y
    elif operator == "=><":
        return lambda x, y, z: z <= x or z > y

    else:
        return lambda x, y, z: x == y == z

def get_operator(operator: str, upper: bool = False):
    return get_double_operator(operator) if upper else get_single_operator(operator)


def get_single_operator_expand(operator: str):
    if operator.startswith("<"):
        return 1
    elif operator.startswith(">"):
        return -1
    else:
        return 0

def get_double_operator_expand(operator: str):
    lower = operator.find("<")
    upper = operator.find(">")
    if lower == -1 or upper == -1:
        return 0, 0
    if lower > upper:
        return 1, -1
    else:
        return -1, 1

def get_operator_expand(operator: str, upper: bool = False) -> tuple[int, int]:
    return get_double_operator_expand(operator) if upper else get_single_operator_expand(operator), 0


gc.collect()
