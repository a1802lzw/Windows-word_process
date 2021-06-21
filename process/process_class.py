import jieba
import numpy as np
import re
from collections import defaultdict
import config
import process.utils as utils
# 用相对路径就报错，奇怪
user_dict_path = config.user_dict
# jiaba 定义
jieba.load_userdict(user_dict_path)
jieba.suggest_freq(('有', '阀门'), True)
jieba.suggest_freq(('有', '右轮'), True)
jieba.suggest_freq(('有', '右'), True)
jieba.suggest_freq(('使', '上'), True)
jieba.suggest_freq(('有', '盖'), True)
# jieba.suggest_freq('薄膜', True)

out_put = './'


# 初始化logger
def init_logger(log_file=out_put+'result.txt'):
    from logging import getLogger, INFO, FileHandler,  Formatter,  StreamHandler
    logger = getLogger(log_file)
    logger.setLevel(INFO)
    handler1 = StreamHandler()
    handler1.setFormatter(Formatter("%(levelname)s:%(message)s"))
    handler2 = FileHandler(filename=log_file)
    handler2.setFormatter(Formatter("%(levelname)s:%(message)s"))
    logger.addHandler(handler1)
    logger.addHandler(handler2)
    return logger


# 必须放在@utils.error_decorator(get_logger) 前面！
def get_logger():
    return LOGGER


class All:
    """
    所有字符
    """
    def __init__(self, string):
        self.string = string

    def find_error(self):
        # 找连续的标点符号
        string = re.sub(r"\s+|\(|\)|（|）|—|°|\”|\“", "", self.string)
        re_lis = re.findall('(\W{2})', string, re.U)
        for s in re_lis:
            idx = self.string.find(s)
            LOGGER.info(f'标点符号有问题,在 "{self.string[idx-6:idx]}" 后面')
            pass
        pass
    pass


# 类化，保存更多信息
class Summary:
    """
    说明书摘要
    """
    def __init__(self, string):
        self.string = string
        if self.string:
            self.word_lis = get_words(self.string)
            # 说明书摘要长度
            self.len = len(self.string)


