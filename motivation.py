import os
import time
import argparse
import numpy as np

from functools import reduce
from HEWrapper.seal_ckks import generate_pk_and_sk

args_parser = argparse.ArgumentParser()
args_parser.add_argument('--poly_modulus_degree', '-p', type=int, default=8192)
args_parser.add_argument('--plus_c', '-c', type=str, default='false')

args = args_parser.parse_args()

poly_modulus_degree = args.poly_modulus_degree
plus_c = True if args.plus_c.lower() == 'true' else False
repeat_times = 10

public_key, private_key = generate_pk_and_sk(poly_modulus_degree=poly_modulus_degree, lazy_rescale=True)


def matmul(mat1, mat2):
    h1, w1 = len(mat1), len(mat1[0])
    h2, w2 = len(mat2), len(mat2[0])
    results = []
    for i in range(h1):
        tmp_result = []
        for j in range(w2):
            tmp = []
            for k in range(w1):
                tmp.append(mat1[i][k] * mat2[k][j])
            tmp_result.append(reduce(lambda x, y: x+y, tmp))
        results.append(tmp_result)
    return results


def matadd(mat1, mat2):
    h1, w1 = len(mat1), len(mat1[0])
    result = []
    for i in range(h1):
        tmp = []
        for j in range(w1):
            tmp.append(mat1[i][j] + mat2[i][j])
        result.append(tmp)
    return result


file_name = 'results/motivation_%s_%s.csv' % ('a_b_c' if plus_c else 'a_b', poly_modulus_degree)

for r in range(1):
    for num_dims in [1, 10, 20, 40, 60, 80, 100, 150, 200]:

        print('######## Dim %s ########' % num_dims)

        a = np.random.random([repeat_times, num_dims, public_key.slot_count])
        b = np.random.random([num_dims, repeat_times, public_key.slot_count])
        c = np.random.random([repeat_times, repeat_times, public_key.slot_count])

        start = time.time()
        if plus_c:
            result_ptp = matmul(a, b) + c
        else:
            result_ptp = matmul(a, b)
        ptp_compute_time = time.time() - start
        print('Time P*P', ptp_compute_time)

        a_cipher = [[public_key.encrypt(a[i, j, :]) for j in range(num_dims)] for i in range(repeat_times)]
        b_plaintext = [[public_key.encode(b[i, j, :]) for j in range(repeat_times)] for i in range(num_dims)]
        b_cipher = [[public_key.encrypt(b[i, j, :]) for j in range(repeat_times)] for i in range(num_dims)]
        c_cipher = [[public_key.encrypt(c[i, j, :]) for j in range(repeat_times)] for i in range(repeat_times)]

        start = time.time()
        if plus_c:
            result_ctp = matadd(matmul(a_cipher, b_plaintext), c_cipher)
        else:
            result_ctp = matmul(a_cipher, b_plaintext)
            for i in range(repeat_times):
                for j in range(repeat_times):
                    result_ctp[i][j].rescale()
        ctp_compute_time = time.time() - start
        print('Time C*P', ctp_compute_time)

        start = time.time()
        if plus_c:
            result_ctc = matadd(matmul(a_cipher, b_cipher), c_cipher)
        else:
            result_ctc = matmul(a_cipher, b_cipher)
            for i in range(repeat_times):
                for j in range(repeat_times):
                    result_ctc[i][j].rescale()
        ctc_compute_time = time.time() - start
        print('Time C*C', ctc_compute_time)

        print('Diff', ctc_compute_time / ctp_compute_time)

        result_ptp = np.array(result_ptp)

        start = time.time()
        result_ctp_dec = np.array([[private_key.decrypt(result_ctp[i][j])
                                    for j in range(repeat_times)] for i in range(repeat_times)])
        ctp_decrypt_time = time.time() - start
        print('Time Decrypt C*P', ctp_decrypt_time)

        start = time.time()
        result_ctc_dec = np.array([[private_key.decrypt(result_ctc[i][j])
                                    for j in range(repeat_times)] for i in range(repeat_times)])
        ctc_decrypt_time = time.time() - start
        print('Time Decrypt C*C', ctc_decrypt_time)

        ctp_error = np.abs(result_ctp_dec - result_ptp).mean()
        ctc_error = np.abs(result_ctc_dec - result_ptp).mean()
        print('Error C*P', ctp_error)
        print('Error C*C', ctc_error)

        if not os.path.isfile(file_name):
            with open(file_name, 'w') as f:
                f.write(', '.join([
                    'dims', 'pp(t)', 'cp(t)', 'cc(t)', 'cp_de(t)', 'cc_de(t)', 'cp(e)', 'cc(e)'
                ]) + '\n')

        with open(file_name, 'a+') as f:
            f.write(', '.join([str(e) for e in [
                num_dims, ptp_compute_time, ctp_compute_time, ctc_compute_time, ctp_decrypt_time, ctc_decrypt_time,
                ctp_error, ctc_error
            ]]) + '\n')
