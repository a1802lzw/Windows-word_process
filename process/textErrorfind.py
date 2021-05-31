import numpy as np
import re
import jieba
from collections import defaultdict


class All:
    """
    所有字符
    """
    def __init__(self, string):
        self.result = []
        self.string = string

    def find_error(self):
        # 找连续的标点符号
        string = re.sub(r"\s+|\(|\)|（|）|—|°|\”|\“", "", self.string)
        re_lis = re.findall('(\W{2})', string, re.U)
        for s in re_lis:
            idx = self.string.find(s)
            # print(self.string[idx-6:idx])
            self.result.append(f'标点符号有问题,在 "{self.string[idx-6:idx]}" 后面')
        return self.result


class Summary:
    """
    说明书摘要
    """
    def __init__(self, string):
        self.result = []
        self.string = string
        # 说明书摘要长度
        self.len = len(string)
    pass


class Claim:
    """
    权利要求书
    """
    def __init__(self, string):
        self.result = []
        self.string = string
        # 权利要求 字符串
        self.string_lis = self.split_str(string)
        # 获得权利要求条数
        self.claim_len = len(self.string_lis)
        # 权利要求 词表
        self.word_lis = [self.get_words(i) for i in self.string_lis]
        # 权利要求1数字
        self.claim_one_len = len(self.string_lis[0])

    # 差错
    def check(self):
        # print(111)
        # 获得词数组和部件数组    结构 [[word_lis], [word_lis], [word_lis]]
        special_part = []
        # 假设第一个权利没有错
        for idx, array in enumerate(self.word_lis):
            # if idx + 1 == 1:
            #     print(array)
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
                idx_weight_lis.append(idx_weight - 1)
                # 获得权力要求对应词句
                part_array = self.word_lis[idx_weight - 1]
                parts = self.get_part(part_array)
                all_parts.extend(parts)
                idx_weight -= 1

            # 获得所有部件，包括嵌套内容
            # 去重
            all_parts = list(set(all_parts))
            # print(all_parts)
            # 获得当前权利要求部件
            array_parts = self.get_part(array)
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
                        temp_info.append(f'{item}({num})')
                    else:
                        if sum(temp_nums == num) != 1:
                            temp_info.append(f'{item}({num})')
                        pass
                # for item, num in np.array(array_parts):
                #     if sum(temp_nums == num) != 1:
                #         temp_info.append(f'{item}({num})')
                if temp_info:
                    self.result.append(f'权利要求{idx + 1}可能出了问题, {temp_info}可能存在标号冲突,或错别字')
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
                            self.result.append(f'权利要求{idx + 1}出了问题，在"{error_info}", 可能部件名称或标号错误')
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
                                    self.result.append(f'可能出现错误引用，关键词{array_parts[aidx]}，可能的正确引用方式为：权利要求{idx + 1}引用——>权利要求{sidx}')
                        special_part.append([array_parts[aidx], idx + 1])
                        pass
            elif not list(array_parts):
                # 暂不考虑 这种情况是引用时没有增加部件
                pass
        pass

    # @staticmethod
    def split_str(self, string):
        str_lis = string.split('。')
        # print(str_lis)
        if str_lis[-1].strip():
            self.result.append('最后一项权利要求没有以句号结尾')
        for idx, s in enumerate(str_lis):
            # 不能为空
            if not str_lis[idx].strip():
                str_lis.pop(idx)
                continue
            if not s.strip()[0].isdigit():
                self.result.append(f'权利要求{idx}出了问题， 可能是存在多个句号, 在"{str_lis[idx - 1][-5:]}"后面')
                err = str_lis.pop(idx)
                str_lis[idx - 1] += err
            if f"{idx + 2}．" in str_lis[idx] or f"{idx + 2}." in str_lis[idx]:
                try:
                    err_idx = str_lis[idx].index(f"{idx + 2}．")
                except ValueError:
                    err_idx = str_lis[idx].index(f"{idx + 2}.")
                self.result.append(f'权利要求{idx + 1}出了问题， 可能没有以句号结尾, 在"{str_lis[idx][err_idx - 6:err_idx - 1]}"后面')
                err = str_lis.pop(idx)
                str1, str2 = err[:err_idx], err[err_idx:]
                str_lis.insert(idx, str1)
                str_lis.insert(idx + 1, str2)
        return str_lis

    @staticmethod
    def get_words(string):
        return list(jieba.cut(string, use_paddle=False))
        pass

    @staticmethod
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
                while word[idx + 1 + temp_idx] not in ['）', ')']:
                    nums += word[idx + 1 + temp_idx]
                    temp_idx += 1
                ######################################
                # 测试，到底是两个词好还是一个词好 基本是两个词好 增加停用词，增加正确率
                ######################################
                with open(r'D:\Downloads\flask_project-master\process\stop_dict.txt', encoding='utf-8') as f:
                    stop_word = f.read().split('\n')
                    stop_word.append('\n')
                # print(stop_word)
                if word[idx - 2] in stop_word:
                    parts.append((word[idx - 1], nums))
                # elif not word[idx - 1]:
                #     parts.append((word[idx - 3] + word[idx - 2], nums))
                else:
                    parts.append((word[idx - 2] + word[idx - 1], nums))
        return parts


