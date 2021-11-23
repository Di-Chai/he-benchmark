## Metrics

| HE<br />Algorithm | Type | C+P  | C+C  | C*P  | C*C  |  BS  | Real | Complex | GPU  | CPU-Multithread |
| :---------------: | :--: | :--: | :--: | :--: | :--: | :--: | :--: | :-----: | :--: | :-------------: |
|  python-paillier  | PHE  |  √   |  √   |  √   |  ×   |  ×   |  ⭕   |    ×    |  ×   |        ×        |
|     SEAL-CKKS     | LHE  |  √   |  √   |  √   |  √   |  ×   |  √   |    √    |  ×   |        ×        |
|     SEAL-BFV      |      |      |      |      |      |      |      |         |      |                 |

## Time Efficiency (ms)

#### Hardware :

Intel(R) Xeon(R) E5-2630 24-core 2.6GHz CPU, 63GB RAM

#### Shared Param

1. Scale of the plaintext number, floating numbers: 0\~1, Integer numbers: 0\~100
2. Repeat times : 100 (presented results are averaged values)

| HE Algo  |               Param                | Encrypt  |   C+P    |   C+C    |   C*P    |   C*C    | Decrypt  |
| :------: | :--------------------------------: | :------: | :------: | :------: | :------: | :------: | :------: |
| Paillier |            1024, 1e-15             | 2.952835 | 0.045799 | 0.022273 | 0.127396 |   NULL   |  0.8013  |
| Paillier |            2048, 1e-15             | 19.64399 | 0.102064 | 0.062424 | 0.39062  |   NULL   |  5.7883  |
| Paillier |            4096, 1e-15             | 110.4095 | 0.280304 | 0.203196 | 1.10679  |   NULL   | 39.08318 |
| Paillier |            8192, 1e-15             | 629.7019 | 0.868673 | 0.719323 | 3.15596  |   NULL   | 221.0439 |
|   CKKS   |       4096-24-[30_24_24_30]        | 6.21131  | 1.24118  | 0.13797  | 2.84830  | 5.27865  | 1.16159  |
|   CKKS   |       8192-40-[60_40_40_60]        | 12.51202 | 2.60122  | 0.46410  | 5.79688  | 10.99037 | 2.35254  |
|   CKKS   | 16384-50-[60_50_50_50_50_50_50_60] | 42.88685 | 9.39863  | 1.69185  | 26.73753 | 68.33356 | 13.15035 |

## Error Statistics (MAPE)

| HE Algo  |               Param                |   C+P    |   C+C    |   C*P    |   C*C    |
| :------: | :--------------------------------: | :------: | :------: | :------: | :------: |
| Paillier |            1024, 1E-15             | 1.13E-15 | 1.86E-15 | 3.62E-16 |   NULL   |
| Paillier |            2048, 1E-15             | 7.99E-16 | 9.13E-16 | 2.75E-16 |   NULL   |
| Paillier |            4096, 1E-15             | 8.59E-17 | 1.35E-16 | 2.25E-16 |   NULL   |
| Paillier |            8192, 1E-15             | 7.12E-17 | 2.72E-16 | 3.61E-16 |   NULL   |
|   CKKS   |       4096-24-[30_24_24_30]        | 1.30E-4  | 1.87E-4  |   0.39   |   1.03   |
|   CKKS   |       8192-40-[60_40_40_60]        | 6.81E-09 | 1.53E-08 | 5.70E-07 | 5.55E-07 |
|   CKKS   | 16384-50-[60_50_50_50_50_50_50_60] | 8.64E-12 | 1.20E-11 | 1.16E-09 | 9.69E-10 |

## Ciphertext Size

| HE Algo  |               Param                | Ciphertext Size (MB) |
| :------: | :--------------------------------: | :------------------: |
| Paillier |            1024, 1E-15             |        0.0005        |
| Paillier |            2048, 1E-15             |       0.000769       |
| Paillier |            4096, 1E-15             |       0.00134        |
| Paillier |            8192, 1E-15             |       0.00248        |
|   CKKS   |       4096-24-[30_24_24_30]        |        0.188         |
|   CKKS   |       8192-40-[60_40_40_60]        |        0.376         |
|   CKKS   | 16384-50-[60_50_50_50_50_50_50_60] |        1.753         |

## Reproduce the results

#### Prepare the environments

```bash
cd docekr
sudo docker build . -t he:benchmark
```

If you have slow network connections, the following commend might be faster

```bash
sudo docker build . -t he:benchmark -f Local.Dockerfile
```

#### Single trial

```bash
# Paillier
sudo docker run -it --rm -v $(pwd):/he -w /he he:benchmark python paillier.py

# SEAL-CKKS
sudo docker run -it --rm -v $(pwd):/he -w /he he:benchmark python seal_ckks.py
```

#### Multiple trials using the master file

```bash
# Master File
sudo docker run -it --rm -v $(pwd):/he -w /he he:benchmark python master.py
```

## References

Packages:

- python-paillier https://github.com/data61/python-paillier

- SEAL https://github.com/microsoft/SEAL
- SEAL-Python  https://github.com/Huelse/SEAL-Python

Learning materials:

- Explanation of BFV Schema https://blog.n1analytics.com/homomorphic-encryption-illustrated-primer/
