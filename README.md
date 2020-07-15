## Metrics

| HE<br />Algorithm | Type | C+P  | C+C  | C*P  | C*C  |  BS  | Real | Complex | GPU  | CPU-Multithread |
| :---------------: | :--: | :--: | :--: | :--: | :--: | :--: | :--: | :-----: | :--: | :-------------: |
|  python-paillier  | PHE  |  √   |  √   |  √   |  ×   |  ×   |  ⭕   |    ×    |  ×   |        ×        |
|     SEAL-CKKS     | LHE  |  √   |  √   |  √   |  √   |  ×   |  √   |    √    |  ×   |        ×        |
|     SEAL-BFV      |      |      |      |      |      |      |      |         |      |                 |

## Time Efficiency (ms)

#### Hardware :

Intel(R) Xeon(R) E5-2630 24-core 2.6GHz CPU, 63GB RAM

#### Python-Paillier

| KeySize | Encrypt |   C+P   |   C+C   |   C*P   | Decrypt |
| :-----: | :-----: | :-----: | :-----: | :-----: | :-----: |
|  1024   | 2.92041 | 0.08736 | 0.02332 | 0.13881 | 0.79487 |
|  2048   | 19.6483 | 0.24298 | 0.06207 | 0.42519 | 5.92360 |
|  4096   | 110.109 | 0.68800 | 0.20159 | 1.20092 | 39.0524 |
|  8192   | 627.369 | 2.05440 | 0.71803 | 3.44691 | 220.295 |

#### SEAL-CKKS

| ploy modulus degree | Scale |  coeff modulus   | Encrypt |   C+P   |   C+C   |   C*P   |   C*C    | Decrypt |
| :-----------------: | :---: | :--------------: | :-----: | :-----: | :-----: | :-----: | :------: | :-----: |
|        8192         | 2^40  | [60, 40, 40, 60] | 11.1359 | 0.36586 | 0.53753 | 3.59743 | 10.14369 | 1.70241 |
|  8192 (no rescale)  | 2^40  | [60, 40, 40, 60] |         |         |         | 0.64937 | 7.22217  | 2.52461 |



## Error Statistics

| HE<br />Algorithm | Key  |   C+P   |   C+C   |   C*P   |   C*C   |
| :---------------: | :--: | :-----: | :-----: | :-----: | :-----: |
|  python-paillier  | 1024 | 1.19e-7 | 1.98e-7 | 2.95e-4 |   ---   |
|  python-paillier  | 2048 | 1.19e-7 | 1.96e-7 | 2.95e-4 |   ---   |
|  python-paillier  | 4096 | 1.19e-7 | 1.99e-7 | 2.97e-4 |   ---   |
|  python-paillier  | 8192 | 1.19e-7 | 2.05e-7 | 3.03e-4 |   ---   |
|     SEAL-CKKS     | 8192 | 1.89e-9 | 2.62e-9 | 4.79e-6 | 8.17e-6 |

## Prepare the environments

```bash
cd docekr
sudo docker build . -t he:benchmark
```

## Reproduce the results

```bash
# Paillier
sudo docker run -it --rm -v $(pwd):/he -w /he he:benchmark python paillier.py

# SEAL-CKKS
sudo docker run -it --rm -v $(pwd):/he -w /he he:benchmark python seal_ckks.py
```

## References

Packages:

- python-paillier https://github.com/data61/python-paillier

- SEAL https://github.com/microsoft/SEAL
- SEAL-Python  https://github.com/Huelse/SEAL-Python

Learning materials:

- Explanation of BFV Schema https://blog.n1analytics.com/homomorphic-encryption-illustrated-primer/

  