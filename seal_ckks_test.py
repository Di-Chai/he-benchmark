import numpy as np
import argparse

from HEBenchMark import HEBenchMark
from HEWrapper.seal_ckks import generate_pk_and_sk

args_parser = argparse.ArgumentParser()
args_parser.add_argument('--poly_modulus_degree', '-p', type=int, default=16384)
args_parser.add_argument('--sample_size', '-s', type=int, default=100)
args_parser.add_argument('--int_max', '-i', type=int, default=10000)
args_parser.add_argument('--float_max', '-f', type=float, default=1.0)

args = args_parser.parse_args()

poly_modulus_degree = args.poly_modulus_degree
sample_size = args.sample_size

public_key, private_key = generate_pk_and_sk(
    poly_modulus_degree=8192,
    # poly_modulus_degree=poly_modulus_degree,
    # scale=2**24, coefficient_modulus=[30, 24, 24, 30],
    # scale=2**60, coefficient_modulus=[60, 50, 50, 50, 50, 60],
    # scale=2**50, coefficient_modulus=[60, 40, 40, 40, 40, 40, 40, 40, 60],
    lazy_rescale=True
)

x = public_key.encrypt([1, 2, 3, 4, 5])

y = np.pi

x_y = x * y

x_2 = x * x

x_4 = x_2 * x_y

result = private_key.decrypt(x_4)[:5]

print(result)

print(np.abs(result - np.pi * np.array([1**3, 2**3, 3**3, 4**3, 5**3])).mean())
