from scipy import stats
from HEBenchMark import HEBenchMark


# HEBenchMark.evaluate_from_file('results/ckks.csv')

file_name = 'results/ckks.csv'

with open(file_name, 'r') as f:
    records = [e for e in f.readlines() if len(e) > 0]
    records = [[e1.strip(' ') for e1 in e.strip('\n').split(',')] for e in records]
    header, records = records[0], records[1:]


def t_test(group_by, test):
    data = [[e[header.index(group_by)], float(e[header.index(test)])] for e in records]
    data_sequence = {}
    for r in data:
        data_sequence[r[0]] = data_sequence.get(r[0], []) + [r[1]]
    significance = []
    for k1, v1 in data_sequence.items():
        for k2, v2 in data_sequence.items():
            if k1 == k2:
                continue
            significance.append([k1, k2] + list(stats.ttest_rel(v1, v2)))
    return significance


# Tasks
# (1) IntMax vs. Time&Error

significance_result = t_test('IntMax', 'encrypt(m)')

print(significance_result)