from writer.write_ind_data import proc_ind_data
from writer.write_ind_data import trans_ind_to_one_symbol
from writer.write_ind_data import write_data_to_mysql

from writer.write_factor_data import cal_factor_data


# ind_dict = proc_ind_data()
# ticker_data_dict = trans_ind_to_one_symbol(ind_dict)
# write_data_to_mysql('indicator', ticker_data_dict)


factor_dict = cal_factor_data()
write_data_to_mysql('factor', factor_dict)