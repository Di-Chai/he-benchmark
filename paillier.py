import argparse

from phe import paillier
from HEBenchMark import HEBenchMark

args_parser = argparse.ArgumentParser()
args_parser.add_argument('--key_size', '-k', type=int, default=1024)
args_parser.add_argument('--precision', '-p', type=float, default=1e-5)
args_parser.add_argument('--int_max', '-i', type=int, default=10000)
args_parser.add_argument('--float_max', '-f', type=float, default=1.0)
args_parser.add_argument('--sample_size', '-s', type=int, default=100)

args = args_parser.parse_args()

key_size = args.key_size
precision = args.precision

print(key_size, precision)
public_key, private_key = paillier.generate_paillier_keypair(n_length=key_size)
he_benchmark = HEBenchMark(pub_key=public_key, sec_key=private_key, encrypt_params={'precision': precision},
                           output_file_name='results/paillier.csv',
                           output_infos=('paillier', '%s-%s' % (key_size, precision)))

he_benchmark.run(test_objects=['c+c', 'c+p', 'c*p'], SIMD=False, sample_size=args.sample_size,
                 int_max=args.int_max, float_max=args.float_max)
