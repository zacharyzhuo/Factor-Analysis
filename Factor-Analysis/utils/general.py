from itertools import product


class General:

    def __init__(self):
        pass

    # 排列組合各種參數
    @staticmethod
    def combinate_parameter(factor_list, strategy_list, date_2, date_3):
        data = factor_list, strategy_list, date_2, date_3
        task_list = []
        for x, y, z, w in product(*data):
            # 單因子不能執行策略 1
            if len(x) == 1 and y != 1:
                task_list.append([x, y, z, w])
            # 雙因子不能執行策略 0
            if len(x) == 2 and y != 0:
                task_list.append([x, y, z, w])
        return task_list

    # 將整串request factor list抓出不重複的因子 回傳一個陣列
    @staticmethod
    def get_distinct_factor_list(org_factor_list):
        factor_list = []

        # 找出不重複的因子
        for elm in org_factor_list:
            for factor in elm:
                if factor not in factor_list:
                    factor_list.append(factor)
        return factor_list

    # 將以某符號間格的字串(預設'|') 轉成list 方便寫入資料庫
    @staticmethod
    def string_to_list(string, d_type='string', sep='|'):
        if d_type == 'string':
            string_list = [n for n in string.split(sep)]
        elif d_type == 'int':
            string_list = [int(n) for n in string.split(sep)]
        elif d_type == 'float':
            string_list = [float(n) for n in string.split(sep)]

        return string_list

    # 將list轉成字串並中間以某符號間格(預設'|') 方便寫入資料庫
    @staticmethod
    def list_to_string(ori_list, sep='|'):
        string = ""
        if len(ori_list) == 0:
            pass
        else:
            # 使用特殊符號作區隔
            for sub_list in ori_list:
                string = string + sep + str(sub_list)
            string = string[1:]
        return string
    
    # 將雙因子之間以'&'間隔 而各因子之間以'|'間隔的字串轉為list
    @staticmethod
    def factor_string_to_list(string, d_type='string', sep='|'):
        if d_type == 'string':
            string_list = [n.split('&') for n in string.split(sep)]
        elif d_type == 'int':
            string_list = [int(n) for n in string.split(sep)]
        elif d_type == 'float':
            string_list = [float(n) for n in string.split(sep)]

        return string_list

    # 將request factor list轉成 雙因子之間以'&'間隔 而各因子之間以'|'間隔的字串
    @staticmethod
    def factor_list_to_string(ori_list, sep='|'):
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

    # 將某一個陣列元素中的因子轉成字串 如果是雙因子中間以'&'間隔
    @staticmethod
    def factor_to_string(ori_list):
        if len(ori_list) == 1:
            return ori_list[0]
        elif len(ori_list) == 2:
            return "{}&{}".format(ori_list[0], ori_list[1])

    # 陣列轉成字典
    @staticmethod
    def list_to_dict(key_column, data):
        result_dict = dict()

        for item in data:
            result_dict.update({item[key_column]: item})
        return result_dict
