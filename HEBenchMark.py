import os
import copy
import time
import random
import psutil
import numpy as np
from scipy import stats


class HEBenchMark:

    def __init__(self,
                 pub_key, sec_key, output_file_name='result.csv',
                 encrypt_params: dict = None,
                 output_infos: tuple = ('HE Name', 'Params')):
        self.pub_key = pub_key
        self.sec_key = sec_key
        self.encrypt_params = encrypt_params
        self.output_file_name = output_file_name
        if not os.path.isdir(os.path.dirname(self.output_file_name)):
            os.makedirs(os.path.dirname(self.output_file_name))
        self.output_infos = output_infos

        self.run_time = {
            'encrypt': [], 'decrypt': [], 'c+c': [], 'c+p': [], 'c*c': [], 'c*p': []
        }
        self.error = {
            'c+c': [], 'c+p': [], 'c*c': [], 'c*p': []
        }
        self.ram = {
            'encrypt': [], 'c+c': [], 'c+p': [], 'c*c': [], 'c*p': []
        }

    def encrypt(self, value_list):
        # The ram size could be correctly calculated using Linux
        start_RAM = psutil.Process(os.getpid()).memory_info().rss
        if self.encrypt_params is not None:
            start = time.time()
            results = [self.pub_key.encrypt(e, **self.encrypt_params) for e in value_list]
        else:
            start = time.time()
            results = [self.pub_key.encrypt(e) for e in value_list]
        end = time.time()
        end_RAM = psutil.Process(os.getpid()).memory_info().rss
        self.run_time['encrypt'].append((end - start) / len(results) * 1000)
        self.ram['encrypt'].append((end_RAM - start_RAM) / len(results) / 2 ** 20)
        return results

    def decrypt(self, value_list):
        start = time.time()
        results = [self.sec_key.decrypt(e) for e in value_list]
        end = time.time()
        self.run_time['decrypt'].append((end - start) / len(results) * 1000)
        return results

    @staticmethod
    def wape(decrypted, real_vale):
        # weighted average percentage error
        return np.sum(np.abs(np.array(decrypted) - np.array(real_vale))) / np.sum(np.abs(real_vale))

    @staticmethod
    def safe_mape(decrypted, real_vale):
        # Add (real_vale == 0) to mute the warnings
        mape = np.abs(decrypted - real_vale) / np.abs(real_vale + (real_vale == 0))
        mape[np.where(real_vale == 0)] = 0
        return np.sum(mape) / np.sum(real_vale != 0)

    def add(self, v1, v2, true_result):
        assert len(v1) == len(v2)
        start_RAM = psutil.Process(os.getpid()).memory_info().rss
        start = time.time()
        results = [v1[i] + v2[i] for i in range(len(v1))]
        end = time.time()
        end_RAM = psutil.Process(os.getpid()).memory_info().rss
        decrypt_result = self.decrypt(results)
        if isinstance(v2[0], type(v1[0])):
            self.run_time['c+c'].append((end - start) / len(results) * 1000)
            self.ram['c+c'].append((end_RAM - start_RAM) / len(results) / 2 ** 20)
            self.error['c+c'].append(self.safe_mape(decrypted=decrypt_result, real_vale=true_result))
        else:
            self.run_time['c+p'].append((end - start) / len(results) * 1000)
            self.ram['c+p'].append((end_RAM - start_RAM) / len(results) / 2 ** 20)
            self.error['c+p'].append(self.safe_mape(decrypted=decrypt_result, real_vale=true_result))
        return results

    def multiply(self, v1, v2, true_result):
        assert len(v1) == len(v2)
        start_RAM = psutil.Process(os.getpid()).memory_info().rss
        start = time.time()
        results = [v1[i] * v2[i] for i in range(len(v1))]
        end = time.time()
        end_RAM = psutil.Process(os.getpid()).memory_info().rss
        decrypt_result = self.decrypt(results)
        if isinstance(v2[0], type(v1[0])):
            self.run_time['c*c'].append((end - start) / len(results) * 1000)
            self.error['c*c'].append(self.safe_mape(decrypted=decrypt_result, real_vale=true_result))
            self.ram['c*c'].append((end_RAM - start_RAM) / len(results) / 2 ** 20)
        else:
            self.run_time['c*p'].append((end - start) / len(results) * 1000)
            self.error['c*p'].append(self.safe_mape(decrypted=decrypt_result, real_vale=true_result))
            self.ram['c*p'].append((end_RAM - start_RAM) / len(results) / 2 ** 20)
        return results

    @staticmethod
    def get_machine_info():
        num_logical_cpu = psutil.cpu_count(logical=True)
        cpu_freq_min = psutil.cpu_freq().min
        cpu_freq_max = psutil.cpu_freq().max
        cpu_freq_current = psutil.cpu_freq().current
        memory = psutil.virtual_memory().total / 2**30
        return num_logical_cpu, cpu_freq_min, cpu_freq_max, cpu_freq_current, memory

    def run(self, test_objects=('c+c', 'c+p'), SIMD=False, sample_size=1000, int_max=10000, float_max=1.0):
        if SIMD:
            shuffled_plain_text = np.random.randint(low=1, high=int_max,
                                                    size=[sample_size, self.pub_key.slot_count]).tolist() + \
                                  np.random.randint(low=-int_max, high=-1,
                                                    size=[sample_size, self.pub_key.slot_count]).tolist() + \
                                  (np.random.random([sample_size, self.pub_key.slot_count]) * float_max).tolist() + \
                                  (-1 * (np.random.random([sample_size, self.pub_key.slot_count])) * float_max).tolist()
        else:
            shuffled_plain_text = np.random.randint(low=1, high=int_max, size=sample_size).tolist() + \
                                  np.random.randint(low=-int_max, high=-1, size=sample_size).tolist() + \
                                  (np.random.random([sample_size]) * float_max).tolist() + \
                                  (-1 * (np.random.random([sample_size]) * float_max)).tolist()

        plain_text = copy.deepcopy(shuffled_plain_text)
        random.shuffle(shuffled_plain_text)

        # Encrypt
        cipher_text = self.encrypt(plain_text)
        shuffled_cipher_text = self.encrypt(shuffled_plain_text)

        # Parse the test objects
        assert len(test_objects) > 0
        for test_o in test_objects:
            print('Benchmarking', test_o)
            if test_o.lower() == 'c+c':
                self.add(cipher_text, shuffled_cipher_text, np.array(plain_text) + np.array(shuffled_plain_text))
            elif test_o.lower() == 'c+p':
                self.add(cipher_text, shuffled_plain_text, np.array(plain_text) + np.array(shuffled_plain_text))
            elif test_o.lower() == 'c*c':
                self.multiply(cipher_text, shuffled_cipher_text, np.array(plain_text) * np.array(shuffled_plain_text))
            elif test_o.lower() == 'c*p':
                self.multiply(cipher_text, shuffled_plain_text, np.array(plain_text) * np.array(shuffled_plain_text))
            else:
                raise ValueError('Unknown test object', test_o)

        output_order = ['encrypt', 'decrypt', 'c+p', 'c+c', 'c*p', 'c*c']
        if os.path.isfile(self.output_file_name):
            file_exist = True
            header = None
        else:
            file_exist = False
            header = ['#CPU', 'FreqMin', 'FreqMax', 'FreqCurrent', 'Memory', 'IntMax', 'FloatMax'] +\
                     ['HE Method', 'Params'] +\
                     [e + '(t)' for e in output_order] +\
                     [e + '(e)' for e in output_order[2:]] + [e + '(m)' for e in output_order[:1] + output_order[2:]]
        with open(self.output_file_name, 'a') as f:
            if not file_exist:
                f.write(', '.join(header) + '\n')
            f.write(', '.join(
                [str(e) for e in self.get_machine_info()] + [str(int_max), str(float_max)] + list(self.output_infos) +
                ['None' if len(self.run_time[e]) == 0 else str(np.mean(self.run_time[e])) for e in output_order] +
                ['None' if len(self.error[e]) == 0 else str(np.mean(self.error[e])) for e in output_order[2:]] +
                ['None' if len(self.ram[e]) == 0 else str(np.mean(self.ram[e]))
                 for e in output_order[:1] + output_order[2:]]
            ) + '\n')

    @staticmethod
    def evaluate_from_file(file_name):
        with open(file_name, 'r') as f:
            records = []
            for e in f.readlines():
                if len(e) > 0:
                    records.append(e)
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

        # Perform the t-test
        significance_results = [
            # Number Size vs. Time
            t_test('IntMax', 'encrypt(t)'), t_test('IntMax', 'decrypt(t)'),
            t_test('IntMax', 'c+p(t)')
        ]


