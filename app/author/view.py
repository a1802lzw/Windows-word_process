from . import author
from flask import request
import requests
# import config


@author.route('/author/ocr', methods=['GET', 'POST'])
def ocr():
    # if request.method == 'POST':
    #     return '暂无此功能'
    #     # 懒得自己写，难题交给别人吧！
    #     # params = {}
    #     # file_obj = request.files.get("get_image")
    #     # params['filename'] = file_obj.filename
    #     # response = requests.get(r'http://192.168.0.13:5000/wotk/ocr', )
    # elif request.method == 'GET':
    #     filename = request.args.get('filename')
    #     image = request.args.get('image')
    #     show = request.args.get('show')
    #     params = {
    #         'filename': filename,
    #         'image': image,
    #         'show': show
    #     }
    #     response = requests.get('https://192.168.0.13:5000/wotk/ocr', params=params)
    #     if response.status_code == 200:
    #         return response
    #     else:
    #         return 'error'
    return '暂时不用'
