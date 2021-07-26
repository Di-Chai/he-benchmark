import nufhe
import time
import random



class EncryptedList:

    def __init__(self, value, vm):
        self.value = value
        self.size = self.value[0].shape[0]  # how many int
        self.vm = vm

    def __add__(self, other):
        return fhe_add(self.value, other.value, len(self), self.vm, self.size)

    def __sub__(self, other):
        return fhe_sub(self.value, other.value, len(self), self.vm, self.size)

    def __mul__(self, other):
        return fhe_multiplication(self.value, other.value, len(self), self.vm, self.size)

    def __len__(self):
        return len(self.value)

    def __getitem__(self, item):
        pass


class PrivateKey:

    def __init__(self, abt):
        self.sk = abt.get_secret_key()
        self.ctx = abt.get_Context()
        self.ck = abt.get_cloud_key()
        self.vm = abt.get_virtual_machine()
        self.encryptedFalse = self.ctx.encrypt(self.sk, [False])

    def encrypt_bits(self, a: int):
        a_bin_temp = to32bitstr(a)
        size = len(a_bin_temp)
        a_bin = []
        for i in range(size):
            a_bin.append(self.ctx.encrypt(self.sk, a_bin_temp[i]))
        return a_bin

    def encrypted_list(self, a: []):
        result = []
        encrypted_result = []
        for i in range(32):
            result.append([])
        for i in range(len(a)):
            a_bin_temp = to32bitstr(a[i])
            for j in range(len(a_bin_temp)):
                result[j].append(a_bin_temp[j][0])
        for i in range(len(result)):
            encrypted_result.append(self.ctx.encrypt(self.sk, result[i]))
        return EncryptedList(encrypted_result, self.vm)

    def decrypt_list(self, result):
        size = result.size
        len_result = len(result)
        result2 = []
        result3 = []
        latest_result = []
        for i in range(len_result):
            result2.append(self.ctx.decrypt(self.sk, result.value[i]))

        for i in range(size):
            result3.append([])
            for j in range(len_result):
                result3[i].append(result2[j][i])

        for j in range(size):
            result4 = ""
            for i in range(len_result):
                if result3[j][len_result - i - 1]:
                    if i == 0:
                        result4 += '-'
                    else:
                        result4 += '1'
                else:
                    result4 += '0'
            latest_result.append(bitstr_to_int(result4))
        return latest_result


class Arbiter:

    def __init__(self, transform_type='FFT'):
        ctx = nufhe.Context()
        self._secret_key, self._cloud_key = ctx.make_key_pair(transform_type=transform_type)
        self._virtual_machine = ctx.make_virtual_machine(self._cloud_key)
        self._ctx = ctx

    def get_secret_key(self):
        return self._secret_key

    def get_cloud_key(self):
        return self._cloud_key

    def get_virtual_machine(self):
        return self._virtual_machine

    def get_Context(self):
        return self._ctx


def dec2bin(num):
    l = []
    if num < 0:
        return '-' + dec2bin(abs(num))
    while True:
        num, remainder = divmod(num, 2)
        l.append(str(remainder))
        if num == 0:
            return ''.join(l[::-1])


def to32bitstr(num):
    str1 = dec2bin(num)
    len_bin = len(str1)
    binnum = []
    if str1[0] != '-':

        for i in range(len_bin):
            binnum.append([])
            if str1[len_bin - i - 1] == '0':
                binnum[i].append(False)
            else:
                binnum[i].append(True)

        while len(binnum) < 32:
            binnum.append([False])

    else:
        for i in range(len_bin):
            binnum.append([])
            if str1[len_bin - i - 1] == '1':
                binnum[i].append(False)
            else:
                binnum[i].append(True)

        while len(binnum) < 32:
            binnum.append([True])

        temp = True
        for i in range(len(binnum) - 1):
            if binnum[i][0] == True & temp == True:
                binnum[i][0] = False
            else:
                binnum[i][0] = (binnum[i][0] | temp)
                break
        binnum[-1][0] = True
    return binnum


