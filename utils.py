import os

sample_size = 2500

# Paillier
for key in [1024, 2048, 4096, 8192]:
    for precision in [1e-5, 1e-10, 1e-15]:
        os.system('python paillier.py --sample_size {} --precision {} --key {} > {}'.format(
            sample_size, precision, key, 'results/paillier_{}_{}.txt'.format(precision, key)
        ))


sample_size = 250
params = [
    "--poly_modulus_degree 4096 --log_scale 26 --coeff_modulus 30,24,24,30",
    "--poly_modulus_degree 8192 --log_scale 60 --coeff_modulus 60,40,40,60",
    "--poly_modulus_degree 16384 --log_scale 60 --coeff_modulus 60,40,40,60"
]

for p in params:
    os.system('python seal_ckks.py ' + p + ' --sample_size {} > results/cssk{}.txt'.format(
        sample_size, p.replace(' ', '').replace('--', '_').replace(',', '_')
    ))
