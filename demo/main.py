import re
# 这里的string是说明书中，附图说明中的文字

def remove_null(string):
    return re.sub(re.compile(r'\W'), '', string)


def get_ins_parts(string):
    res = re.findall('图.*?[：|:](.*)', string, re.S)
    res_dic = {}
    if res:
        # 标号似乎只能有阿拉伯数字，所以是能够使用的
        res = re.findall(r'(\d+)(\D+)|(\D+)(\d+)', remove_null(res[0]))
        # 统一转换成同一个格式
        print(res)
        for item in res:
            if item[0] and item[1]:
                res_dic[item[1]] = item[0]
            elif item[2] and item[3]:
                res_dic[item[2]] = item[3]
            else:
                print('有待考察')
        # 检查是否出现错误
        if len(set(res_dic.values())) != len(res_dic):
            print('标号中只能使用阿拉伯数字, 但是在标号中发现非数字，这可能会使得后续检测出现问题')
    return res_dic


print(get_ins_parts(string))

