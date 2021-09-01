import cmath


class DiskBlock:
    """
        定义磁盘块
    """

    def __init__(self, index, block_type, data=None):
        self.index = index
        self.type = block_type
        self.data = data


class IndexTable:
    """
        第二重索引
    """

    def __init__(self, index):
        self.index = index
        self.index_table = []

    def generate_index_table(self, removed_list):
        self.index_table = removed_list


class GroupLink:
    """
        定义成组链接法中的超级块
    """

    def __init__(self, size, index_list, is_last_group=False):
        """
                max_size:每一个超级块的最大容量
                index:该块被上一块的哪个元素所指向
        :param size:每一个超级块的下一组空闲盘块数
        :param index_list: 超级块的空闲块号列表
        """
        self.max_size = size
        self.size = size if is_last_group == False else size - 1
        self.index_list = index_list
        self.index = 0
        self.next_group = None
        self.remove_block_list = []

    # 清空该超级块的内容
    def clear_group_link(self):
        self.index_list = []
        self.size = 0

    # 和下一组进行链接
    def link_next_group(self, next_group):
        self.next_group = next_group
        self.next_group.index = self.index_list[-1]

    # 清空目前所使用的块的列表
    def clear_remove_block_list(self):
        self.remove_block_list = []

    # 寻找并移走空闲块
    def remove_free_blocks(self, num_blocks):
        if num_blocks < self.size:
            for i in range(num_blocks):
                self.remove_block_list.append(self.index_list[i])
            self.index_list = self.index_list[num_blocks:]
            self.size -= num_blocks
        elif num_blocks >= self.size:
            next_block_num = num_blocks - self.size
            for block in self.index_list:
                self.remove_block_list.append(block)
            self.index_list = self.next_group.index_list
            self.size = self.next_group.size
            self.next_group = self.next_group.next_group
            self.remove_free_blocks(next_block_num)

    # 回收空闲块
    def recover_free_blocks(self, block_list):
        for block in block_list:
            if self.size != self.max_size:
                self.index_list.insert(0, block)
                self.size += 1
            else:
                # 超级块已满，创建一个新的超级块
                group_link = GroupLink(self.size, self.index_list)
                group_link.link_next_group(self.next_group)
                self.link_next_group(group_link)
                self.clear_group_link()
                self.index_list.append(block)
                self.size += 1
                self.link_next_group(group_link)


