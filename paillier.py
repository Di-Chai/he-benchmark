import time
import copy
import argparse
import random
import numpy as np

from phe import paillier

args_parser = argparse.ArgumentParser()
args_parser.add_argument('--key', type=int, default=1024)
args_parser.add_argument('--sample_size', type=int, default=1000)
args_parser.add_argument('--precision', type=float, default=1e-5)
args = args_parser.parse_args()


def encrypt(value_list):
    start = time.time()
    results = [public_key.encrypt(e, precision=args.precision) for e in value_list]
    print('Encrypt(Time)', (time.time() - start) / len(results) * 1000, 'ms')
    return results


def decrypt(value_list):
    start = time.time()
    results = [private_key.decrypt(e) for e in value_list]
    print('Decrypt(Time)', (time.time() - start) / len(results) * 1000, 'ms')
    return results


def c_add_c(c1, c2):
    start = time.time()
    results = [c1[i] + c2[i] for i in range(len(c1))]
    print('C+C(Time)', (time.time() - start) / len(results) * 1000, 'ms')
    return results


def c_add_p(c, p):
    start = time.time()
    results = [c[i] + p[i] for i in range(len(c))]
    print('C+P(Time)', (time.time() - start) / len(results) * 1000, 'ms')
    return results


def c_times_p(c, p):
    start = time.time()
    results = [c[i] * p[i] for i in range(len(c))]
    print('C*P(Time)', (time.time() - start) / len(results) * 1000, 'ms')
    return results


public_key, private_key = paillier.generate_paillier_keypair(n_length=args.key)

####################################################################################################
sample_size = args.sample_size

shuffled_plain_text = np.random.randint(low=1, high=10000, size=sample_size).tolist() +\
                      np.random.randint(low=-10000, high=-1, size=sample_size).tolist() +\
                      np.random.random([sample_size]).tolist() +\
                      (-1 * np.random.random([sample_size])).tolist()

plain_text = copy.deepcopy(shuffled_plain_text)
random.shuffle(shuffled_plain_text)

# Encryption
cipher_text = encrypt(plain_text)
shuffled_cipher_text = encrypt(shuffled_plain_text)

# Calculate
c_a_c = c_add_c(cipher_text, shuffled_cipher_text)
c_a_p = c_add_p(cipher_text, shuffled_plain_text)
c_t_p = c_times_p(cipher_text, shuffled_plain_text)

# Decrypt
c_a_c_p = np.array(decrypt(c_a_c))
c_a_p_p = np.array(decrypt(c_a_p))
c_t_p_p = np.array(decrypt(c_t_p))

# Compare the error with plaintext calculation
c_a_c_error = np.mean(np.abs(np.array(plain_text) + np.array(shuffled_plain_text) - c_a_c_p) /
                      np.abs(np.array(plain_text) + np.array(shuffled_plain_text)))
c_a_p_error = np.mean(np.abs(np.array(plain_text) + np.array(shuffled_plain_text) - c_a_p_p) /
                      np.abs(np.array(plain_text) + np.array(shuffled_plain_text)))
c_t_p_error = np.mean(np.abs(np.array(plain_text) * np.array(shuffled_plain_text) - c_t_p_p) /
                      np.abs(np.array(plain_text) * np.array(shuffled_plain_text)))

print('C+C(MAPE)', c_a_c_error)
print('C+P(MAPE)', c_a_p_error)
print('C*P(MAPE)', c_t_p_error)
