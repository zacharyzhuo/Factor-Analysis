from itertools import product
from flask import jsonify
from flask_restful import Resource
from flask_restful import request
from utils.general import General


class TaskApi(Resource):

    def get(self):
        output = []
        
        try:
            factor_list_str = request.args.get('factor_list')
            strategy_list = list(map(int, request.args.getlist('strategy_list')))
            window_list = list(map(int, request.args.getlist('window_list')))
            method_list = list(map(int, request.args.getlist('method_list')))
            group_list = list(map(int, request.args.getlist('group_list')))
            position_list = list(map(int, request.args.getlist('position_list')))

            factor_list = General().factor_string_to_list(factor_list_str)

            data = (
                factor_list, strategy_list, window_list, 
                method_list, group_list, position_list
            )

            for combi in product(*data):
                # strategy: B&H
                if combi[1] == 0:
                    # B&H 排除0之外的窗格 排除等權重之外的方法
                    if combi[2] != 0 or combi[3] != 0: 
                        continue
                output.append(combi)

            return jsonify({"result": output})

        except Exception as e:
            print("[Error]: {}".format(e))
            return jsonify({"Error": e})
            pass