class Claim:
    """
    权利要求书
    """
    def __init__(self, string):
        # self.string = re.sub(re.compile(r'\s+'), '', string)
        self.string = string
        # 权利要求 字符串
        if self.string:
            self.string_lis = split_str(self.string)
            # 获得权利要求条数
            self.claim_len = len(self.string_lis)
            # 权利要求 词表
            self.word_lis = [get_words(i) for i in self.string_lis]
            # 权利要求1数字
            self.claim_one_len = len(self.string_lis[0])

    # 差错
    @utils.error_decorator(get_logger)
    def check(self):
        # 判断 string 是否为空
        if not self.string:
            return False
        # 获得词数组和部件数组    结构 [[word_lis], [word_lis], [word_lis]]
        special_part = []
        # 假设第一个权利没有错
        for idx, array in enumerate(self.word_lis):
            part_array = array
            idx_weight = idx
            idx_weight_lis = []

            if idx_weight:
                # 可能存在独权！ 先忽略掉
                if '根据' in array:
                    if '权利要求' not in array:
                        # LOGGER.info(f'权利要求{idx + 1}出了问题， 不存在关键字："权利要求", 请修改后重新提交')
                        pass
                else:
                    continue
            # 直到引用完成否则循环寻找
            all_parts = []
            while idx_weight:
                # 权利要求索引
                idx_weight = part_array.index('权利要求') + 1
                # 获得权力要求引用对应权利要求
                idx_weight = int(part_array[idx_weight])
                assert idx_weight != idx + 1, f'权利要求{idx + 1}出了问题，不能引用自身'
                idx_weight_lis.append(idx_weight - 1)
                # 获得权力要求对应词句
                part_array = self.word_lis[idx_weight - 1]
                parts = get_part(part_array)
                all_parts.extend(parts)
                idx_weight -= 1

            # 获得所有部件，包括嵌套内容
            # 去重
            all_parts = list(set(all_parts))
            # print(all_parts)
            # 获得当前权利要求部件
            array_parts = get_part(array)
            array_parts = list(set(array_parts))

            # 检测数组内部是否存在错误
            if array_parts:
                temp_part = np.array(array_parts)[:, 0]
                temp_nums = np.array(array_parts)[:, 1]
                # print(temp_part)
                # print(temp_nums)
                temp_info = []
                for item, num in np.array(array_parts):
                    if sum(temp_part == item) != 1:
                        temp_info.append([item, num])
                    else:
                        if sum(temp_nums == num) != 1:
                            temp_info.append([item, num])
                        pass
                # for item, num in np.array(array_parts):
                #     if sum(temp_nums == num) != 1:
                #         temp_info.append(f'{item}({num})')
                if temp_info:
                    # 把部件和部件数字组合起来
                    temp_res = []
                    temp_info = np.array(temp_info)
                    key = np.unique(temp_info[:, 0])
                    for temp in key:
                        info = temp_info[np.where(temp_info[:, 0] == temp)]
                        if len(info) > 1:
                            temp_res.append(info.tolist())
                            temp_info = temp_info[np.where(temp_info[:, 0] != temp)]
                    value = np.unique(temp_info[:, 1])
                    for temp in value:
                        info = temp_info[np.where(temp_info[:, 1] == temp)]
                        if len(info) > 1:
                            # 获得最短的词 并以此为基准
                            min_word_idx = np.argmin(np.apply_along_axis(lambda x: len(x[0]),
                                                                         axis=0, arr=info[:, 0].reshape(1, -1)))
                            min_word = info.tolist()[min_word_idx]
                            info_lis = []
                            for item in info.tolist():
                                if min_word[0] not in item[0] and min_word[0] != item[0]:
                                    info_lis.append(item)
                            if info_lis:
                                info_lis.append(min_word)
                                temp_res.append(info_lis)
                            temp_info = temp_info[np.where(temp_info[:, 1] != temp)]
                    if temp_res:
                        LOGGER.info(f'权利要求{idx + 1}可能出了问题')
                        for item in temp_res:
                            LOGGER.info(f'{item}')
                        LOGGER.info(f'以上可能出现部件名称或标号错误')
            # 非权利要求1 and 权利要求存在部件时进入
            if list(array_parts) and list(all_parts):
                # print(idx+1)
                # print('all', all_parts)
                # print('####')
                # print('part', array_parts)
                for aidx in range(len(array_parts)):
                    # 查看部件名称和标号是否正确 （针对的是本条权利要求非独有的） 用 and 可能会把错误的当作独有的 先用着，如果有错再改
                    if array_parts[aidx][0] in np.array(all_parts)[:, 0]:
                        if array_parts[aidx] in all_parts:
                            # right
                            pass
                        else:
                            error_info = ''.join(array_parts[aidx])
                            # print(error_info, all_parts)
                            LOGGER.info(f'权利要求{idx + 1}出了问题，在"{error_info}", 可能部件名称或标号错误')
                    # elif array_parts[aidx][1] in np.array(all_parts)[:, 1]:
                    #     if array_parts[aidx] in all_parts:
                    #         # right
                    #         pass
                    #     else:
                    #         error_info = ''.join(array_parts[aidx])
                    #         # print(error_info, all_parts)
                    #         LOGGER.info(f'权利要求{idx + 1}出了问题，在"{error_info}", 可能部件标号错误')
                    # 本权利特有！
                    else:
                        if special_part:
                            for item, sidx in special_part:
                                if array_parts[aidx] == item:
                                    LOGGER.info(f'可能出现错误引用，关键词{array_parts[aidx]}，可能的正确引用方式为：权利要求{idx + 1}引用——>权利要求{sidx}')
                        special_part.append([array_parts[aidx], idx + 1])
                        pass
            elif not list(array_parts):
                # 暂不考虑 这种情况是引用时没有增加部件
                pass
        pass


class Manual:
    """
    说明书
    """
    def __init__(self, string):
        self.string = string
        # print(self.string)
        if self.string:
            # 获得每个部分的字符串，好进行下一步行动
            self.part1, self.part2, self.part3, self.part4, self.part5 = self.get_manual_part()
            # 说明书附图长度
            self.manual_map_len = self.get_map_len(self.part4)

    def get_manual_part(self):
        parts = []
        part_idx = self.get_manual_part_util()
        start = 0
        for val_idx, val in enumerate(part_idx):
            if val == -1:
                LOGGER.info(f'说明书主要内容可能缺少{config.manual_parts[val_idx]}')
                parts.append('')
            else:
                if not start:
                    start = val
                    continue
                end = val
                parts.append(self.string[start:end])
                start = end
        # 把末尾添加
        if part_idx[-1] != -1:
            parts.append(self.string[part_idx[-1]:])
        else:
            parts.append('')
        return parts

    def get_manual_part_util(self):
        idx = []
        for values in config.manual_parts:
            index = -1
            for value in values:
                index = self.string.find(value + '\n')
                # 可能在最后一行
                if index == -1:
                    index = self.string.find('\n' + value)
                if index != -1:
                    break
            idx.append(index)
        return idx

    @staticmethod
    @utils.error_decorator(get_logger)
    def get_map_len(string):
        return len(set(re.findall('图\s?([0-9]+)', string, re.S)))


