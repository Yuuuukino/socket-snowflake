import os
import pathlib
import snowflake

# 对于子文件夹进行新建和查找子函数
def add_path(path, now):
    now = str(int(now, 2))
    path += f"/{now}"
    if not os.path.exists(path):
        os.makedirs(path)
    return path

# 将雪花ID当做字符串, 文件数当做Trie树进行插入
# 生成的ID64位进行分块, 加速文件查找
def cut_into_blocks(path, snowid):
    now = snowid[: 10]  # 第一层, 每49.7d新建一个文件夹
    path = add_path(path, now)
    now = snowid[10: 18]  # 第二层, 每4.66h新建一个文件夹
    path = add_path(path, now)
    now = snowid[18: 26]  # 第三层, 每65.53s新建一个文件夹
    path = add_path(path, now)
    now = snowid[26: 34]  # 第四层, 每256ms新建一个文件夹
    path = add_path(path, now)
    now = snowid[34: 42]  # 第五层, 每1ms一个
    path = add_path(path, now)
    now = snowid[42: 52]  # 机器编号
    path = add_path(path, now)
    now = snowid[52: 64]  # ms级并发编号
    path = add_path(path, now)
    # print("path =", path)
    return path


# block_len = 8
# blocks = int(64 / block_len)
def insert(snowid) -> str:
    if not os.path.exists('./tmp'):
        os.makedirs('./tmp')
    path = './trie'
    if not os.path.exists(path):
        os.makedirs(path)
    snowid = str(bin(snowid))[2:]
    # insert Out of scope
    if len(snowid) > 64: return "Lenth Error"
    # insert short less than 64
    if len(snowid) < 64: snowid = snowid.zfill(64)

    # for i in range(blocks): # insert to file trie
    #     st, ed = i * block_len, (i + 1) * block_len
    #     now = snowid[st: ed]
    #     # print("block =", now)
    #     now = hex(int(now, 2))
    #     path += f"/{now}"
    #     if not os.path.exists(path):
    #         os.makedirs(path)
    path = cut_into_blocks(path, snowid)
    return path

# file_path = pathlib.Path.cwd()
# print(os.path.basename(file_path))

# worker = snowflake.create_worker()
# snowid = worker.get_id()
# print("snowid =", snowid, bin(snowid))
# print("insert_path =", insert(snowid))
