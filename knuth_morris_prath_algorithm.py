

class KnuthMorrisPrathAlgorithm():

    """
        Очень эффективен в случае, если в строке и подстроке содержатся повторяющиеся последовательности.
        Например,применяется для поиска для анализа геномов живых существ.
        Геном шифруется 4 символам часто встречаются повторяющиеся последовательности. Сложность O(n+m)
        с учётом предварительной обработки
    """
    @staticmethod
    def __found_prefix_array_substring(sub_str):
        prefix_array = [0] * len(sub_str)
        i_sign_compared = 0
        current_index = 1

        while current_index < len(sub_str):
            if sub_str[i_sign_compared] == sub_str[current_index]:
                prefix_array[current_index] = i_sign_compared + 1
                current_index += 1  # если буквы схожи то присваиваем значение,учитывая схожесть
                i_sign_compared += 1  # предыдуших постфикса и префикса
            else:  # иначе
                if i_sign_compared > 0:  # находим постфикс наибольшей. длинны,без сравниваемой буквы равный префиксу
                    i_sign_compared = prefix_array[i_sign_compared - 1]
                else:  # если первый знак постфикса не совпадает,то присваеваем 0
                    current_index += 1
        return prefix_array

    @staticmethod
    def __algoritm_knuth_morris_prath(str, sub_str):
        i_elem_str = 0
        i_elem_sub_str = 0
        prefix_array = KnuthMorrisPrathAlgorithm.__found_prefix_array_substring(sub_str)
        while i_elem_str < len(str):
            if sub_str[i_elem_sub_str] == str[i_elem_str]:
                i_elem_str += 1  # сравниваем как обычно элементы
                i_elem_sub_str += 1

                if i_elem_sub_str == len(sub_str):
                    return i_elem_str - len(sub_str)

            elif i_elem_sub_str > 0:
                # мы знаем какие были предыдущие буквы в строке,котор. мы сравнивали с бодстрочными,поэтому
                # переносим индекс в подстроке так,чтобы были в начале хорошие буквы
                i_elem_sub_str = prefix_array[i_elem_sub_str - 1]
            else:
                # ну,тут точно строка не содержится в бодстроке,переходим к следующий позиции
                i_elem_str += 1
        # если подстока не найдена
        return -1

    def find_substring_in_string(self, str, sub_str):
        if self.is_correct_data(str, sub_str):
            return KnuthMorrisPrathAlgorithm.__algoritm_knuth_morris_prath(str, sub_str)
        return -1


if __name__ =="__main__":
    algorithm = KnuthMorrisPrathAlgorithm()
    print(algorithm.find_substring_in_string('abcdefg', 'de'))
    print(algorithm.find_substring_in_string('abdefcdefg', 'cd'))
