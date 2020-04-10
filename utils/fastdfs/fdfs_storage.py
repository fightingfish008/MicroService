import os
from fdfs_client.client import Fdfs_client


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
client_conf = BASE_DIR + "/conf/fdfs_client_dev.conf"


def save(imagefile):
    fd_fs = Fdfs_client(client_conf)
    # meta_dict = {'ext_name': 'jpg', 'file_size': '10240B', 'width': '160px', 'hight': '80px'}
    res = fd_fs.upload_by_buffer(filebuffer=imagefile, file_ext_name="jpg", meta_dict={})
    return res



