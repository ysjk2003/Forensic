FILENAME = 'kernel32_dll.txt'
txt = open(FILENAME, 'r')
data_list = []
while True:
    data = txt.readline().split()
    if not data: break
    data_list.append(data)

search = list(input())
search_ord = [ord(a) for a in search]