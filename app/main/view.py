from flask import flash, session, request, render_template, url_for, redirect, abort, current_app, g
import time
import datetime
import os
from . import main
from app import models
from process import *
import config
from win32com import client as wc
import pythoncom
import pdfplumber
# 全局参数区
temp_glob = None


@main.route('/abs')
def index():
    weekday = models.get_weekday()
    return render_template('index.html', beautiful=config.beautiful_images,
                           weekday=weekday, poems=config.poems)


@main.route('/')
def work():
    return render_template('work.html')


@main.route('/work/get_data', methods=['GET', 'POST'])
def get_data():
    global temp_glob
    if request.method == "POST":
        file_obj = request.files.get("up_file")  # 上传的文件从request.FILES中取
        # 桥梁作用 可以知道最开始的obj是空的或不是空的
        temp_obj = file_obj
        if not temp_obj:
            file_obj = request.files.get('file')

        if file_obj.filename[-3:] != 'doc':
            temp_glob = ['文件必须为doc文件']
            return render_template('work.html', txt_info=['文件必须为doc文件'])
        # 获得ip地址 + 文件名
        ip_txt = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S.%f') + '+' + request.remote_addr\
                 + '+' +file_obj.filename[:-4] + '.txt'
        save_path = os.path.join(config.base_dir, file_obj.filename)
        txt_path = os.path.join(config.base_dir, file_obj.filename.split('.')[0] + '.pdf')
        # 保存文件
        file_obj.save(save_path)

        # 文件转化！
        pythoncom.CoInitialize()
        wps = wc.DispatchEx('kwps.Application')
        doc = wps.Documents.Open(r'{}'.format(save_path))
        doc.SaveAs(txt_path, 17)
        doc.Close()
        wps.Quit()
        pythoncom.CoUninitialize()
        pdf = pdfplumber.open(txt_path)
        text_data = pdf_get(pdf, ip=ip_txt, filename=file_obj.filename[:-4] + '.txt')
        text_data = check_parts(text_data)
        pdf.close()
        # # 不是用split而使用正则表达式！
        # txt_info = get_content(path=txt_path)
        # summary_txt, claim, manual_part, manual_txt, map_lis = get_parts(txt_info)
        # 获得类别
        if '本发明' in text_data['abstract']:
            cls = '发明专利'
        else:
            cls = '实用新型'
        all_content = All(text_data['all'])
        summary_obj = Summary(text_data['abstract'])
        claim_obj = Claim(text_data['claim'])
        manual_obj = Manual(text_data['instructions'])
        maps = Map(text_data['ms'])
        asd = Rule(summary_obj, claim_obj, manual_obj, maps, all_content)
        asd.get_rule(r'C:\Users\Administrator\Desktop\workspace\flask_project-master\特定词汇表.txt')
        asd.run_rule(cls=cls)
        result = get_result(path=ip_txt)
        # if len(result) == 1:
        #     result.append('没有发现错误')
        os.remove(save_path)
        os.remove(txt_path)
        temp_glob = result
        if temp_obj:
            temp_glob = None
        return render_template('work.html', txt_info=result)
    return redirect(url_for('main.work'))


@main.route('/work/temp_data/')
def temp_data():
    global temp_glob
    start = time.time()
    while not temp_glob:
        end = time.time()
        temp = end-start
        time.sleep(0.1)
        if temp > 20:
            return redirect(url_for('main.work'))
    temp = temp_glob
    temp_glob = None
    print('temp_glob', temp_glob)
    return render_template('work.html', txt_info=temp)