class Disk:
    """
        定义磁盘
    """

    def __init__(self, size, block_size, num_blocks, num_normal_blocks, num_exchange_blocks, group_link_size):
        """
        :param size:磁盘的内存总大小
        :param size:每块的大小
        :param num_blocks: 磁盘的块数
        :param num_normal_blocks: 普通块
        :param num_exchange_blocks: 兑换块
        :param group_link_size: 超级块的大小N
        """
        self.size = size  # 磁盘的总内存
        self.block_size = block_size  # 磁盘中块的大小
        self.num_blocks = num_blocks  # 磁盘中块的总数
        self.num_normal_blocks = num_normal_blocks  # 磁盘中的普通块数目
        self.num_exchange_blocks = num_exchange_blocks  # 磁盘中的兑换块数目
        self.disk_blocks = []  # 磁盘中的磁盘块
        self.num_free_blocks = self.size  # 现有的空闲块数目
        self.group_link_size = group_link_size  # 超级块大小
        self.group_link = None  # 超级块头结点
        self.sec_index = []  # 索引表
        self.file_index_dict = {}  # 记录文件名和索引表值的字典
        self.index = 0  # 记录索引表使用到了第几个索引值

    # 生成索引表序列
    def generate_sec_index(self):
        self.sec_index = [i for i in range(0, cmath.sqrt(self.num_blocks) / 2)]

    # 生成磁盘块
    def generate_disk_block(self):
        for i in range(0, self.num_blocks):
            block_type = 'normal' if i < self.num_normal_blocks else 'exchange'
            disk_block = DiskBlock(i, block_type)
            self.disk_blocks.append(disk_block)

    # 生成成组链接表
    def generate_group_link(self):
        num_group_link = int(self.size / self.block_size / self.group_link_size) + 1
        first_group_list = [i for i in range(0, self.group_link_size)]
        # 产生第一个超级块
        self.group_link = GroupLink(self.group_link_size, first_group_list)
        # 产生后面的超级块
        last_group_link = self.group_link
        for i in range(1, num_group_link):
            if i != num_group_link - 1:
                group_link_size = self.group_link_size
                group_list = [j for j in range(i * self.group_link_size, (i + 1) * self.group_link_size)]
            else:
                group_list = [j for j in range(i * self.group_link_size, self.num_blocks)]
                group_link_size = len(group_list)
            group_link = GroupLink(group_link_size, group_list)
            # 连接前后的超级块
            last_group_link.link_next_group(group_link)
            last_group_link = group_link

    # 将数据写入某块
    def write_data_to_block(self, block_index, data):
        self.disk_blocks[block_index].data = data
        self.num_free_blocks -= 1

    # 将数据写入磁盘（数据分块 + 寻找合适空闲块 + 写入数据）
    def save_file_to_disk(self, filename, data):
        # 先将data全部转换为字节格式
        data_bytes = data.encode()
        data_size = len(data_bytes)
        # 计算需要用到的块数
        num_blocks_needed = int(data_size / (4 * 1024)) + 1
        # 将超级块中的块移出，并将移出的块的列表交给block_used
        self.group_link.remove_free_blocks(num_blocks_needed)
        block_used = self.group_link.remove_block_list
        self.group_link.clear_remove_block_list()
        # 创建一个第二重索引表，代表该文件的实际地址
        index_table = IndexTable(self.index)
        index_table.generate_index_table(block_used)
        # 将该索引表添加至第一层索引列表中,将对应的序号和文件名形成字典，序号+1
        self.sec_index.append(index_table)
        self.file_index_dict[filename] = self.index
        self.index += 1
        # 将内容写入块中
        for i, block_index in enumerate(block_used):
            if i != num_blocks_needed - 1:
                block_data = data_bytes[i * 4 * 1024:(i + 1) * 4 * 1024]
            else:
                block_data = data_bytes[i * 4 * 1024:]
            self.write_data_to_block(block_index, block_data)

    # 将数据从磁盘中清除
    def del_file_from_disk(self, filename):
        stored_blocks = self.read_file_add_from_disk(filename)
        self.group_link.recover_free_blocks(stored_blocks)
        for index in stored_blocks:
            self.disk_blocks[index].data = None

    # 读出磁盘中存储文件的地址
    def read_file_add_from_disk(self, filename):
        sec_num = self.file_index_dict[filename]
        stored_blocks = self.sec_index[sec_num].index_table
        return stored_blocks

    # 读出磁盘中的内容
    def read_file_from_disk(self, filename):
        stored_blocks = self.read_file_add_from_disk(filename)
        output_string = b''
        for index in stored_blocks:
            output_string += self.disk_blocks[index].data
        return output_string

    # 打印空闲块
    def print_free_blocks(self):
        group = self.group_link
        print('第一个栈：')
        print('index={}, N={}, \ndata:{}'.format(group.index, group.size, group.index_list))

        while group.next_group is not None:
            group = group.next_group
            print('下一个栈:')
            print('index={}, N={}, \ndata:{}'.format(group.index, group.size, group.index_list))

    # 打印磁盘数据
    def print_disk_data(self):
        for i, block in enumerate(self.disk_blocks):
            print('第{}个磁盘块所存储的内容是{}'.format(i, block.data))

# disk = Disk(4*1024*1024, 4*1024, 1024, 900, 124, 100)
# disk.generate_group_link()
# disk.generate_disk_block()
#
# file = open('1.txt', encoding='utf-8')
# file_text = file.read()
# file.close()
# disk.save_file_to_disk('file', file_text)
# disk.print_disk_data()
# disk.read_file_from_disk('file')
#
# disk.print_free_blocks()
# disk.del_file_from_disk('file')
# disk.print_disk_data()
# disk.print_free_blocks()
