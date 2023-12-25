from fractions import Fraction


def division_with_big_delta(divisible, divider):
    result = format((divisible / divider), ".16f")
    fractional_number = float(result)
    binary_representation = ""
    while True:
        fractional_number *= 2
        if fractional_number >= 1:
            binary_representation += "1"
            fractional_number -= 1
        else:
            binary_representation += "0"
        if len(binary_representation) > 17: # log2(65536) = 16
            break
    return "0." + binary_representation


def reduction_float(left_part, right_part):
    if right_part[0] == "1":
        for i in range(2, len(left_part)):
            if left_part[i] == "0":
                return left_part[:i] + "1"
        return left_part + "1"
    for i in range(2, len(left_part)):
        if right_part[i] == "1" and left_part[i] == "0":
            return right_part[:i+1]

def ratio_in_int2_str(ration : Fraction):
    result = ""
    numerator = ration.numerator
    denominator = ration.denominator
    while(numerator!=0):
        numerator *= 2**8
        part_float = numerator // denominator
        in_bite = bin(part_float)[2:]
        part = ('0' * (8 - len(in_bite)) + in_bite)
        result += part
        numerator = numerator % denominator

    result = "0," + result
    for i in range(len(result)-1, -1, -1):
        if result[i] != "0":
            result = result[:i+1]
            break
    if len(result) == 2:
        result = result + "0"
    return result

def convert_two_in_ratio(number):
    amount_decimal_places = len(number) - 2
    numerator = 0
    for i in range(2, len(number)):
        numerator *= 2
        if number[i] == "1":
            numerator += 1
    return Fraction(numerator, 2**amount_decimal_places)

def convert_byte_in_int(bytes):
    return int.from_bytes(bytes, byteorder='big')

def byte_in_bite(byte):
    in_bite = bin(convert_byte_in_int(byte))[2:]
    return '0' * (8 - len(in_bite)) + in_bite

def bite_in_byte(bite):
    if len(bite)!=8:
        raise Exception("aaaa")
    in_integer = int(bite, 2)
    return in_integer.to_bytes(1, 'big')

def bite_in_int(bite):
    return int(bite, 2)




