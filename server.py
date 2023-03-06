import os
import tqdm
import socket

import trie
import snowflake

#设置服务器IP,端口
SERVER_HOST = ''
SERVER_PORT = 12121
#设置缓冲区
BUFFER_SIZE = 4096
# 传输数据分隔符
SEPARATOR = '<SEPARATOR>'
# 创建Server
s = socket.socket()
s.bind((SERVER_HOST, SERVER_PORT))
#设置连接监听数
s.listen(5)
print(f"服务器监听{SERVER_HOST}:{SERVER_PORT}")
# 导入雪花生成器
worker = snowflake.create_worker()

while 1:
    try:
        client_socket, address = s.accept()
        # 生成雪花路径
        snowid = worker.get_id()
        path = trie.insert(snowid)
        # 接受客户端连接 打印客户端IP
        print(f"客户端{address}连接")
        # 接受客户端信息
        received = client_socket.recv(BUFFER_SIZE).decode()
        # print("received: ", received) # bilibili.jpg<SEPARATOR>35834
        file_name, file_size = received.split(SEPARATOR)
        # file_name = os.path.basename(file_name)
        file_path = path + '/' + file_name
        print(file_path)
        file_size = int(file_size)
        #文件接受
        progress = tqdm.tqdm(range(file_size), f"接受{file_name}",
                             unit = "B", unit_divisor=1024, unit_scale=True)

        with open(file_path, 'wb') as f:
            for _ in progress:
                bytes_read = client_socket.recv(BUFFER_SIZE)
                if not bytes_read:
                    progress.close()
                    break
                f.write(bytes_read)
                progress.update(len(bytes_read))
        client_socket.close()
    except:
        s.close()
        break