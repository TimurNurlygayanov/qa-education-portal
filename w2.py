A = [{"a": 4534234234234, "b": "34fb,flg,sld,b"}, {"a": 324234, "b": "gfldf,gdlfg,df"},]

prev = {}

for i in A:
    if i['a']<prev.get('a'):
        i['a'], prev['a'] = prev['a'], i['a']
        prev = i

print A
