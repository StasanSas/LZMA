from math import ceil, log2
from work_with_small_float import  convert_two_in_ratio, bite_in_int
from knuth_morris_prath_algorithm import KnuthMorrisPrathAlgorithm

class DeCoder():
    def __init__(self, data_byte):
        self.data = data_byte
        self.pos_read_bite = 0
        self.pos_alg = 0
        self.max_bite_for_offset = None
        self.max_bite_for_len = None
        self.len_original_data = None
        self.len_dictionary = None
        self.max_len_for_probability = None
        self.algorithm = KnuthMorrisPrathAlgorithm()
        self.need_delete_end = False

    def nearest_up_degree_two(self, number):
        return max(0, ceil(log2(number)))

    def read_size_bite(self, size):
        result = self.data[self.pos_read_bite: self.pos_read_bite + size]
        self.pos_read_bite += size
        return result

    def setting_parameters(self):
        self.need_delete_end = ("1" == self.read_size_bite(1))
        self.len_original_data = bite_in_int(self.read_size_bite(16))
        self.len_dictionary = bite_in_int(self.read_size_bite(16))
        self.max_bite_for_offset = self.nearest_up_degree_two((self.len_original_data * 2**12) / 2**16)
        self.max_bite_for_len = self.nearest_up_degree_two((self.len_original_data * 2**9) / 2**16)
        self.max_len_for_probability = self.nearest_up_degree_two(self.len_original_data)

    def run(self):
        self.data = ''.join(format(byte, '08b') for byte in self.data)
        self.setting_parameters()
        number, _dict_in_sort_list = self.decode_in_dict_and_number(self.data)
        list_tup = self.decode_interval(number, _dict_in_sort_list)
        message_delta = self.decode_sliding_window(list_tup)
        encode_message = self.decode_delta(message_delta)
        if self.need_delete_end:
            encode_message = self.need_delete_end[:-1]
        return encode_message

    def decode_in_dict_and_number(self, binary_string):
        _dict_in_sort_list = []
        for i in range(self.len_dictionary):
            is_refer = ("1" == self.read_size_bite(1))
            if is_refer:
                offset = int(self.read_size_bite(self.max_bite_for_offset), 2)
                _len = int(self.read_size_bite(self.max_bite_for_len), 2)
            else:
                offset = 0
                _len = 0
            next_symbol = int(self.read_size_bite(8), 2)
            a = self.read_size_bite(self.max_len_for_probability)
            probability = convert_two_in_ratio("0," + a)
            _dict_in_sort_list.append(((offset, _len, next_symbol), probability))
        number_str = "0," + self.data[self.pos_read_bite:]
        number = convert_two_in_ratio(number_str)
        return number, _dict_in_sort_list


    def get_span_dict(self, _dict_in_sort_list):
        span_dict_sorted = []
        last_right_border = None
        for key_and_value in _dict_in_sort_list:
            if last_right_border is None:
                span_dict_sorted.append((key_and_value[0], (0, key_and_value[1])))
                last_right_border = key_and_value[1]
            else:
                span_dict_sorted.append((key_and_value[0], (last_right_border, key_and_value[1] - last_right_border)))
                last_right_border = key_and_value[1]
        return span_dict_sorted

    def get_list_refs_and_letters(self, number, span_dict_sorted):
        result = []
        start = 0
        delta = 1
        while number.numerator != 0:
            for key_and_value in span_dict_sorted:
                if key_and_value[1][0] <= number < key_and_value[1][0] + key_and_value[1][1]:
                    result.append(key_and_value[0])
                    start = key_and_value[1][0]
                    delta = key_and_value[1][1]
                    break
            number = (number - start) / delta
        return result

    def get_right_border(self, _dict_in_sort_list):
        result = []
        curr_left_border = 0
        for key_and_value in _dict_in_sort_list:
            result.append((key_and_value[0], key_and_value[1] + curr_left_border))
            curr_left_border = key_and_value[1] + curr_left_border
        return result


    def decode_interval(self, number, _dict_in_sort_list):
        right_border_dict = self.get_right_border(_dict_in_sort_list)
        span_dict_sorted = self.get_span_dict(right_border_dict)
        decode_message = self.get_list_refs_and_letters(number, span_dict_sorted)
        return decode_message

    def decode_sliding_window(self, list_tup):
        result = b""
        for tup in list_tup:
            offset = tup[0]
            _len = tup[1]
            next_symbol = tup[2].to_bytes(1, 'big')
            add_part = result[len(result)-offset: len(result)-offset + _len]
            result = result + add_part + next_symbol
        return result

    def decode_delta(self, message_delta):
        result = ""
        last_symbol = None
        for byte_in_int in message_delta:
            if last_symbol is None:
                add_symbol_in_int = byte_in_int
                result = result + chr(add_symbol_in_int)
                last_symbol = add_symbol_in_int
            else:
                add_symbol_in_int = (byte_in_int + last_symbol) % 256
                result = result + chr(add_symbol_in_int)
                last_symbol = add_symbol_in_int
        return result


