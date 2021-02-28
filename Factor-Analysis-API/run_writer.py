import time

from writer.write_stk_data import proc_stk_data
from writer.write_stk_data import trans_stk_to_one_symbol


from writer.mom_calculator import MOMCalculator
from writer.calendar_writer import CalendarWriter
from writer.indicator_writer import IndicatorWriter
from writer.factor_writer import FactorWriter


# ind_dict = proc_ind_data()
# ticker_data_dict = trans_ind_to_one_symbol(ind_dict)
# write_data_to_mysql('indicator', ticker_data_dict)


# factor_dict = cal_factor_data()
# write_data_to_mysql('factor', factor_dict)


# proc_stk_data()

# ticker_dict = trans_stk_to_one_symbol()
# write_data_to_mysql('stock2', ticker_dict)


# ind_dict = proc_ind_data()
# ticker_data_dict = trans_ind_to_one_symbol(ind_dict)
# write_data_to_mysql('indicator', ticker_data_dict)

# start = time.time()
# MOMCalculator()
# end = time.time()
# print("Execution time: %f second" % (end - start))

FactorWriter()