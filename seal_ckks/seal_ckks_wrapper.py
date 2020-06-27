import sys
import copy
import time
import random
import argparse
import numpy as np

from seal import *


class CKKSPlaintext:
    pass


class CKKSCiphertext:
    pass


class CKKSPublicKey:
    pass


class CKKSSecretKey:
    pass


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

    encryptor = Encryptor(context, public_key)
    evaluator = Evaluator(context)
    decryptor = Decryptor(context, secret_key)

    encoder = CKKSEncoder(context)
    slot_count = encoder.slot_count()

    pass


class CKKSKey:

    def __init__(self, poly_modulus_degree, scale, coeff_modulus=None,):

        # Public part
        parms = EncryptionParameters(scheme_type.CKKS)
        parms.set_poly_modulus_degree(poly_modulus_degree)
        parms.set_coeff_modulus(CoeffModulus.Create(poly_modulus_degree, coeff_modulus))

        scale = pow(2.0, scale)
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