def bitstr_to_int(bit):
    if bit[0] != '-':
        return int(bit, 2)

    else:
        len_bit = len(bit)
        list_bit = list(bit)
        for i in range(len_bit):
            if bit[i] == '1':
                list_bit[i] = '0'
            elif bit[i] == '0':
                list_bit[i] = '1'
        temp = '1'
        for i in range(len_bit):
            if (list_bit[len_bit - 1 - i] == '1') & (temp == '1'):
                list_bit[len_bit - 1 - i] = '0'
            else:
                list_bit[len_bit - 1 - i] = '1'
                break
        bit1 = ''.join(list_bit)
        return int(bit1, 2)


def full_adder(A, B, C_in, vm):
    S1 = vm.gate_xor(A, B)
    Sum = vm.gate_xor(S1, C_in)
    T3 = vm.gate_and(A, B)
    co2 = vm.gate_and(S1, C_in)
    C_out = vm.gate_or(T3, co2)
    return Sum, C_out


def full_subtractor(xi, yi, bi, vm):
    T1 = vm.gate_xor(xi, yi)
    di = vm.gate_xor(T1, bi)
    T2 = vm.gate_and(vm.gate_not(xi), bi)
    T3 = vm.gate_and(vm.gate_not(xi), yi)
    T4 = vm.gate_and(yi, bi)
    bj = vm.gate_or(T4, vm.gate_or(T3, T2))
    return di, bj


def fhe_add(a_bin, b_bin, size, vm, int_num):
    result = []
    t = []
    for i in range(int_num):
        t.append(False)
    C_in = vm.gate_constant(t)
    for i in range(size):
        ciphertext1 = a_bin[i]
        ciphertext2 = b_bin[i]
        Sum, C_in = full_adder(ciphertext1, ciphertext2, C_in, vm)
        result.append(Sum)

    Encrypted_result = EncryptedList(result, vm)
    return Encrypted_result


def fhe_sub(a_bin, b_bin, size, vm, int_num):
    result = []
    t = []
    for i in range(int_num):
        t.append(False)
    C_in = vm.gate_constant(t)
    for i in range(size):
        ciphertext1 = a_bin[i]
        ciphertext2 = b_bin[i]
        Sum, C_in = full_subtractor(ciphertext1, ciphertext2, C_in, vm)
        result.append(Sum)

    Encrypted_result = EncryptedList(result, vm)
    return Encrypted_result


def fhe_add2(a_bin, b_bin, size, vm, int_num):
    result = []
    t = []
    for i in range(int_num):
        t.append(False)
    C_in = vm.gate_constant(t)
    for i in range(size):
        ciphertext1 = a_bin[i]
        ciphertext2 = b_bin[i]
        Sum, C_in = full_adder(ciphertext1, ciphertext2, C_in, vm)
        result.append(Sum)
    return result


def fhe_multiplication(a_bin, b_bin, size, vm, int_num):
    t = []
    for i in range(int_num):
        t.append(False)
    T = vm.gate_constant(t)
    temp_result = []
    for i in range(size):
        temp_result.append([])
        for j in range(size):
            temp_result[i].append(T)
    result = []
    for i in range(size):
        result.append(T)
    for i in range(size - 1):
        for j in range(size - 1):
            if j + i < size - 1:
                temp_result[i][(j + i)] = (vm.gate_and(a_bin[j], b_bin[i]))
            else:
                temp_result[i][(j + i) % (size - 1)] = T
        result = fhe_add2(result, temp_result[i], size, vm, int_num)

    result[size - 1] = vm.gate_xor(a_bin[size - 1], b_bin[size - 1])
    Encrypted_result = EncryptedList(result, vm)
    return Encrypted_result


"""
sk = generate_sk_and_pk()

a = [1, 2, 3]
b = [4, 5, 6]

enc_a = sk.encrypt(a)
enc_b = sk.encrypt(b)

enc_a_b_add = enc_a + enc_b
enc_a_b_mul = enc_a * enc_b

a_b_add = sk.decrypt(enc_a_b_add)
"""


def generate_sk():
    abt = Arbiter()
    sk = PrivateKey(abt)
    return sk
