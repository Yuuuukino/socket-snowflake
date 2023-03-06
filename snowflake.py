import time
import logging

'''
64-bit = 1 + 41 + 10 + 12
41: timestamp
10: WORKER_ID_BITS + DATACENTER_ID_BITS
12: SEQUENCE_BITS
'''
# 64位ID的划分
WORKER_ID_BITS = 5
DATACENTER_ID_BITS = 5
SEQUENCE_BITS = 12

# 数据中心最大有多少机器
MAX_WORKER_ID = -1 ^ (-1 << WORKER_ID_BITS)  # 2**5-1 0b11111
# 数据中心（机器区域）最大有多少个
MAX_DATACENTER_ID = -1 ^ (-1 << DATACENTER_ID_BITS)

# 移位偏移计算
WOKER_ID_SHIFT = SEQUENCE_BITS
DATACENTER_ID_SHIFT = SEQUENCE_BITS + WORKER_ID_BITS
TIMESTAMP_LEFT_SHIFT = SEQUENCE_BITS + WORKER_ID_BITS + DATACENTER_ID_BITS

# 序号循环掩码
SEQUENCE_MASK = -1 ^ (-1 << SEQUENCE_BITS)

# Twitter元年时间戳, 使用时修改为系统的元年时间戳
TWEPOCH = 1288834974657


# logger = logging.getLogger('flask.app')

class IdWorker(object):
    def __init__(self, datacenter_id, worker_id, sequence=0):
        """
        初始化
        :param datacenter_id: 数据中心（机器区域）ID
        :param worker_id: 机器ID
        :param sequence: 毫秒内序列号
        """
        # sanity check
        if worker_id > MAX_WORKER_ID or worker_id < 0:
            raise ValueError('worker_id值越界')

        if datacenter_id > MAX_DATACENTER_ID or datacenter_id < 0:
            raise ValueError('datacenter_id值越界')

        self.worker_id = worker_id
        self.datacenter_id = datacenter_id
        self.sequence = sequence
        self.cnt = 0
        self.last_timestamp = -1  # 上次计算的时间戳

    def _gen_timestamp(self):
        return int(time.time() * 1000)  # 生成整数时间戳

    def get_id(self):
        timestamp = self._gen_timestamp()

        # 如果当前时间小于上一次ID生成的时间戳，说明系统时钟回退过这个时候应当抛出异常
        if timestamp < self.last_timestamp:
            logging.error('clock is moving backwards. Rejecting requests until {}'.format(self.last_timestamp))
            raise ValueError('时钟回拨')

        # 如果是同一时间生成的，则进行毫秒内序列
        if timestamp == self.last_timestamp:
            self.sequence = (self.sequence + 1) & SEQUENCE_MASK
            if self.sequence == 0:  # 毫秒内序列溢出,阻塞到下一个毫秒,获得新的时间戳
                self.cnt += 1
                timestamp = self._til_next_millis(self.last_timestamp)
        else:
            self.sequence = 0

        self.last_timestamp = timestamp

        # 行末反斜杠是续行符
        new_id = ((timestamp - TWEPOCH) << TIMESTAMP_LEFT_SHIFT) | (self.datacenter_id << DATACENTER_ID_SHIFT) | \
                 (self.worker_id << WOKER_ID_SHIFT) | self.sequence
        # print(bin(timestamp - TWEPOCH), bin(self.datacenter_id), bin(self.worker_id), bin(self.sequence))
        return new_id

    def _til_next_millis(self, last_timestamp):  # 等到下一毫秒
        timestamp = self._gen_timestamp()
        while timestamp <= last_timestamp:
            timestamp = self._gen_timestamp()
        return timestamp


def creare_worker(houseid=1, computerid=1):
    sample_worker = IdWorker(houseid, computerid)
    return sample_worker
