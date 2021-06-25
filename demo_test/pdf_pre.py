# 测试文件
from PyPDF2 import PdfFileReader
readFile = r'一种防泄漏化学品储藏罐-缪仁杰.pdf'
with open(readFile, 'rb') as readFile:
    # 调用PdfFileReader函数
    pdf_document = PdfFileReader(readFile)

    # 使用PdfFileReader对象的变量，获取各个信息，如numPages属性获取PDF文档的页数
    print(pdf_document.numPages)

    # 调用PdfFileReader对象的getPage()方法，传入页码，取得Page对象：输出PDF文档的第一页内容
    first_page = pdf_document.getPage(0)

    # 调用Page对象的extractText()方法，返回该页文本的字符串
    text = first_page.extractText()
    print(type(text))
