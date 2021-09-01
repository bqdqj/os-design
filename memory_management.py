import random
from disk_management import Disk


class Memory_Block:
    def __init__(self, size, index, data=None, free=True):
        self.size = size
        self.index = index
        self.data = data
        self.free = free

    # 向内存块中加入数据
    def set_data(self, data):
        self.data = data


class Page:
    def __init__(self, index, data=None):
        self.index = index
        self.data = data
        self.visit = 0

    def change_visit(self):
        self.visit = 1


# 将内容放入磁盘兑换区（用于将内存中置换出的页放入）
def save_page_to_exchange_area(disk, page):
    for block in disk.disk_blocks:
        if block.type == 'exchange':
            block.data = page
    print('已成功将页{}存入磁盘对换区的块{}中'.format(page.index, block.index))


class Memory:
    def __init__(self, size, num_block):
        self.size = size  # 内存总大小
        self.num_block = num_block  # 内存总块数
        self.block_size = size / num_block  # 内存块的大小
        self.memory_list = []  # 内存中内存块组成的列表
        self.free_block_list = []  # 内存中空闲块组成的列表
        self.page_list = []  # 页组成的列表
        self.string = None  # 存储从磁盘中读出的字符串

    # 创建一个空的内存空间
    def create_memory_list(self):
        for i in range(0, self.num_block):
            memory_block = Memory_Block(self.block_size, i)
            self.memory_list.append(memory_block)
            self.free_block_list.append(i)

    # 创建一个页的列表
    def create_page_list(self, num_pages):
        for i in range(0, num_pages):
            page = Page(i)
            self.page_list.append(page)

    # 为进入内存的数据寻找空闲的内存块
    def find_free_blocks(self, num_blocks):
        if len(self.free_block_list) == 0:
            print('已无空闲内存块')
            return None
        block_list = []
        for _ in range(0, num_blocks):
            index = self.free_block_list[0]
            self.free_block_list.remove(index)
            self.memory_list[index].free = False
            block_list.append(self.memory_list[index])
        return block_list

    # 将磁盘中的文件读出到内存
    def read_file_from_disk_to_memory(self, disk, file_name):
        self.string = disk.read_file_from_disk(file_name)

    # 为每个文件分配8个内存块，并且执行全局置换
    def save_file_to_memory(self, num_blocks, num_pages, disk):
        # 分配8个内存块
        memory_blocks = self.find_free_blocks(num_blocks)
        # 将文件信息存入内存块，每个信息随机对应一个页
        self.create_page_list(num_pages)
        data_bytes = self.string
        data_size = len(data_bytes)
        num_pages_needed = int(data_size / (4 * 1024)) + 1
        memory_blocks_used = 0
        for i in range(0, num_pages_needed):
            # 随机取一页
            page_index = random.randint(0, num_pages - 1)
            print('第{}部分所用的页是{}'.format(i, page_index))
            # 如果目前不是最后一页，就直接装4KB
            if i != num_pages_needed - 1:
                self.page_list[page_index].data = data_bytes[i * 4 * 1024:(i + 1) * 4 * 1024]
            # 到最后一页，直接装剩下的所有东西
            else:
                self.page_list[page_index].data = data_bytes[i * 4 * 1024:]
            # 判断该页是否已经在内存列表中
            # 执行全局置换算法，判断该内存列表中的内存块是否已经被全部用完
            page_is_in_block = False
            for block in memory_blocks:
                if block.data is None:
                    continue
                if block.data.index == self.page_list[page_index].index:
                    block.data = self.page_list[page_index]
                    page_is_in_block = True
                    block.data.visit = 1
            # 如果该页在内存中，由于刚才已经将visit置为1，可以直接进入下一次选页
            if page_is_in_block:
                print('页{}已经在内存块中，命中！'.format(page_index))
                continue
            # 如果该内存列表中的内存块已经全部被用完，则新分配一块
            if memory_blocks_used >= num_blocks:
                new_block = self.find_free_blocks(1)
                new_block = new_block[0] if new_block is not None else None
                if new_block is not None:
                    memory_blocks.append(new_block)
                # 如果无空闲内存块，执行clock置换算法
                else:
                    self.clock_algorithm(memory_blocks, page_index, disk)
            # 如果该页不在内存中，则将该页添加至内存的第一个没有页的块
            for block in memory_blocks:
                if block.data is None:
                    block.data = self.page_list[page_index]
                    print('未命中，内存未满，该页存于内存块{}中'.format(block.index))
                    memory_blocks_used += 1
                    break

    # 页面置换算法clock
    def clock_algorithm(self, memory_blocks, page_index, disk):
        for block in memory_blocks:
            # 如果找到第一个没被命中过的页，则将该块指向的页替换成新页
            if block.data.visit == 0:
                save_page_to_exchange_area(disk, block.data)
                block.data = self.page_list[page_index]
                print('未命中，内存已满，该页已经和页{}发生置换，进入内存块{}中'.format(block.data.index, block.index))
                print('目前内存的情况：\n')
                self.print_block_status()
                break
            elif block.data.visit == 1:
                block.data.visit = 0

    # 回收内存
    def recover_memory(self):
        self.memory_list = []
        self.free_block_list = []
        self.create_memory_list()

    # 打印空闲块
    def print_free_block(self):
        print('目前空闲的块有:')
        print(self.free_block_list)

    # 打印所有块情况
    def print_block_status(self):
        for block in self.memory_list:
            if block.data:
                print('该内存块的序号为{},保存的页是{},页中的内容为{},页面的visit值为{}'.format(block.index, block.data.index, block.data.data,
                                                                        block.data.visit))
            else:
                print('该内存块的序号为{},为空闲块'.format(block.index))


# disk = Disk(4 * 1024 * 1024, 4 * 1024, 1024, 900, 124, 100)
# disk.generate_group_link()
# disk.generate_disk_block()
#
# file = open('2.txt', encoding='utf-8')
# file_text = file.read()
# file.close()
# disk.save_file_to_disk('file', file_text)
#
# memory = Memory(256 * 1024, 64)
# memory.create_memory_list()
# memory.read_file_from_disk_to_memory(disk, 'file')
# memory.save_file_to_memory(8, 160, disk)
