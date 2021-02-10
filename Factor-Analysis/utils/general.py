

class General:

    def __init__(self):
        pass

    @staticmethod
    def string_to_list(string, d_type='string', sep='|'):
        """
        將list的字串轉換回list型態

        :param string: string (Require)
            傳入原始list之字串
        :param d_type: string (Optional)
            指定list中各元素之型態，可指定為string（預設）、int、float
        :param sep: string (Optional)
            分隔之符號，預設為「|」
        :return: string_list: list
            回傳字串解析結果
        """
        if d_type == 'string':
            string_list = [n for n in string.split(sep)]
        elif d_type == 'int':
            string_list = [int(n) for n in string.split(sep)]
        elif d_type == 'float':
            string_list = [float(n) for n in string.split(sep)]

        return string_list

    @staticmethod
    def list_to_string(ori_list, sep='|'):
        """
        將list轉換成字串（以特殊符號分隔）

        :param ori_list: list (Require)
            原始之list要轉換成字串
        :param sep: string (Optional)
            分隔之符號，預設為「|」
        :return:
        """
        string = ""
        if len(ori_list) == 0:
            pass
        else:
            # 使用特殊符號作區隔
            for sub_list in ori_list:
                string = string + sep + str(sub_list)
            string = string[1:]
        return string
    
    @staticmethod
    def factor_string_to_list(string, d_type='string', sep='|'):
        """
        將factor list的字串轉換回list(2D)型態
        （1D: 以"|"分隔 2D: 以"&"分隔）

        :param string: string (Require)
            傳入原始list之字串
        :param d_type: string (Optional)
            指定list中各元素之型態，可指定為string（預設）、int、float
        :param sep: string (Optional)
            1D: 以"|"分隔 2D: 以"&"分隔
        :return: string_list: list
            回傳字串解析結果
        """
        if d_type == 'string':
            string_list = [n.split('&') for n in string.split(sep)]
        elif d_type == 'int':
            string_list = [int(n) for n in string.split(sep)]
        elif d_type == 'float':
            string_list = [float(n) for n in string.split(sep)]

        return string_list

    @staticmethod
    def factor_list_to_string(ori_list, sep='|'):
        """
        將factor list(2D)轉換成字串
        （1D: 以"|"分隔 2D: 以"&"分隔）

        :param ori_list: list (Require)
            原始之list要轉換成字串
        :param sep: string (Optional)
            元素之間分隔之符號「|」 因子之間分隔之符號「&」
        :return:
        """
        string = ""
        if len(ori_list) == 0:
            pass
        else:
            # 使用特殊符號作區隔
            for sub_list in ori_list:
                if len(sub_list) == 1:
                    string = string + sep + str(sub_list[0])
                elif len(sub_list) == 2:
                    string = string + sep + "{}&{}".format(str(sub_list[0]), str(sub_list[1]))
            string = string[1:]
        return string

    @staticmethod
    def list_to_dict(key_column, data):
        result_dict = dict()

        for item in data:
            result_dict.update({item[key_column]: item})
        return result_dict