class Manual:
    """
    说明书
    """
    def __init__(self, string):
        self.result = []
        self.string = string
        # 获得每个部分的字符串，好进行下一步行动
        self.part1, self.part2, self.part3, self.part4, self.part5, self.part6 = self.get_manual_part(string)
        # 说明书附图长度
        self.manual_map_len = len(set(re.findall('图\s?([0-9]+)', self.part4, re.S)))

    def get_manual_part(self, manual_txt):
        assert manual_txt, '说明书内容为空'
        try:
            parts = re.findall('技术领域\W(.*?)背景技术\W(.*?。).*?内容\W(.*?)附图说明\W(.*?)具体实施(例|方式)\W(.*)', manual_txt, re.S)
        except IndexError as e:
            # 错误信息
            error_info = '说明书中小节名称错误，请确认说书中以下小节名称[技术领域][背景技术][?内容][附图说明][具体实施?]'
            self.result.append(error_info)
            raise ValueError(error_info)
        return parts[0]


class Map:
    """
    图有关
    """
    def __init__(self, map_string, img_lis=None):
        # 获得附图长度
        self.result = []
        self.map_len = len(self.get_map_lis(map_string))

    @staticmethod
    def get_map_lis(map_string):
        maps_lis = re.findall('图(.*)', map_string)
        return maps_lis


class Rule:
    """
    准则，规则，即特定词汇表以及常用规则
    """
    def __init__(self, summary, claim, manual, map, all_part):
        # 放回错误
        self.result = []
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
                            if attr:
                                para1 = para1.__dict__[attr]
                            else:
                                attr = 'string'
                                para1 = para1.__dict__[attr]
                            # 结合
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
        try:
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
                                self.result.append(f'{temp[operator[-1]]}{idx+1}出了问题{result}')
                        pass
                    elif 'len' in operator[-1]:
                        temp = dict([(value, key) for key, value in self.attr.items()])
                        result = operator[0](operator[1], operator[2], operator[4])
                        if result:
                            self.result.append(f'{temp[operator[-1]]}出了问题, {result}')
                        pass
                    else:
                        result = operator[0](operator[1], operator[2])
                        if result:
                            self.result.append(f'{operator[3]}{result}')
                            pass
            # 非规则表上的规则
            if not self.part['说明书'].manual_map_len == self.part['图'].map_len:
                self.result.append(f'说明书附图与附图不相同')
            self.part['权利要求书'].check()
            return True
        except:
            return False

    @staticmethod  # 必有 其中之一 简化函数用法，使其变得更通用
    def must_have(obj_sting, word_lis, mod=None):
        temp = []
        for string in word_lis:
            if obj_sting.find(string) != -1:
                temp.append(temp)
        if not temp:
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
        if len(temp) != 1 and temp:
            return f'存在互斥词{temp}'


def pdf_string_get(pdf, ip='127.0.0.1.txt'):
    # 收集数据
    data = f'datasets\{ip}'
    file_write = open(data, 'w', encoding='utf-8')
    pages = pdf.pages
    parts = defaultdict(str)
    for p in pages:
        text = p.extract_text()
        file_write.write(text)
        split_txt = text.split('\n')
        # 通过页眉拆分字符串
        if split_txt[0] == '说 明 书 摘 要':
            string = '\n'.join(split_txt[1:-1])
            parts['abstract'] += string
            parts['all'] += string
        elif split_txt[0] == '摘 要 附 图':
            string = '\n'.join(split_txt[1:-1])
            parts['m1'] += string
        elif split_txt[0] == '权 利 要 求 书':
            string = '\n'.join(split_txt[1:-1])
            parts['claim'] += string
            parts['all'] += string
        elif split_txt[0] == '说 明 书':
            string = '\n'.join(split_txt[1:-1])
            parts['instructions'] += string
            parts['all'] += string
        elif split_txt[0] == '说 明 书 附 图':
            string = '\n'.join(split_txt[1:-1])
            parts['ms'] += string + '\n'
    file_write.close()
    return parts

