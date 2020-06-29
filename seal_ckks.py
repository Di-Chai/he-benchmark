import sys
import copy
import time
import random
import argparse
import numpy as np

from seal import *


"""
--poly_modulus_degree 4096 --log_scale 26 --coeff_modulus 30,24,24,30
--poly_modulus_degree 8192 --log_scale 60 --coeff_modulus 60,40,40,60
--poly_modulus_degree 16384 --log_scale 60 --coeff_modulus 60,40,40,60
"""

args_parser = argparse.ArgumentParser()
args_parser.add_argument('--poly_modulus_degree', type=int, default=8192)
args_parser.add_argument('--log_scale', type=int, default=40)
args_parser.add_argument('--coeff_modulus', type=str, default='60,40,40,60')
args_parser.add_argument('--sample_size', type=int, default=10)
args_parser.add_argument('--dtype', type=str, default='ni')
args = args_parser.parse_args()

####################################################################################################
# Encrypt parameters

parms = EncryptionParameters(scheme_type.CKKS)

poly_modulus_degree = args.poly_modulus_degree
parms.set_poly_modulus_degree(poly_modulus_degree)
parms.set_coeff_modulus(CoeffModulus.Create(poly_modulus_degree, [int(e) for e in args.coeff_modulus.split(',')]))

scale = pow(2.0, args.log_scale)
context = SEALContext.Create(parms)

keygen = KeyGenerator(context)
public_key = keygen.public_key()
secret_key = keygen.secret_key()
relin_keys = keygen.relin_keys()

encryptor = Encryptor(context, public_key)
evaluator = Evaluator(context)
decryptor = Decryptor(context, secret_key)

encoder = CKKSEncoder(context)
slot_count = encoder.slot_count()


def encrypt(value_list):
    start = time.time()
    results = []
    for value in value_list:
        vector_value = DoubleVector()
        vector_value.append(value)
        plaintext_value = Plaintext()
        encoder.encode(vector_value, scale, plaintext_value)
        encrypt_value = Ciphertext()
        encryptor.encrypt(plaintext_value, encrypt_value)
        results.append(encrypt_value)
    print('Encrypt(Time)', (time.time() - start) / len(results) * 1000, 'ms')
    return results


def c_add_c(c1, c2):
    start = time.time()
    results = []
    for i in range(len(c1)):
        tmp_result = Ciphertext()
        evaluator.add(c1[i], c2[i], tmp_result)
        results.append(tmp_result)
    print('C+C(Time)', (time.time() - start) / len(results) * 1000, 'ms')
    return results


def c_add_p(c, p):
    start = time.time()
    results = []
    for i in range(len(c)):
        result = Ciphertext()
        tmp_p = Plaintext()
        encoder.encode(p[i], scale, tmp_p)
        evaluator.add_plain(c[i], tmp_p, result)
        results.append(result)
    print('C+P(Time)', (time.time() - start) / len(results) * 1000, 'ms')
    return results


def c_times_c(c1, c2, rescale=True):
    start = time.time()
    results = []
    for i in range(len(c1)):
        tmp_result = Ciphertext()
        evaluator.multiply(c1[i], c2[i], tmp_result)
        evaluator.relinearize_inplace(tmp_result, relin_keys)
        if rescale:
            evaluator.rescale_to_next_inplace(tmp_result)
        results.append(tmp_result)
    print('C*C(Time,Rescale=%s)' % rescale, (time.time() - start) / len(results) * 1000, 'ms')
    return results


def c_times_p(c, p, rescale=True):
    start = time.time()
    results = []
    for i in range(len(c)):
        tmp_result = Ciphertext()
        tmp_p = Plaintext()
        encoder.encode(p[i], scale, tmp_p)
        evaluator.multiply_plain(c[i], tmp_p, tmp_result)
        if rescale:
            evaluator.rescale_to_next_inplace(tmp_result)
        results.append(tmp_result)
    print('C*P(Time,Rescale=%s)' % rescale, (time.time() - start) / len(results) * 1000, 'ms')
    return results


def decrypt(c, verbose=True, name=None):
    start = time.time()
    results = []
    for i in range(len(c)):
        tmp_p = Plaintext()
        decryptor.decrypt(c[i], tmp_p)
        result = DoubleVector()
        encoder.decode(tmp_p, result)
        results.append(result[0])
    if verbose:
        print(name or 'Decrypt(Time)', (time.time() - start) / len(results) * 1000, 'ms')
    return results


####################################################################################################
sample_size = args.sample_size

shuffled_plain_text = np.random.randint(low=1, high=10000, size=sample_size).tolist() +\
                      np.random.randint(low=-10000, high=-1, size=sample_size).tolist() +\
                      np.random.random([sample_size]).tolist() +\
                      (-1 * np.random.random([sample_size])).tolist()

plain_text = copy.deepcopy(shuffled_plain_text)
random.shuffle(shuffled_plain_text)

# Plaintext results
plain_text_add = np.array(plain_text) + np.array(shuffled_plain_text)
plain_text_mul = np.array(plain_text) * np.array(shuffled_plain_text)

# Encryption
cipher_text = encrypt(plain_text)
shuffled_cipher_text = encrypt(shuffled_plain_text)
print('##################################################')

# Calculate
# (1) C+C
c_a_c = c_add_c(cipher_text, shuffled_cipher_text)
c_a_c_p = np.array(decrypt(c_a_c, name='DecryptC+C(Time)'))
print('C+C(MAPE)', np.mean(np.abs(plain_text_add - c_a_c_p) / np.abs(plain_text_add)))
print('##################################################')

# (2) C+P
c_a_p = c_add_p(cipher_text, shuffled_plain_text)
c_a_p_p = np.array(decrypt(c_a_p, name='DecryptC+P(Time)'))
print('C+P(MAPE)', np.mean(np.abs(plain_text_add - c_a_p_p) / np.abs(plain_text_add)))
print('##################################################')

# (3) C*C
for is_rescale in [True, False]:
    c_t_c = c_times_c(cipher_text, shuffled_cipher_text, rescale=is_rescale)
    c_t_c_p = decrypt(c_t_c, name='DecryptC*C(Time,Rescale=%s)' % is_rescale)
    print('C*C(MAPE,Rescale=%s)' % is_rescale,
          np.mean(np.abs(plain_text_mul - np.array(c_t_c_p)) / np.abs(plain_text_mul)))
print('##################################################')

# (4) C*P
for is_rescale in [True, False]:
    c_t_p = c_times_p(cipher_text, shuffled_plain_text, rescale=is_rescale)
    c_t_p_p = decrypt(c_t_p, name='DecryptC*P(Time,Rescale=%s)' % is_rescale)
    print('C*P(MAPE,Rescale=%s)' % is_rescale,
          np.mean(np.abs(plain_text_mul - np.array(c_t_p_p)) / np.abs(plain_text_mul)))
