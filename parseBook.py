import re, sys
import opencc

def strQ2B(ustring):
    rstring = ""
    for uchar in ustring:
        inside_code=ord(uchar)
        if inside_code == 12288:                                       
            inside_code = 32 
        elif (inside_code >= 0xff10 and inside_code <= 0xff19) or (inside_code >= 0xff21 and inside_code <= 0xff3a) or ((inside_code >= 0xff41 and inside_code <= 0xff5a)):
            inside_code -= 65248
        rstring += chr(inside_code)
    return rstring

def main():
    converter = opencc.OpenCC('t2s.json')
    book = sys.argv[1]
    with open(book, "rb") as f:
        data = f.read()
        text = data.decode('utf-8',errors='ignore')
        # RE = re.compile(u'[⺀-⺙⺛-⻳⼀-⿕々〇〡-〩〸-〺〻㐀-䶵一-鿃豈-鶴侮-頻並-龎|，|。]', re.UNICODE)
        RE = re.compile('[\u4e00-\u9fff|\u3001-\u303F|\uff01-\uff5d|\u2160-\u217F|\u203B|\u30FB|\u2027|\u25a0|\u2500|\uff5e|\u2026\u25c6|\u2460-\u2487]', re.UNICODE)
        chinese = RE.findall(text)
        tcscript = ''.join(chinese)
        sc = converter.convert(tcscript)
        sc = strQ2B(sc)
        with open(book+".txt", "a+", encoding="utf-8") as f1:
            f1.write(sc)
            f1.write('\n\n')

if __name__ == '__main__':
    main()

#週周，馀余，鑑鉴，佈布，鬆松，係系，恆恒，盃杯，製制，儘尽，麽么，曆历，囖咯