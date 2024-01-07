import psutil

# Get cpu statistics
cpu = str(psutil.cpu_percent()) + '%'
cpuavg = psutil.getloadavg()
cpustat = psutil.cpu_stats()
cpucount = psutil.cpu_count()

# Calculate memory information
memory = psutil.virtual_memory()
# Convert Bytes to MB (Bytes -> KB -> MB)
available = round(memory.available/1024.0/1024.0,1)
total = round(memory.total/1024.0/1024.0,1)
mem_info = str(available) + 'MB free / ' + str(total) + 'MB total ( ' + str(memory.percent) + '% )'

# Calculate disk information
disk = psutil.disk_usage('/')
# Convert Bytes to GB (Bytes -> KB -> MB -> GB)
free = round(disk.free/1024.0/1024.0/1024.0,1)
total = round(disk.total/1024.0/1024.0/1024.0,1)
disk_info = str(free) + 'GB free / ' + str(total) + 'GB total ( ' + str(disk.percent) + '% )'

print("CPU Info--> ", cpu, ' / ', cpuavg, ' / ', cpustat, ' / ', cpucount)
print("Memory Info-->", mem_info)
print("Disk Info-->", disk_info)
