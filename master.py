import os


current_path = os.path.dirname(os.path.abspath(__file__))
print(current_path)

int_max = [100, 1000, 10000, 100000, 1000000]

repeat_times = 10

# CKKS
# for i_m in int_max:
#     for _ in range(repeat_times):
#         for p in [4096, 8192, 16384]:
#             os.system('python seal_ckks.py -p {} -s {} -i {}'.format(p, 100, i_m))

# Paillier
for i_m in int_max:
    for key_size in [1024, 2048, 4096, 8192]:
        for precision in [1e-5, 1e-10, 1e-15]:
            # sample size = 10 to make it faster
            os.system('python paillier.py -k {} -p {} -s {} -i {}'.format(key_size, precision, 1000, i_m))
