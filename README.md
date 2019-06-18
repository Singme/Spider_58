# Spider_58
This is a crawler that solves font encryption.
## 用selenium爬取58同城租房信息  

* 58同城，反反爬技术，采用**网站字体加密**技术

通过查看页面，可以发现字体是被加密的：
> <b class="strongbox">龒龒驋閏</b>  
> .strongbox {
    font-family: 'fangchan-secret','Hiragino Sans GB','Microsoft yahei',Arial,sans-serif,'宋体'!important;
}  

通过分析，定点查到***fangchan-secret***，查看网页源码发现这边采用的是base64加密方式，加密字符串是"AAEAAA...AAAAAAAA"  
点击下一页，再网页源码对比发现，两次的加密字符串不相同，所以可以肯定的是，js动态加密字体。  
#### 解决字体加密的方式

* 1.用正则匹配获取加密字符串
```
driver.get("https://sz.zu.anjuke.com/")  # 发送请求    
html = driver.page_source  # 获取网页源代码  
pattern = re.compile(r"'.*;base64,(.*?)'")  # 正则匹配  
ret_list = pattern.findall(html)  
```  
* 2.解析获取关系映射表  
```
# 将base64编码的字体字符串解码成二进制编码
binData = base64.decodebytes(ret_list[0].encode())
with open('anjuke.otf', 'wb') as f:
	f.write(binData)
# ByteIO 把一个二进制内存块生成文件来操作
font = TTFont(BytesIO(bin_data))
# 将编码字体保存为xml
font.saveXML('anjuke.xml')
# 取出字符和码值对应的关系映射表
utfList = font['cmap'].tables[0].ttFont.tables['cmap'].tables[0].cmap  
# utfList = {38006: 'glyph00010', 38287: 'glyph00006', 39228: 'glyph00001', 39499: 'glyph00009', 40506: 'glyph00008', 40611: 'glyph00003', 40804: 'glyph00007', 40850: 'glyph00004', 40868: 'glyph00002', 40869: 'glyph00005'}
```  
* 3.根据关系表找出对应的值  
```
retList = []
getText2 = '龒龒驋閏'
for i in getText2:  # 遍历取出每个字符
	if ord(i) in utfList:  # ord() 将字符转为对应的ASCII值
		text = int(utfList[ord(i)][-2:]) - 1
	else:
		text = i
	retList.append(text)
crackText = ''.join([str(i) for i in retList])
```  
字体加密是一种很有效的反爬技术，58同城的例子值得参考。

