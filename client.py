import socket
import tqdm
import os

# 传输数据分隔符
SEPARATOR = '<SEPARATOR>'
# 服务器信息
host = '175.178.114.64'
port = 12121
# 传输缓冲区
BUFFER_SIZE = 4096
# 传输文件
file_name = 'acfun.zip'
# 文件大小
file_size = os.path.getsize(file_name)
# 创建socketl连接
s = socket.socket()
print(f"服务器连接中{host}:{port}")
s.connect((host, port))
print("连接成功")

# 发送文件名字和文件大小,必须进行编码处理--encode
s.send(f"{file_name}{SEPARATOR}{file_size}".encode())
# 文件传输
progress = tqdm.tqdm(range(file_size), f"发送{file_name}", unit="B", unit_divisor=1024)
with open(file_name, 'rb') as f:
    for _ in progress:  # 读取文件
        bytes_read = f.read(BUFFER_SIZE)
        if not bytes_read:
            progress.close()
            break
        s.sendall(bytes_read)  # 确保即使网络忙碌的时候数据仍然可以传输,优先级高
        progress.update((len(bytes_read)))
s.close()
