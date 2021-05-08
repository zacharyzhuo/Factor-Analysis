from itertools import product
from flask import jsonify
from flask_restful import Resource
from flask_restful import request


class TaskApi(Resource):

    def get(self):
        output = []
        try:
            factor_list = request.args.getlist('factor_list')
            strategy_list = list(map(int, request.args.getlist('strategy_list')))
            window_list = list(map(int, request.args.getlist('window_list')))
            method_list = list(map(int, request.args.getlist('method_list')))
            group_list = list(map(int, request.args.getlist('group_list')))
            position_list = list(map(int, request.args.getlist('position_list')))
            print(factor_list)

            data = (
                factor_list, strategy_list, window_list, 
                method_list, group_list, position_list
            )

            for combi in product(*data):
                if combi[1] == '0':
                    if combi[2] != '0' or combi[3] == '1':
                        continue
                output.append(combi)

            return jsonify({"result": output})

        except Exception as e:
            print("[Error]: {}".format(e))
            return jsonify({"Error": e})
            pass
