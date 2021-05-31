# ====================================================
# 数据相关
# ====================================================


# 获得当天星期数
def get_weekday():
    from datetime import datetime
    week_day = datetime.now().weekday()
    if week_day > 5:
        return 5
    return week_day


if __name__ == '__main__':
    print(get_weekday())
    pass
