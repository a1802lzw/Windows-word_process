# 文档转换文件
import os
from win32com import client as wc


wps = wc.DispatchEx('kwps.Application')
#新建wps文字
# mywps = wps.Documents.Add()
doc = wps.Documents.Open(r'C:\Users\Administrator\Desktop\workspace\word_pre\一种平衡车用的锥形定位装置.doc')
# 调用word程序
wps.Visible = 0
wps.DisplayAlerts = 0
doc.SaveAs(r'C:\Users\Administrator\Desktop\workspace\word_pre\一种平衡车用的锥形定位装置.pdf', 17)
doc.Close()
wps.Quit()
