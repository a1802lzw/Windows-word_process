import pdfplumber
from collections import defaultdict
import numpy as np
import re
import json
import requests
import base64
# 这里只是demo，较好的"获得数据"的方案参考flask_project
manual_parts = [['技术领域'], ['背景技术'], ['实用新型内容', '发明内容'], ['附图说明'], ['具体实施方式', '具体实施例']]


# 参数是p页数
def get_img_label(p):
    images = p.images
    string = p.extract_text().split('\n')[1:-1]
    # print(string)
    temp_list = []
    temp_dict = {}
    # 图如果是字符为第一级
    for item in string:
        if '图' in item:
            temp_dict[item] = temp_list
            temp_list = []
        else:
            result = [re.sub(re.compile(r'\W'), '', i) for i in item.split(' ')]
            temp_list.extend(result)

    # 图如果是真的图，那么作为第二级
    for key in temp_dict:
        if not temp_dict[key]:
            img = images.pop(0)
            name = img['name']
            img = img['stream'].get_data()
            base64_image = base64.b64encode(img).decode()
            data = {'filename': f'{name}.png',
                    'image': base64_image,
                    'show': False
                    }
            data = json.dumps(data)
            response = requests.post('http://192.168.0.13:5000/author/ocr', data=data)
            response_dict = json.loads(response.text)
            # 去除分数过低的
            response_string = [re.sub(re.compile(r'\W'), '', i[0]) for i in response_dict['string'] if i[1] > 0.8]
            temp_dict[key] = response_string
    return temp_dict


def get_manual_part_util(string):
        idx = []
        for values in manual_parts:
            index = -1
            for value in values:
                index = string.find(value + '\n')
                # 可能在最后一行
                if index == -1:
                    index = string.find('\n' + value)
                if index != -1:
                    break
            idx.append(index)
        return idx


def get_manual_part(string):
    dict_parts = {}
    parts = []
    part_idx = get_manual_part_util(string)
    start = 0
    for val_idx, val in enumerate(part_idx):
        if val == -1:
            print(f'说明书主要内容可能缺少{manual_parts[val_idx]}')
            parts.append('')
        else:
            if not start:
                start = val
                continue
            end = val
            parts.append(string[start:end])
            start = end
    # 把末尾添加
    if part_idx[-1] != -1:
        parts.append(string[part_idx[-1]:])
    else:
        parts.append('')
    for part in parts:
        part = part.split('\n')
        key = part.pop(0)
        # print('\n'.join(part))
        dict_parts[key] = '\n'.join(part)
    return dict_parts


# 有图
# 一种应用于市政污泥处理设备.pdf
# 无图
# 一种低噪音轴流风机.pdf
parts = defaultdict(str)

maps = {}
pdf = pdfplumber.open(r'一种高纯度苯乙腈的制备方法及设备.pdf')
pages = pdf.pages
for p in pages:
    text = p.extract_text()
    split_txt = text.split('\n')
    # # 通过页眉拆分字符串
    # if split_txt[0] == '说 明 书 摘 要':
    #     parts['abstract'] += '\n'.join(split_txt[1:-1])
    # elif split_txt[0] == '摘 要 附 图':
    #     parts['m1'] += '\n'.join(split_txt[1:-1])
    # elif split_txt[0] == '权 利 要 求 书':
    #     # print(text)
    #     parts['claim'] += '\n'.join(split_txt[1:-1]) + '\n'
    # elif split_txt[0] == '说 明 书':
    #     parts['instructions'] += '\n'.join(split_txt[1:-1])
    # elif split_txt[0] == '说 明 书 附 图':
    #     # print(text)
    #     # 加上\n防止图与标签重合的情况
    #     parts['ms'] += ('\n'.join(split_txt[1:-1]) + '\n')
    # 处理特殊情况以加速
    parts['all'] += '\n'.join(split_txt[1:-1]) + '\n'
    if split_txt[0] == '权 利 要 求 书':
        # print(text)
        parts['claim'] += '\n'.join(split_txt[1:-1]) + '\n'
    elif split_txt[0] == '说 明 书':
        parts['instructions'] += '\n'.join(split_txt[1:-1])
    elif split_txt[0] == '说 明 书 附 图':
        map_label = get_img_label(p)
        for key in map_label:
            maps[key] = map_label[key]
        # parts['ms'] += ('\n'.join(split_txt[1:-1]) + '\n')
pdf.close()
# print(parts['instructions'])
print(maps)


def get_map_lis(map_string):
    map_lis = re.findall('图(.*)', map_string)
    return map_lis


# 获得权利要求列表
def get_claims(string):
    # print(string)
    claim = []
    for cla in string.split('\n'):
        if cla.strip():
            if cla.strip()[0].isdigit() or '权利要求' in cla.strip() or not claim:
                claim.append(cla)
            else:
                claim[-1] += cla
    return claim


# 权利要求列表
def check(claim_lis):
    for idx, cla in enumerate(claim_lis):
        # 检查多个句号，检查是否以句号结尾
        if cla.count('。') > 1:
            print(f'权利要求{idx+1}存在多个句号')
        if cla[-1] != '。':
            print(f'权利要求{idx+1}没有以句号结尾')
    return


# 改进空间极大
def count_part(string_lis, all_text=parts['all']):
    for idx, string in enumerate(string_lis):
        part_lis = []
        num = idx + 1
        max_len = 8
        string = re.sub(re.compile(r'\s+'), '', string)
        all_text = re.sub(re.compile(r'\s+'), '', all_text)
        array_string = np.array(list(string))
        for index in np.where(array_string == '（')[0]:
            if index > max_len:
                previous_word = []
                for i in range(1, max_len + 1):
                    word = ''.join(list(array_string)[index-i:index])
                    previous_word.append(len(set(re.findall(f'.(?={word})', all_text, re.S))))
                    # print(word)
                    # print((set(re.findall(f'.(?={word})', all_text, re.S))))
                word_len = np.argmax(previous_word)
                # 可能第一个和后面的相同, 单字为词的概率极低，所以认为是错误的
                if word_len == 0:
                    two = sorted(previous_word)[-2]
                    previous_word[0] = 0
                    word_len = previous_word.index(two)
                part_lis.append(string[index - word_len - 1:index])
        print(num, set(part_lis))


def remove_null(string):
    return re.sub(re.compile(r'\s+'), '', string)


def remove_no_character(string):
    return re.sub(re.compile(r'\W+'), '', string)


if __name__ == '__main__':
    # claim_num = get_claims(parts['claim'])
    # check(claim_num)
    # print(count_part(claim_num))
    # print(range(1, int(claim_num[-1])))
    # temp_str = get_manual_part(parts['instructions'])['附图说明']
    instr = remove_no_character(parts['instructions'])
    print(re.findall(r'鼓膜(\d{3})', instr))
    # print(re.findall('图.*?[：|:](.*)', temp_str, re.S))

    # res = re.findall('技术领域\W(.*?)背景技术\W(.*?。).*?内容\W(.*?)附图说明\W(.*?)具体实施(例|方式)\W(.*)', parts['instructions'], re.S)
    # parts_index = res[0][3].index('图中标号说明：')
    # all_parts = res[0][3][parts_index + 7:]
    # all_parts = re.sub(re.compile('\W'), '', all_parts)
    pass
