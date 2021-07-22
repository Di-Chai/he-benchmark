import nufhe
import time
import random



class Encrypted_list:

    def __init__(self, value, vm):
        self.value = value
        self.size = self.value[0].shape[0] # how many int
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

    def encryptedNum(self, a):
        value = self.encrypt_bits(a)
        vm = self.vm
        return EncryptedNumber(value, vm)


    def encrypt_bits(self, a: int):
        a_bin_temp = to32bitstr(a)
        size = len(a_bin_temp)
        a_bin = []
        for i in range(size):
            a_bin.append(self.ctx.encrypt(self.sk, a_bin_temp[i]))
        return a_bin

    def encrypted_list(self, a: []):
        result = []
        encryptedresult = []
        for i in range(32):
            result.append([])
        for i in range(len(a)):
            a_bin_temp = to32bitstr(a[i])
            for j in range(len(a_bin_temp)):
                result[j].append(a_bin_temp[j][0])
        for i in range(len(result)):
            encryptedresult.append(self.ctx.encrypt(self.sk, result[i]))
        return Encrypted_list(encryptedresult, self.vm)

    def decrypt_bits(self, result):
        size = len(result.value)
        result2 = []
        result3 = []
        result4 = ""
        for i in range(size):
            result2.append(self.ctx.decrypt(self.sk, result.value[i]))
            result3.append(result2[i][0])
        print(result3)
        for i in range(size):
            if (result3[size - i - 1] == True):
                if i == 0:
                    result4 += '-'
                else:
                    result4 += '1'
            else:
                result4 += '0'
        return bitstr_to_int(result4)

    def decrypt_list(self, result):
        size = result.size
        len_result = len(result)
        result2 = []
        result3 = []
        result4 = ""
        laest_result = []
        print(len_result)
        for i in range(len_result):
            result2.append(self.ctx.decrypt(self.sk, result.value[i]))
        print(result2)

        print(size)
        for i in range(size):
            result3.append([])
            for j in range(len_result):
                result3[i].append(result2[j][i])
        print(result3)
        for j in range(size):
            result4 = ""
            for i in range(len_result):
                if (result3[j][len_result - i - 1] == True):
                    if i == 0:
                        result4 += '-'
                    else:
                        result4 += '1'
                else:
                    result4 += '0'
            laest_result.append(bitstr_to_int(result4))
        return laest_result


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
    if (str1[0] != '-'):

        for i in range(len_bin):
            binnum.append([])
            if (str1[len_bin - i - 1] == '0'):
                binnum[i].append(False)
            else:
                binnum[i].append(True)

        while len(binnum) < 32:
            binnum.append([False])

    else:
        for i in range(len_bin):
            binnum.append([])
            if (str1[len_bin - i - 1] == '1'):
                binnum[i].append(False)
            else:
                binnum[i].append(True)

        while len(binnum) < 32:
            binnum.append([True])

        temp = True
        for i in range(len(binnum) - 1):
            if (binnum[i][0] == True & temp == True):
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

    Encrypted_result = Encrypted_list(result, vm)
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

    Encrypted_result = Encrypted_list(result, vm)
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
    for i in range(size-1):
        for j in range(size-1):
            if(j+i < size-1):
                temp_result[i][(j+i)] = (vm.gate_and(a_bin[j], b_bin[i]))
            else:
                temp_result[i][(j + i) % (size-1)] = T
        result = fhe_add2(result, temp_result[i], size, vm, int_num)

    result[size-1] = vm.gate_xor(a_bin[size-1], b_bin[size-1])
    Encrypted_result = Encrypted_list(result, vm)
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


def main():
    sk = generate_sk()
    control_number = 1000
    list1 = []
    list2 = []
#    list1 = [-1,2,3,4,-5]
#    list2 = [10,-9,8,7,-6]
    for i in range(control_number):
        list1.append(random.randint(-99999, 99999))
        list2.append(random.randint(-99999, 99999))
    enc_start = time.time()
    l1 = sk.encrypted_list(list1)
    enc_time = time.time() - enc_start
    l2 = sk.encrypted_list(list2)

    add_start = time.time()
    list_add = l1 + l2
    add_time = time.time() - add_start
    print("add time:", add_time/control_number)

    sub_start = time.time()
    list_sub = l1 - l2
    sub_time = time.time() - sub_start
    print("sub time:", sub_time/control_number)

    mul_start = time.time()
    list_mul = l1 * l2
    mul_time = time.time() - mul_start
    print("mul time:", mul_time/control_number)

    dec_start = time.time()
    dec_add = sk.decrypt_list(list_add)
    dec_time = time.time() - dec_start
    dec_sub = sk.decrypt_list(list_sub)
    dec_mul = sk.decrypt_list(list_mul)

    result_add = []
    result_sub = []
    result_mul = []
    for i in range(control_number):
        result_add[i] = list1[i] + list2[i]
        result_sub[i] = list1[i] - list2[i]
        result_mul[i] = list1[i] * list2[i]

    assert all(dec_add == result_add)
    assert all(dec_sub == result_sub)
    assert all(dec_mul == result_mul)
    
    print("encrypt time:",enc_time)
    print("decrypt time", dec_time)


if __name__ == '__main__':
    main()

