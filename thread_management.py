import threading
import time
from directory_management import Directory
from disk_management import Disk
from memory_management import Memory

my_disk = Disk(4 * 1024 * 1024, 4 * 1024, 1024, 900, 124, 100)
my_disk.generate_group_link()
my_disk.generate_disk_block()

my_dir = Directory()

my_memory = Memory(256 * 1024, 64)
my_memory.create_memory_list()

mutex = 1


class Data_Generation_Thread(threading.Thread):
    def __init__(self, name, data_source, file_name, file_extension, user, structure):
        super(Data_Generation_Thread, self).__init__()
        self.name = name
        self.data_source = data_source
        self.file_name = file_name
        self.file_extension = file_extension
        self.file_full_name = self.file_name + '.' + self.file_extension
        self.user = user
        self.structure = structure
        self.add = ''

    def run(self):
        print('task:{} is running......'.format(self.name))
        present_time = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        my_dir.create_file(self.file_name, self.file_extension, present_time, self.user, self.structure, self.data_source, my_disk)
        self.get_add()

    def get_add(self):
        file_add_blocks = my_disk.read_file_add_from_disk(self.file_full_name)
        self.add = str(file_add_blocks[0]) + '-' + str(file_add_blocks[-1])


class Data_Del_Thread(threading.Thread):
    def __init__(self, name, file_name):
        super(Data_Del_Thread, self).__init__()
        self.name = name
        self.file_name = file_name

    def run(self):
        print('task:{} is running......'.format(self.name))
        my_dir.del_file_directory(self.file_name, my_disk)


class Execute_Thread(threading.Thread):
    def __init__(self, name, file_name):
        super(Execute_Thread, self).__init__()
        self.name = name
        self.file_name = file_name
        self.memory_list = []
        self.group_link = None

    def run(self):
        global mutex
        while mutex == 0:
            continue
        mutex -= 1
        print('task:{} is running......'.format(self.name))
        my_memory.read_file_from_disk_to_memory(my_disk, self.file_name)
        my_memory.save_file_to_memory(8, 160, my_disk)
        self.get_memory_list()
        self.get_group_link_list()
        mutex += 1

    def get_memory_list(self):
        self.memory_list = my_memory.memory_list

    def get_group_link_list(self):
        self.group_link = my_disk.group_link


if __name__ == '__main__':
    data_generation_thread = Data_Generation_Thread('data_generation', '2.txt', 'file', 'txt', 'zxj', 'structure')
    data_del_thread = Data_Del_Thread('data_delete', 'file.txt')
    execute_thread = Execute_Thread('execute', 'file.txt')
    data_generation_thread.start()
    data_generation_thread.join()
    time.sleep(5)
    execute_thread.start()
    execute_thread.join()
    data_del_thread.start()
    data_del_thread.join()


