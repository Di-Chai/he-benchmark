import psutil

print("# logical CPU cores", psutil.cpu_count(logical=True))

print("CPU Frequency %.2f GHz" % (psutil.cpu_freq().current / 1000))

print("Memory Size: %.0f GB" % (psutil.virtual_memory().total / 2**30))