class Map:
    """
    图有关
    """
    def __init__(self, map_string, img_lis=None):
        # 获得附图长度
        self.string = map_string
        if map_string:
            self.map_len = len(self.get_map_lis(map_string))

    @staticmethod
    @utils.error_decorator(get_logger)
    def get_map_lis(map_string):
        maps_lis = re.findall('图(.*)', map_string)
        return maps_lis


class Rule:
    """
    准则，规则，即特定词汇表以及常用规则
    """
    def __init__(self, summary, claim, manual, map, all_part):
        # 纸上先写着 [实用， 发明]
        self.class_dict = {'发明专利': {}, '实用新型': {}}
        # {'权利要求':obj, '说明书':obj}
        self.part = {'说明书': manual, '权利要求书': claim, '说明书摘要': summary, '图': map, '全文': all_part}
        # obj属性 {"权利要求1长度": 'obj_attr'} 巧用类修饰器！
        self.attr = {"权利要求1长度": 'claim_one_len',
                     '图数量': 'map_len',
                     '权利要求条数': 'claim_len',
                     '权利要求': 'string_lis'}
        # 操作，大于，长度，... {'操作符名称': 方法/函数}
        self.operator = {"大于": self.compare,
                         "小于": self.compare,
                         '大于等于': self.compare,
                         '小于等于': self.compare,
                         '必有': self.must_have,
                         '禁用': self.cant_have,
                         '互斥': self.xor}

    # @staticmethod 获得
    def get_rule(self, txt_path=None):
        """
        文档类型有两种， 文档内内容有4种，
        :param txt_path: 规则书写文件
        :return: 返回最后的规则
        """
        assert txt_path, '特定词汇表文件位置不能为空'
        with open(txt_path, encoding='utf-8') as f:
            result = f.read()
        result = result.split('\n')[1:]
        keys_values = [string.split('：') for string in result if string]
        for key, value in keys_values:
            key_lis = [i[:-1] for i in key.split('[') if i]
            value_lis = [i for i in value.split('|') if i]
            # 为空则跳过
            if not value_lis:
                continue
            # 获取类别 规则对象
            class_lis = []
            part_lis = []
            attr = None
            # print('key_lis', key_lis)
            for item in key_lis:
                # print(self.class_dict.keys())
                if item in self.class_dict.keys():
                    class_lis.append(item)
                    continue

                # elif item == '任意':
                #     class_lis.extend(self.class_dict.keys())
                #     part_lis.extend(self.part.keys())
                #     continue

                elif item in self.part.keys():
                    part_lis.append(item)
                    continue

                elif item in self.attr.keys():
                    # print(item)
                    attr = self.attr[item]
                    continue

                elif item in self.operator.keys():
                    # print('cla_lis', class_lis)
                    # print(part_lis)
                    # 前面所有类名
                    for cls in class_lis:
                        for part in part_lis:
                            # 获得操作函数
                            operator = self.operator[item]
                            # 获得将函数所需参数保存 para1 obj of part（部件对象）para2 操作所需值 para3 部件名称(不知道有没有用，留着) para4 操作符
                            para1, para2, para3, para4 = self.part[part], value_lis, part, item
                            # 获得属性参数
                            if attr in para1.__dict__:
                                para1 = para1.__dict__[attr]
                            else:
                                attr = 'string'
                                para1 = para1.__dict__[attr]
                            # 结合 前提是属性存在，及字符或者数字为空
                            if para1:
                                if part in self.class_dict[cls].keys():
                                    self.class_dict[cls][part].append([operator, para1, para2, para3, para4, attr])
                                else:
                                    self.class_dict[cls][part] = [[operator, para1, para2, para3, para4, attr]]
        return self.class_dict

    def run_rule(self, cls):
        """
        运行规则方法
        :param cls: 文档类别
        :return: state 状态
        """
        # 规则表上的规则
        for key, value in self.class_dict[cls].items():
            # print(key, value)
            for operator in value:
                # 分类，分为， string， 比较， 和列表
                if 'lis' in operator[-1]:
                    temp = dict([(value, key) for key, value in self.attr.items()])
                    for idx, string in enumerate(operator[1]):
                        result = operator[0](string, operator[2])
                        if result:
                            LOGGER.info(f'{temp[operator[-1]]}{idx+1}出了问题{result}')
                    pass
                elif 'len' in operator[-1]:
                    temp = dict([(value, key) for key, value in self.attr.items()])
                    result = operator[0](operator[1], operator[2], operator[4])
                    if result:
                        LOGGER.info(f'{temp[operator[-1]]}出了问题, {result}')
                    pass
                else:
                    result = operator[0](operator[1], operator[2])
                    if result:
                        LOGGER.info(f'{operator[3]}{result}')
                        pass

        # 非规则表上的规则
        # 非空判断
        # if self.part['说明书'].string:
        s1 = self.part['说明书'].string
        s2 = self.part['图'].string
        if s1 and s2:
            说明书的附图说明小节用文字表述的图的数量= self.part['说明书'].manual_map_len
            说明书附图中图片的张数 = self.part['图'].map_len
            if not 说明书附图中图片的张数 == 说明书的附图说明小节用文字表述的图的数量:
                LOGGER.info(f'说明书附图中图片的张数为（{说明书附图中图片的张数}） 、说明书的附图说明小节用文字表述的图的数量为（{说明书的附图说明小节用文字表述的图的数量}），二者不相符')
        self.part['权利要求书'].check()

    @staticmethod  # 必有 其中之一 简化函数用法，使其变得更通用
    def must_have(obj_sting, word_lis, mod=None):
        temp = []
        for string in word_lis:
            if obj_sting.find(string) != -1:
                temp.append(temp)
        if not temp and obj_sting:
            return f'不存在必有词{word_lis}'
        pass

    @staticmethod  # 禁用 不能有其中之一
    def cant_have(obj_string, word_lis, mod=None):
        temp = []
        for string in word_lis:
            if obj_string.find(string) != -1:
                temp.append(string)
        if temp:
            return f'存在禁用词{temp}'
        pass

    @staticmethod  # 使用闭包解决参数通用性问题
    def compare(num, value, mod='大于'):
        # value 是列表里面存着字符串，先转为数字
        value = int(value[0])
        temp = value
        if '大于等于' in mod:
            func = min
        elif '小于等于' == mod:
            func = max
        elif '大于' == mod:
            func = min
            temp += 1
        elif '小于' == mod:
            func = max
            temp -= 1
        else:
            # 以后使用logging 反映
            raise ValueError('操作符字符写错了')
        if not temp == func(num, temp):
            return f'要求{mod}临界值:{value}，实际{num}'

    @staticmethod  # 互斥 必须存在其一，但是不能同时存在
    def xor(obj_string, word_lis, mod=None):
        temp = []
        for word in word_lis:
            if obj_string.find(word) != -1:
                temp.append(word)
        if len(temp) != 1 and temp and obj_string:
            return f'存在互斥词{temp}'


