import os
import tqdm
import socket
import trie
import threading
import snowflake
from concurrent.futures import ThreadPoolExecutor

# 设置服务器IP,端口
SERVER_HOST = ''
SERVER_PORT = 12121
# 设置缓冲区
BUFFER_SIZE = 4096
# 设置线程池大小
MAX_WORKERS = 2
# 传输数据分隔符
SEPARATOR = '<SEPARATOR>'
# 创建Server
s = socket.socket()
s.bind((SERVER_HOST, SERVER_PORT))
# 设置连接监听数
s.listen(5)
print(f"服务器监听{SERVER_HOST}:{SERVER_PORT}")
# 导入雪花生成器
worker = snowflake.create_worker()
# 信号量
SEM = 2

# 开启线程池
# executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)
# def run_serve(times):
#     return times
# task1 = executor.submit(run_serve, (3))    # 第一个是回调函数，第二个是传给函数的参数
# task2 = executor.submit(run_serve, (2))
# print(task1.done())
# print(task2.cancel())
# print(task1.result())

sem = threading.Semaphore(SEM)
def serve(client_socket, address):
    print("sem: ", sem)
    with sem:
        # 生成雪花路径
        snowid = worker.get_id()
        path = trie.insert(snowid)
        # 接受客户端连接 打印客户端IP
        print(f"客户端{address}连接")
        # 接受客户端信息
        received = client_socket.recv(BUFFER_SIZE).decode()
        file_name, file_size = received.split(SEPARATOR)
        # file_name = os.path.basename(file_name)
        file_path = path + '/' + file_name

        # client_socket.send((SERVER_HOST +  "/ServerPackage" + file_path[1:]).encode())

        file_size = int(file_size)
        #文件接受
        progress = tqdm.tqdm(range(file_size), f"接受{file_name}",
                                unit = "B", unit_divisor=1024, unit_scale=True)

        with open(file_path, 'wb') as f:
            for _ in progress:
                bytes_read = client_socket.recv(BUFFER_SIZE)
                if len(bytes_read) > 0:
                    f.write(bytes_read)
                    progress.update(len(bytes_read))
                else:
                    progress.close()
                    break
        print("sendto", (SERVER_HOST +  "/ServerPackage" + file_path[1:]).encode())
        client_socket.send((SERVER_HOST +  "/ServerPackage" + file_path[1:]).encode())
        client_socket.close()

while 1:
    try:
        client_socket, address = s.accept()
        thr = threading.Thread(target=serve, args=(client_socket, address))
        thr.start()
    except:
        s.close()
        break
