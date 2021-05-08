from api import calendar, stock, stock_index, indicator, factor, task

def create_routes(api):
    # calendar api
    api.add_resource(calendar.TradeDateApi, '/cal')
    api.add_resource(calendar.AllTradeDateApi, '/cal/get_all_date')
    api.add_resource(calendar.ReportDateListApi, '/cal/get_report_date_list')

    # stock api
    api.add_resource(stock.StkListApi, '/stk/stk_list')
    api.add_resource(stock.StkByTickerApi, '/stk/get_ticker_all_stk')
    api.add_resource(stock.StkByTickerDateApi, '/stk/get_ticker_period_stk')

    # stock index api
    api.add_resource(stock_index.StkIdxListApi, '/stk_idx/stk_idx_list')
    api.add_resource(stock_index.StkIdxByTickerApi, '/stk_idx/get_ticker_all_stk_idx')
    api.add_resource(stock_index.StkIdxByTickerDateApi, '/stk_idx/get_ticker_period_stk_idx')

    # indicator api
    api.add_resource(indicator.IndListApi, '/ind/stk_list')
    api.add_resource(indicator.IndByTickerApi, '/ind/get_ticker_all_ind')
    api.add_resource(indicator.IndByTickerFeildApi, '/ind/get_ticker_ind')
    api.add_resource(indicator.IndByDateFeildApi, '/ind/get_date_ind')

    # factor api
    api.add_resource(factor.FacListApi, '/fac/stk_list')
    api.add_resource(factor.FacByTickerApi, '/fac/get_ticker_all_fac')
    api.add_resource(factor.FacByTickerFeildApi, '/fac/get_ticker_fac')
    api.add_resource(factor.FacByDateFeildApi, '/fac/get_date_fac')

    api.add_resource(task.TaskApi, '/task/get_task_combi')
