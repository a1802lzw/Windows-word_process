# 测试ocr windows环境缺失
# from paddleocr import PaddleOCR, draw_ocr
# # Paddleocr目前支持中英文、英文、法语、德语、韩语、日语，可以通过修改lang参数进行切换
# # 参数依次为`ch`, `en`, `french`, `german`, `korean`, `japan`。
# ocr = PaddleOCR(use_angle_cls=True, lang="ch") # need to run only once to download and load model into memory
# img_path = r'C:\Users\Administrator\Desktop\workspace\flask_project-master\
#                 tmp\一种可控刹车顺序的自行车阀门系统_html_8a443ca75352fb76.gif'
# result = ocr.ocr(img_path, cls=True)
# for line in result:
#     print(line)
#
# # 显示结果
# from PIL import Image
# image = Image.open(img_path).convert('RGB')
# boxes = [line[0] for line in result]
# txts = [line[1][0] for line in result]
# scores = [line[1][1] for line in result]
# im_show = draw_ocr(image, boxes, txts, scores, font_path='/path/to/PaddleOCR/doc/fonts/simfang.ttf')
# im_show = Image.fromarray(im_show)
# im_show.save('result.jpg')
