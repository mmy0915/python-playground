import mmap
mmap_file = None


##从内存中读取信息，
def read_mmap_info():
    global mmap_file
    mmap_file.seek(0)
    ##把二进制转换为字符串
    info_str=mmap_file.read().translate(None, b'\x00').decode()
    return info_str
##如果内存中没有对应信息，则向内存中写信息以供下次调用使用

##修改内存块中的数据
def reset_mmap_info(filename):
    global mmap_file
    cnt=mmap_file.read_byte()
    if cnt==0:
        mmap_file.write(filename.encode('utf-8'))
    else:
        mmap_file.close()
        mmap_file = mmap.mmap(-1, 1024, access = mmap.ACCESS_WRITE, tagname = 'share_mmap')
        mmap_file.seek(0)
        mmap_file.write(filename.encode('utf-8'))
    #mmap_file.write(b"Load data to memory again")


def get_mmap_info(filename):
    global mmap_file
    ##第二个参数1024是设定的内存大小，单位：字节。如果内容较多，可以调大一点
    mmap_file = mmap.mmap(-1, 1024, access = mmap.ACCESS_WRITE, tagname = 'share_mmap')
    ##读取有效比特数，不包括空比特
    cnt=mmap_file.read_byte()
    if cnt==0:
        print("Load data to memory")
        mmap_file = mmap.mmap(0, 1024, access = mmap.ACCESS_WRITE, tagname = 'share_mmap')
        mmap_file.write(filename.encode('utf-8'))
    else :
        reset_mmap_info(filename)



if __name__ == '__main__':
    #get_mmap_info('123456')
    #print(read_mmap_info())
    reset_mmap_info('123')
    print(read_mmap_info())
