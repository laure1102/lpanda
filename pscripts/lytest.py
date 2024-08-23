import re  
  
text = """  
奥德赛可家乐福  
啥的房间里  
  
  
算法邻水的  
  
  
  
啥的机房懒得解释  
  
  
  
  
  
阿萨德解放路  
是否  
撒旦法  
  
胜多负少  
""" 

# 使用正则表达式匹配只包含空白字符的行，并将其替换为空字符串  
cleaned_text = re.sub(r'^\s*$\n', '', text, flags=re.MULTILINE)  
  
print(cleaned_text)