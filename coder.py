from fractions import Fraction
from math import log2, ceil
from knuth_morris_prath_algorithm import KnuthMorrisPrathAlgorithm
from work_with_small_float import division_with_big_delta, reduction_float, ratio_in_int2_str, convert_two_in_ratio


class Coder():
    def __init__(self, data):
        self.original_data = data
        self.position = 0
        self.max_bite_for_offset = self.nearest_up_degree_two((len(data) * 2**12) / 2**16)
        self.max_bite_for_len = self.nearest_up_degree_two((len(data) * 2**9) / 2**16)
        self.algorithm = KnuthMorrisPrathAlgorithm()
        self.max_len_for_probability = self.nearest_up_degree_two(len(data))

    def nearest_up_degree_two(self, number):
        return max(0, ceil(log2(number)))


    def run(self):
        delta_coding = self.delta_cod(self.original_data)
        sliding_window_coding = self.sliding_window_code(delta_coding)
        number, sorted_dict = self.interval_code(sliding_window_coding)
        compress_text_str = self.convert_in_byte(sorted_dict, number)
        if len(compress_text_str) % 8 != 0:
            compress_text_str = compress_text_str + '0' * (8-len(compress_text_str) % 8)
        decimal_num = int(compress_text_str, 2)
        len_compress_in_byte = len(compress_text_str)//8
        byte_compress = decimal_num.to_bytes(len_compress_in_byte, 'big')
        return byte_compress


    def delta_cod(self, data: str):
        list_deltas = []
        last_char = None
        for char in data:
            curr_index_char = ord(char)
            if last_char is None:
                list_deltas.append(chr(curr_index_char).encode('utf-8'))
            else:
                next_id = (curr_index_char - last_char) % 256
                delta = next_id.to_bytes(1, 'big')
                list_deltas.append(delta)
            last_char = curr_index_char
        return b''.join(list_deltas)

    def try_compress_next_part(self, part_for_compressed, data):
        len_which_refer = 2**self.max_bite_for_len - 1
        while len_which_refer > 4:
            if len(part_for_compressed) < len_which_refer:
                len_which_refer = len(part_for_compressed)
                continue
            if len(data) - self.position < len_which_refer:
                len_which_refer = len(data) - self.position
                continue
            part_which_need_compress = data[self.position : self.position + len_which_refer]
            found_index = self.algorithm.find_substring_in_string(part_for_compressed, part_which_need_compress)
            if found_index != -1:
                offset = self.position - found_index
                self.position += len_which_refer
                next_symbol = None
                if self.position < len(data):
                    next_symbol = data[self.position]
                self.position += 1
                return offset, len_which_refer, next_symbol
            len_which_refer -= 1
        return None
    def sliding_window_code(self, data):
        list_tuple_compressed_part = []
        while self.position < len(data):
            part_for_compressed = data[max(0, self.position - 2 ** self.max_bite_for_offset): self.position]
            next_tup = self.try_compress_next_part(part_for_compressed, data)
            if next_tup is None:
                list_tuple_compressed_part.append((0, 0, data[self.position]))
                self.position += 1
            else:
                list_tuple_compressed_part.append(next_tup)
        return list_tuple_compressed_part



    def create_dict_repetitions(self, data):
        dict_repetitions = dict()
        for tup in data:
            if tup in dict_repetitions.keys():
                dict_repetitions[tup] += 1
            else:
                dict_repetitions[tup] = 1
        return dict_repetitions

    def convert_int10_in_int2_str(self, number):
        return format(number, 'b')


    def get_dict_with_numeric_line_not_normal(self, keys_and_values_list):
        last_value = None
        new_dict = {}
        for keys_and_value in keys_and_values_list:
            if last_value is None:
                new_dict[keys_and_value[0]] = (0, keys_and_value[1])
                last_value = keys_and_value[1]
            else:
                new_dict[keys_and_value[0]] = (last_value, keys_and_value[1] + last_value)
                last_value = keys_and_value[1] + last_value
        return new_dict

    def get_dict_with_numeric_line_normal(self, not_normal_dict, amount_part):
        for key in not_normal_dict.keys():
            left_part = division_with_big_delta(not_normal_dict[key][0], amount_part)
            right_part = division_with_big_delta(not_normal_dict[key][1], amount_part)
            not_normal_dict[key] = (left_part, right_part)
        return not_normal_dict


    def get_dict_in_float(self, reduction_dict):
        reduction_dict_in_float = dict()
        for key in reduction_dict.keys():
            left_border = convert_two_in_ratio(reduction_dict[key][0])
            right_border = convert_two_in_ratio(reduction_dict[key][1])
            reduction_dict_in_float[key] = (left_border, right_border)
        return reduction_dict_in_float

    def reduction_dict_in_float_convert_in_span_dict(self, data, keys_and_values_float_sorted):
        new_dict = {}
        last_right_border = None
        for keys_and_value in keys_and_values_float_sorted:
            if last_right_border is None:
                left_border = Fraction(0)

                right_border = keys_and_value[1][1]
                delta_for_reduce_in_str = ratio_in_int2_str(right_border)
                delta_reduce = reduction_float('0' * len(delta_for_reduce_in_str), delta_for_reduce_in_str)
                delta_in_ratio = convert_two_in_ratio(delta_reduce)

                new_dict[keys_and_value[0]] = (Fraction(0), delta_in_ratio)
                last_right_border = delta_in_ratio
            else:
                left_border = last_right_border
                right_border = keys_and_value[1][1]
                delta = right_border - left_border
                delta_in_str = ratio_in_int2_str(delta)
                delta_reduce = reduction_float('0' * len(delta_in_str), delta_in_str)
                delta_in_ratio = convert_two_in_ratio(delta_reduce)

                new_dict[keys_and_value[0]] = (left_border, delta_in_ratio)
                last_right_border = left_border + delta_in_ratio
        return new_dict

    def convert_in_number_data(self, data, dict_float_span):
        start = Fraction(0)
        width = Fraction(1)
        c = 0
        for symbol in data:
            symbol_span = dict_float_span[symbol]
            start += width * symbol_span[0]
            width *= symbol_span[1]
            c+=1
        return start

    def interval_code(self, data):
        amount_parts = len(data)
        dict_repetitions = self.create_dict_repetitions(data)
        keys_and_values_sorted = sorted(dict_repetitions.items(), key=lambda tup: tup[1])
        dict_with_numeric_line_not_normal = self.get_dict_with_numeric_line_not_normal(keys_and_values_sorted)
        normal_dict = self.get_dict_with_numeric_line_normal(dict_with_numeric_line_not_normal, amount_parts)
        dict_in_float = self.get_dict_in_float(normal_dict)
        keys_and_values_float_sorted = sorted(dict_in_float.items(), key=lambda tup: tup[1])
        dict_float_span = self.reduction_dict_in_float_convert_in_span_dict(data, keys_and_values_float_sorted)
        dict_float_span_sorted = sorted(dict_float_span.items(), key=lambda tup: tup[1])
        number_in_ratio = self.convert_in_number_data(data, dict_float_span)
        return ratio_in_int2_str(number_in_ratio), dict_float_span_sorted

    def add_int_with_size(self, number, size, result):
        in_bite = bin(number)[2:]
        add_part = ('0' * (size - len(in_bite)) + in_bite)
        return result + add_part

    def add_char(self, char, result):
        number = int(char)
        result = self.add_int_with_size(number, 8, result)
        return result

    def add_float_str(self, number_str, result):
        needed_part = ratio_in_int2_str(number_str)[2:18]
        if (len(needed_part) > self.max_len_for_probability):
            needed_part = needed_part[:self.max_len_for_probability]
        add_part = needed_part + '0' * (self.max_len_for_probability - len(needed_part))
        result = result + add_part
        return result


    def convert_in_byte(self, sorted_dict: list, number: str):
        result = ""          # максимальное кол-во ключей в словаре рано 65 536
        a = convert_two_in_ratio(number)
        result = self.add_int_with_size(len(self.original_data), 16, result)
        result = self.add_int_with_size(len(sorted_dict), 16, result)
        need_delete_end = False
        for key_and_value in sorted_dict:
            offset = key_and_value[0][0]
            _len = key_and_value[0][1]
            _next_symbol = key_and_value[0][2]
            probability = key_and_value[1]
            if offset != 0:
                result = result + "1"
                result = self.add_int_with_size(offset, self.max_bite_for_offset, result)
                result = self.add_int_with_size(_len, self.max_bite_for_len, result)
            else:
                result = result + "0"
            if _next_symbol is not None:
                result = self.add_char(_next_symbol, result)
            else:
                need_delete_end = True
                result = self.add_char(0, result)
            result = self.add_float_str(probability[1], result)
        needed_part = number[2:]
        result = result + needed_part
        if need_delete_end:
            result = "1" + result
        else:
            result = "0" + result
        return result