# 列表版版
@utils.error_decorator(get_logger)
def get_part(word):
    """
    word array
    """
    # 可能包含多个引用
    # array 不太好用， 转为 list
    # 可能会出现(n-n-n)
    parts = []
    for idx, i in enumerate(word):
        if i in ['（', '(']:
            temp_idx = 0
            nums = ''
            while word[idx+1+temp_idx] not in ['）', ')']:
                nums += word[idx+1+temp_idx]
                temp_idx += 1
            ######################################
            # 测试，到底是两个词好还是一个词好 基本是两个词好 增加停用词，增加正确率
            ######################################
            with open(config.stop_dict, encoding='utf-8') as f:
                stop_word = f.read().split('\n')
                stop_word.append('\n')
            # print(stop_word)
            if word[idx - 2] in stop_word:
                parts.append((word[idx-1], nums))
            # elif not word[idx - 1]:
            #     parts.append((word[idx - 3] + word[idx - 2], nums))
            else:
                parts.append((word[idx - 2] + word[idx - 1], nums))
    return parts


# 分割权利要求的函数，有待提高
@utils.error_decorator(get_logger)
def split_str(string):
    # print(string)
    str_lis = []
    for cla in string.split('\n'):
        cla = re.sub(re.compile(r'\s+'), '', cla)
        if cla:
            if cla[0].isdigit() or '权利要求' in cla or not str_lis:
                if str_lis:
                    # 获得长度就能知道是权利要求几了
                    error_info = ''
                    if str_lis[-1].count('。') > 1:
                        error_info = f'权利要求{len(str_lis)}可能出了问题, 可能存在多个句号'
                    elif str_lis[-1].count('。') == 1 and str_lis[-1][-1] != '。':
                        error_info = f'权利要求{len(str_lis)}可能出了问题, 句号可能写错地方'
                    elif str_lis[-1].count('。') == 0:
                        error_info = f'权利要求{len(str_lis)}可能出了问题, 没有以句号结尾'
                    if error_info:
                        LOGGER.info(error_info)
                str_lis.append(cla)
            else:
                str_lis[-1] += cla
    return str_lis


