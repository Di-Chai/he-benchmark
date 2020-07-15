import argparse

from HEBenchMark import HEBenchMark
from HEWrapper.seal_ckks import generate_pk_and_sk

args_parser = argparse.ArgumentParser()
args_parser.add_argument('--poly_modulus_degree', '-p', type=int, default=4096)
args_parser.add_argument('--sample_size', '-s', type=int, default=100)
args_parser.add_argument('--int_max', '-i', type=int, default=10000)
args_parser.add_argument('--float_max', '-f', type=float, default=1.0)

args = args_parser.parse_args()

poly_modulus_degree = args.poly_modulus_degree
sample_size = args.sample_size

public_key, private_key = generate_pk_and_sk(poly_modulus_degree=poly_modulus_degree, lazy_rescale=False)
print(public_key.format_params())
he_benchmark = HEBenchMark(
    pub_key=public_key, sec_key=private_key, encrypt_params=None,
    output_file_name='results/ckks.csv',
    output_infos=('ckks', public_key.format_params().replace(',', '_'))
)
he_benchmark.run(test_objects=['c+p', 'c+c', 'c*p', 'c*c'], SIMD=True, sample_size=sample_size,
                 int_max=args.int_max, float_max=args.float_max)
