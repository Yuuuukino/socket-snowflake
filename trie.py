import os
import pathlib
import snowflake

# worker = snowflake.creare_worker()
# snowid = worker.get_id()
block_len = 8
blocks = int(64 / block_len)

def insert(snowid)->str:
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

    for i in range(blocks): # insert to file trie
        st, ed = i * block_len, (i + 1) * block_len
        now = snowid[st: ed]
        # print("block =", now)
        now = hex(int(now, 2))
        path += f"/{now}"
        if not os.path.exists(path):
            os.makedirs(path)
    return path

# print("snowid =", snowid)
# print("insert_path =", insert(snowid))

# file_path = pathlib.Path.cwd()
# print(os.path.basename(file_path))
