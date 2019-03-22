import os
import sys
import string

string.ascii_letters

FILE_NAME = ''

def openFile():
    if FILE_NAME == '':
        print("파일 열기를 먼저 실행해 주세요")
    else:
        mbr = open(FILE_NAME, 'rb')
        return mbr

while True:
    mode = int(input("메뉴 선택 : \n 0.종료 \n 1.파일 경로 \n 2.섹터 정보 \n 3.파티션 정보 \n"))

    if mode == 1:
        FILE_NAME = input("파일 경로 입력 \n")
    elif mode == 2:
        mbr = openFile()
        size = os.path.getsize(FILE_NAME)
        while True:
            position = int(input(f"섹터 위치 [0 ~ {size//512 - 1}] -1을 입력하면 상위 메뉴로 이동 > "))
            if position == -1:
                break
            else:
                mbr.seek(position*512, 0)
                print("offset(h)  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F")
                print("==========================================================")
                for line in range(32):
                    data = mbr.read(16)
                    hex_data = ["%02X" % b for b in data]
                    character_data = [chr(i) if chr(i) in string.printable[:-5] else '.' for i in data]
                    print("%08X  " % ((line * 16) + position*512), *hex_data, "".join(character_data))
    elif mode == 3:
        mbr = openFile()
        data = mbr.read(512)
        hex_data = ["%02x" % b for b in data]
        
        print("partition [1]", *hex_data[446:462])
        print("partition [2]", *hex_data[462:478])
        print("partition [3]", *hex_data[478:494])
        print("partition [4]", *hex_data[494:510])
        
        start_lba = hex_data[502:506]
        start_lba.reverse()
        intlba = int("".join(start_lba), 16)
        mbr.seek(intlba*512, 0)
        data = mbr.read(512)
        hex_data = ["%02x" % b for b in data]
        
        print("partition [5]", *hex_data[446:462])
        print("partition [6]", *hex_data[462:478])

        print(*hex_data[454:458])
        
    elif mode == 0:
        sys.exit()
    else:
        print("잘못된 메뉴 입력입니다.")