from disk_management import Disk, IndexTable


class FCB:
    def __init__(self, file_name, file_extension, creation_time, user, structure, data_source):
        """
        :param file_name: 文件名
        :param file_extension: 文件扩展名
        :param creation_time: 文件创建时间
        :param user: 文件所有人
        :param structure: 文件结构
                file_length: 文件大小
                address: 文件在磁盘中存放的地址
                data_source:要读取的文件的名称
        """
        self.file_name = file_name
        self.file_extension = file_extension
        self.file_length = None
        self.creation_time = creation_time
        self.user = user
        self.structure = structure
        self.data_source = data_source
        self.address = None
        self.data = None
        if self.file_name and self.file_extension:
            self.file_full_name = self.file_name + '.' + self.file_extension
        else:
            self.file_full_name = None

    # 获取某个文件中的data
    def get_data(self):
        file = open(self.data_source, encoding='utf-8')
        self.data = file.read()
        file.close()

    # 获取该文件的长度
    def get_file_length(self):
        data_length = self.data.encode()
        self.file_length = len(data_length)

    # 将该文件存入disk中
    def save_fcb_to_disk(self, disk):
        disk.save_file_to_disk(self.file_full_name, self.data)
        sec_num = disk.file_index_dict[self.file_full_name]
        stored_blocks = disk.sec_index[sec_num].index_table
        self.address = stored_blocks

    # 将该文件从disk中删除
    def del_fcb_from_disk(self, disk):
        disk.del_file_from_disk(self.file_full_name)

    # 获取该文件在磁盘中的地址块
    def get_address(self):
        return self.address


class Directory:
    def __init__(self):
        self.directory = []

    # 创建空目录
    def create_empty_directory(self, num):
        for i in range(0, num):
            fcb = FCB(None, None, None, None, None, None)
            self.directory.append(fcb)

    # 删除空目录
    def del_empty_directory(self):
        for fcb in self.directory:
            if not fcb.file_name:
                self.directory.remove(fcb)

    # 为文件创建目录项
    def create_file_directory(self, fcb):
        for f in self.directory:
            if f.file_full_name == fcb.file_full_name:
                print('文件已存在')
                return
        self.directory.append(fcb)
        print('已成功在目录中创建目录项:{}'.format(fcb.file_full_name))

    # 完整地创建一个文件（读入数据 + 创建目录项 + 添加至磁盘）
    def create_file(self, file_name, file_extension, creation_time, user, structure, data_source, disk):
        fcb = FCB(file_name, file_extension, creation_time, user, structure, data_source)
        fcb.get_data()
        fcb.get_file_length()
        fcb.save_fcb_to_disk(disk)
        print('已成功将文件添加至磁盘，当前磁盘的情况为:')
        disk.print_disk_data()
        print('当前成组链接块的情况为:')
        disk.print_free_blocks()
        self.create_file_directory(fcb)
        self.print_directory()

    # 删除文件及其在磁盘中的数据
    def del_file_directory(self, file_full_name, disk):
        for fcb in self.directory:
            if fcb.file_full_name == file_full_name:
                fcb.del_fcb_from_disk(disk)
                self.directory.remove(fcb)
                break
        print('已成功将文件从磁盘中删除，当前磁盘的情况为:')
        disk.print_disk_data()
        print('当前成组链接块的情况为:')
        disk.print_free_blocks()
        self.print_directory()

    # 打印当前目录内容
    def print_directory(self):
        print('\n当前目录的内容为：\n')
        for i, fcb in enumerate(self.directory):
            print('第{}条目录信息如下：'.format(i+1))
            print('文件名：{}'.format(fcb.file_full_name))
            print('文件所有者:{}'.format(fcb.user))
            print('创建时间：{}'.format(fcb.creation_time))
            print('文件结构:{}'.format(fcb.structure))
            print('在磁盘中所存放的地址：{}\n'.format(fcb.address))


# disk = Disk(4*1024*1024, 4*1024, 1024, 900, 124, 100)
# disk.generate_group_link()
# disk.generate_disk_block()
# my_dir = Directory()
# my_dir.create_empty_directory(3)
# my_dir.create_file('file', 'txt', '2020.12.20.15:38', 'zxj', 'structure', '1.txt', disk)
