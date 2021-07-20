import nufhe
import time

"""
ctx = nufhe.Context()
#secret_key, cloud_key = ctx.make_key_pair()
secret_key, cloud_key = ctx.make_key_pair(transform_type='FFT')
vm = ctx.make_virtual_machine(cloud_key)
"""


class EncryptedNumber:

    def __init__(self, sk=None, a=None, value=None, vm=None):
        if value is None:
            self.value = sk.encrypt_bits(a)
            self.size = len(self.value)
            self.vm = sk.vm

        else:
            self.value = value
            self.size = len(self.value)
            self.vm = vm

    def __add__(self, other):
        return fhe_add(self.value, other.value, self.size, self.vm)

    def __sub__(self, other):
        return fhe_sub(self.value, other.value, self.size, self.vm)

    def __mul__(self, other):
        pass

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

    def encryptedNum(self):
        return EncryptedNumber(self.sk, a)


    def encrypt_bits(self, a: int):
        a_bin_temp = to16bitstr(a)
        size = len(a_bin_temp)
        a_bin = []
        for i in range(size):
            a_bin.append(self.ctx.encrypt(self.sk, a_bin_temp[i]))
        return a_bin

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


def to16bitstr(num):
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

        while len(binnum) < 16:
            binnum.append([False])

    else:
        for i in range(len_bin):
            binnum.append([])
            if (str1[len_bin - i - 1] == '1'):
                binnum[i].append(False)
            else:
                binnum[i].append(True)

        while len(binnum) < 16:
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


def fhe_add(a_bin, b_bin, size, vm):
    result = []
    C_in = vm.gate_constant([False])
    for i in range(size):
        ciphertext1 = a_bin[i]
        ciphertext2 = b_bin[i]
        Sum, C_in = full_adder(ciphertext1, ciphertext2, C_in, vm)
        result.append(Sum)

    Encrypted_result = EncryptedNumber(None, None, result, vm)
    return Encrypted_result


def fhe_sub(a_bin, b_bin, size, vm):
    result = []
    C_in = vm.gate_constant([False])
    for i in range(size):
        ciphertext1 = a_bin[i]
        ciphertext2 = b_bin[i]
        Sum, C_in = full_subtractor(ciphertext1, ciphertext2, C_in, vm)
        result.append(Sum)

    Encrypted_result = EncryptedNumber(None, None, result, vm)
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

    a = 10

    a_enc = sk.encrypt_bits(a)

    a = EncryptedNumber(sk, 10)
    b = EncryptedNumber(sk, -20)
    c = EncryptedNumber(sk, 30)

    print(sk.decrypt_bits(a + b + c))


if __name__ == '__main__':
    main()