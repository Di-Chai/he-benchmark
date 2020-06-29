import sys
import copy
import time
import random
import argparse
import numpy as np

from seal import *


class CKKSCiphertext(Ciphertext):

    def __init__(self, public_key):
        self.public_key = public_key
        super(CKKSCiphertext, self).__init__()

    def __mul__(self, x):
        result = CKKSCiphertext(self.public_key)
        if isinstance(x, CKKSCiphertext):
            self.public_key.evaluator.multiply(self, x, result)
            self.public_key.evaluator.relinearize_inplace(result, self.public_key.relin_keys)
        else:
            if not isinstance(x, Plaintext):
                x = self.public_key.encode(x)
            self.public_key.evaluator.multiply_plain(self, x, result)
        self.public_key.evaluator.rescale_to_next_inplace(result)
        return result

    def __add__(self, x):
        result = CKKSCiphertext(self.public_key)
        if isinstance(x, CKKSCiphertext):
            self.public_key.evaluator.add(self, x, result)
        else:
            if not isinstance(x, Plaintext):
                x = self.public_key.encode(x)
            self.public_key.evaluator.add_plain(self, x, result)
        return result

    def __sub__(self, x):
        # x should be ciphertext or raw data
        return self + (-1 * x)

    # TODO
    # def __truediv__(self, x):
    #     pass


class CKKSPublicKey:
    def __init__(self, context, public_key, relin_keys, scale):
        self.context = context
        self.encryptor = Encryptor(context, public_key)
        self.evaluator = Evaluator(context)
        self.encoder = CKKSEncoder(context)
        self.slot_count = self.encoder.slot_count()
        self.scale = scale
        self.relin_keys = relin_keys

    def encrypt(self, raw):
        encoded_plaintext = self.encode(raw)
        encrypted_ciphertext = CKKSCiphertext(self)
        self.encryptor.encrypt(encoded_plaintext, encrypted_ciphertext)
        return encrypted_ciphertext

    def encode(self, raw):
        if hasattr(raw, '__len__') and len(raw) > self.slot_count:
            raise ValueError('Expected sizeof(input)<=', self.slot_count, 'Given', len(raw))
        raw_double_vector = DoubleVector(raw)
        encoded_plaintext = Plaintext()
        self.encoder.encode(raw_double_vector, self.scale, encoded_plaintext)
        return encoded_plaintext

    def decode(self, plaintext):
        result = DoubleVector()
        self.encoder.decode(plaintext, result)
        return np.array(result)


class CKKSSecretKey:
    def __init__(self, context, secret_key):
        self.context = context
        self.encoder = CKKSEncoder(self.context)
        self.decryptor = Decryptor(context, secret_key)

    def decrypt(self, ciphertext):
        encoded_plaintext = Plaintext()
        self.decryptor.decrypt(ciphertext, encoded_plaintext)
        result = DoubleVector()
        self.encoder.decode(encoded_plaintext, result)
        return np.array(result)


def generate_pk_and_sk(poly_modulus_degree, scale=None, coefficient_modulus=None):

    if scale is None or coefficient_modulus is None:
        if poly_modulus_degree == 4096:
            scale = 2**26
            coefficient_modulus = [30, 24, 24, 30]
        elif poly_modulus_degree == 8192:
            scale = 2**40
            coefficient_modulus = [60, 40, 40, 60]
        elif poly_modulus_degree == 16384:
            scale = 2**40
            coefficient_modulus = [60, 40, 40, 60]
        else:
            raise ValueError('Please provide scale and coefficient_modulus')

    parms = EncryptionParameters(scheme_type.CKKS)
    parms.set_poly_modulus_degree(poly_modulus_degree)
    parms.set_coeff_modulus(CoeffModulus.Create(poly_modulus_degree, coefficient_modulus))
    context = SEALContext.Create(parms)
    keygen = KeyGenerator(context)

    public_key = keygen.public_key()
    secret_key = keygen.secret_key()
    relin_keys = keygen.relin_keys()

    return CKKSPublicKey(context, public_key, relin_keys, scale), CKKSSecretKey(context, secret_key)