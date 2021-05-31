import functools
import traceback


# 修饰器 bug捕捉 尝试
def error_decorator(LOGGER):
    def wap_error_check(func):
        @functools.wraps(func)
        def wap(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except BaseException as e:
                # 错误信息
                error_info = traceback.format_exc()
                # # 错误函数名
                # fun_name = func.__name__
                # # 错误函数所在文件名
                # fun_filename = func.__code__.co_filename
                # # 错误函数所在行号
                # fun_line_on = func.__code__.co_firstlineno
                # print(error_info)
                # LOGGER().info('以下为程序错误记录')
                LOGGER().error(error_info)
        return wap
    return wap_error_check
