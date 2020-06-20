import math
import copy
import time
import random
import numpy as np

from seal import *

####################################################################################################
# Encrypt parameters

parms = EncryptionParameters(scheme_type.CKKS)

poly_modulus_degree = 8192
parms.set_poly_modulus_degree(poly_modulus_degree)
parms.set_coeff_modulus(CoeffModulus.Create(poly_modulus_degree, [60, 40, 40, 60]))

scale = pow(2.0, 40)
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
    print('Encrypt', (time.time() - start) / len(results) * 1000, 'ms')
    return results


def c_add_c(c1, c2):
    start = time.time()
    results = []
    for i in range(len(c1)):
        tmp_result = Ciphertext()
        evaluator.add(c1[i], c2[i], tmp_result)
        results.append(tmp_result)
    print('Cipher-Add-Cipher', (time.time() - start) / len(results) * 1000, 'ms')
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
    print('Cipher-Add-Plain', (time.time() - start) / len(results) * 1000, 'ms')
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
    print('Cipher-Times-Cipher Rescale %s' % rescale, (time.time() - start) / len(results) * 1000, 'ms')
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
    print('Cipher-Times-Plain Rescale %s' % rescale, (time.time() - start) / len(results) * 1000, 'ms')
    return results


def decrypt(c):
    start = time.time()
    results = []
    for i in range(len(c)):
        tmp_p = Plaintext()
        decryptor.decrypt(c[i], tmp_p)
        result = DoubleVector()
        encoder.decode(tmp_p, result)
        results.append(result[0])
    print('Decrypt', (time.time() - start) / len(results) * 1000, 'ms')
    return results


####################################################################################################
sample_size = 1000

shuffled_plain_text = np.random.randint(low=0, high=10000, size=sample_size).tolist() + \
                      np.random.randint(low=-10000, high=0, size=sample_size).tolist() + \
                      np.random.random([sample_size]).tolist() + \
                      (-1 * np.random.random([sample_size])).tolist()
plain_text = copy.deepcopy(shuffled_plain_text)
random.shuffle(shuffled_plain_text)

# Encryption
cipher_text = encrypt(plain_text)
shuffled_cipher_text = encrypt(shuffled_plain_text)

# Calculate
c_a_c = c_add_c(cipher_text, shuffled_cipher_text)
c_a_p = c_add_p(cipher_text, shuffled_plain_text)
c_t_c_rescale = c_times_c(cipher_text, shuffled_cipher_text)
c_t_p_rescale = c_times_p(cipher_text, shuffled_plain_text)

c_t_c_no_rescale = c_times_c(cipher_text, shuffled_cipher_text, rescale=False)
c_t_p_no_rescale = c_times_p(cipher_text, shuffled_plain_text, rescale=False)


# Decrypt
c_a_c_p = np.array(decrypt(c_a_c))
c_a_p_p = np.array(decrypt(c_a_p))
c_t_c_rescale_p = np.array(decrypt(c_t_c_rescale))
c_t_p_rescale_p = np.array(decrypt(c_t_p_rescale))
c_t_c_no_rescale_p = np.array(decrypt(c_t_c_no_rescale))
c_t_p_no_rescale_p = np.array(decrypt(c_t_p_no_rescale))

# Compare the error with plaintext calculation
c_a_c_error = np.mean(np.abs((np.array(plain_text) + np.array(shuffled_plain_text)) - c_a_c_p))
c_a_p_error = np.mean(np.abs((np.array(plain_text) + np.array(shuffled_plain_text)) - c_a_p_p))
c_t_c_rescale_error = np.mean(np.abs((np.array(plain_text) * np.array(shuffled_plain_text)) - c_t_c_rescale_p))
c_t_p_rescale_error = np.mean(np.abs((np.array(plain_text) * np.array(shuffled_plain_text)) - c_t_p_rescale_p))
c_t_c_no_rescale_error = np.mean(np.abs((np.array(plain_text) * np.array(shuffled_plain_text)) - c_t_c_no_rescale_p))
c_t_p_no_rescale_error = np.mean(np.abs((np.array(plain_text) * np.array(shuffled_plain_text)) - c_t_p_no_rescale_p))

print('Cipher-Add-Cipher Error', c_a_c_error)
print('Cipher-Add-Plain Error', c_a_p_error)
print('Cipher-Times-Cipher-Rescale', c_t_c_rescale_error)
print('Cipher-Times-Plain-Rescale', c_t_p_rescale_error)
print('Cipher-Times-Cipher-No-Rescale', c_t_c_no_rescale_error)
print('Cipher-Times-Plain-No-Rescale', c_t_p_no_rescale_error)

# 8192
# Encrypt 9.473273968696594 ms
# Encrypt 9.595090448856354 ms
# Cipher-Add-Cipher 0.878357583284378 ms
# Cipher-Add-Plain 0.5987134873867035 ms
# Cipher-Times-Cipher Rescale True 8.761111438274384 ms
# Cipher-Times-Plain Rescale True 3.1809574604034423 ms
# Cipher-Times-Cipher Rescale False 6.478950351476669 ms
# Cipher-Times-Plain Rescale False 0.7880936920642853 ms
# Decrypt 2.160055488348007 ms
# Decrypt 2.0523983418941496 ms
# Decrypt 1.302309012413025 ms
# Decrypt 1.4352693557739258 ms
# Decrypt 2.2591874241828918 ms
# Decrypt 2.1422818720340726 ms
# Cipher-Add-Cipher Error 1.320334987279649e-09
# Cipher-Add-Plain Error 9.396874007781245e-10
# Cipher-Times-Cipher-Rescale 4.1541108643543285e-06
# Cipher-Times-Plain-Rescale 2.3543582779546964e-06
# Cipher-Times-Cipher-No-Rescale 4.153989254943783e-06
# Cipher-Times-Plain-No-Rescale 2.3541159630546997e-06
