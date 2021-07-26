import argparse
import time
import random
from HEBenchMark import HEBenchMark.seal_nufhe

sk = generate_sk()
control_list = [1, 10, 100, 1000]
list1 = []
list2 = []
for control_number in control_list:
    for i in range(control_number):
        list1.append(random.randint(-9999, 9999))
        list2.append(random.randint(-9999, 9999))
    enc_start = time.time()
    l1 = sk.encrypted_list(list1)
    enc_time = time.time() - enc_start
    l2 = sk.encrypted_list(list2)

    print(control_number, "integer:")

    add_start = time.time()
    list_add = l1 + l2
    add_time = time.time() - add_start
    print("add time:", add_time / control_number)

    sub_start = time.time()
    list_sub = l1 - l2
    sub_time = time.time() - sub_start
    print("sub time:", sub_time / control_number)

    mul_start = time.time()
    list_mul = l1 * l2
    mul_time = time.time() - mul_start
    print("mul time:", mul_time / control_number)

    dec_start = time.time()
    dec_add = sk.decrypt_list(list_add)
    dec_time = time.time() - dec_start
    dec_sub = sk.decrypt_list(list_sub)
    dec_mul = sk.decrypt_list(list_mul)

    result_add = []
    result_sub = []
    result_mul = []
    for i in range(control_number):
        result_add.append(list1[i] + list2[i])
        result_sub.append(list1[i] - list2[i])
        result_mul.append(list1[i] * list2[i])

    assert (dec_add == result_add)
    assert (dec_sub == result_sub)
    assert (dec_mul == result_mul)

    print("encrypt time:", enc_time)
    print("decrypt time:", dec_time, '\n')