# 分词函数
@utils.error_decorator(get_logger)
def get_words(string):
    return list(jieba.cut(string))


# get text result
def get_result(path='result.txt'):
    path = f'results\{path}'
    # 没有文本则报错， 貌似没有意义
    if not path:
        raise ValueError('path不能为空')
    with open(path) as f:
        txt_info = f.read()
        temp = re.findall('INFO:(.*)', txt_info)
        txt_info = [i.strip() for i in temp]
    # open(path, 'w').close()  # 解开后会把记录删除
    if len(txt_info) == 1:
        LOGGER.info('没有发现错误')
        txt_info.append('没有发现错误')
    return txt_info


# 获得说明书部分辅助函数
@utils.error_decorator(get_logger)
def get_manual_part(manual_txt=None):
    assert manual_txt, '说明书内容为空'
    try:
        parts = re.findall('技术领域\W(.*?)背景技术\W(.*?。).*?内容\W(.*?)附图说明\W(.*?)具体实施(例|方式)\W(.*)', manual_txt, re.S)
    except IndexError as e:
        # 错误信息
        error_info = '说明书中小节名称错误，请确认说书中以下小节名称[技术领域][背景技术][?内容][附图说明][具体实施?]'
        LOGGER.info(error_info)
        raise ValueError(error_info)
    return parts[0]


# 老版获得文档部件辅助函数
"""
def get_parts(content):
    part1 = re.findall('(.*?)(技术领域\n.*)', content, re.S)
    # split 切割
    # 摘要
    summary_txt = re.findall('(.*?)。\n', part1[0][0], re.S)[0].strip()
    # 权利要求
    claim_txt = re.findall('。\n(.*)', part1[0][0], re.S)[0].strip()
    manual_part = claim_txt.split('\n')[-1]
    claim_txt = '\n'.join(claim_txt.split('\n')[:-1])
    # 主题
    # print(claim_txt)
    # print(manual_part)
    if '图1' in part1[0][1]:
        # print(part1[0][1])
        temp_manual_lis = re.findall('(.*)(\n图\D*?1\s.*)', part1[0][1], re.S)[0]

        temp_manual = temp_manual_lis[0]
        # print(temp_manual)
        # 图
        map_str = temp_manual_lis[1]
        # print(map_str)
        # 获得图列表
        map_lis = re.findall('图(.*)', map_str)
    else:
        temp_manual = part1[0][1]
        map_lis = []
    return summary_txt, claim_txt, manual_part, temp_manual, map_lis
"""


# 获得文档部件辅助函数
# @utils.error_decorator(get_logger)
def pdf_get(pdf, ip='127.0.0.1.txt', filename='1'):
    global LOGGER
    # data = f'datasets\{ip}'
    ip = f'results/{ip}'
    # file_write = open(data, 'w', encoding='utf-8')
    LOGGER = init_logger(ip)
    name = pdf.stream.name.split('\\')[-1][:-4]
    LOGGER.info(f'案子:{name}')
    pages = pdf.pages
    parts = defaultdict(str)
    for p in pages:
        text = p.extract_text()
        # 文本若为空，跳过
        if not text:
            continue
        split_txt = text.split('\n')
        title = re.sub(re.compile(r'\s+'), '', split_txt[0])
        string = '\n'.join(split_txt[1:-1]) + '\n'
        # 通过页眉拆分字符串
        if title in config.doc_parts:
            parts[config.doc_parts[title]] += string
            parts[config.doc_parts['全文']] += string
    # print(parts)
    # file_write.close()
    return parts


@utils.error_decorator(get_logger)
def check_parts(doc_parts):
    temp_dict = {}

    for key, values in config.doc_parts.items():
        if values in doc_parts.keys():
            temp_dict[values] = doc_parts[values]
        else:
            # 把不存在的赋空
            temp_dict[values] = ''
            # 写入，哪些不存在
            LOGGER.info('页眉-' + key + '-不存在')
    return temp_dict


if __name__ == '__main__':
    pass



