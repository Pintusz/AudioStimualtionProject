import pandas as pd
import constants as c
import sleep_stage_classifer as s


def check_pip(tester_list):
    last_probas = [{k: v for k, v in elem.items() if k != 'Stage'} for elem in tester_list[-c.CHECK_LEN:]]
    conditions_met_count = sum((elem['N2'] + elem['N3'] > 0.85) and (elem['N3'] <= 0.5) for elem in last_probas)
    if len(last_probas) < c.CHECK_LEN:
        return False
    return conditions_met_count >= c.CHECK_LEN-1        #egy híján mindre igaz

