import os

sudo = ''
docker = False

current_path = os.path.dirname(os.path.abspath(__file__))
print(current_path)

if docker:
    head = 'docker run -it --rm -v {}:/he -w /he/ he:benchmark '.format(current_path)
else:
    head = ''

int_max = [100, 1000, 10000, 100000, 1000000]

# CKKS
for i_m in int_max:
    for _ in range(10):
        for p in [4096, 8192, 16384]:
            os.system(sudo + head + 'python seal_ckks.py -p {} -s {} -i {}'.format(p, 100, i_m))

# Paillier
for i_m in int_max:
    for key_size in [1024, 2048, 4096, 8192]:
        for precision in [1e-5, 1e-10, 1e-15]:
            os.system(sudo + head + 'python paillier.py -k {} -p {} -i {}'.format(key_size, precision, i_m))
