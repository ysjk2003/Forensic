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
    mode = int(input("메뉴 선택 : \n 0.종료 \n 1.파일 경로 \n 2.섹터 정보 \n 3.파티션 정보 \n 4.FAT32 정보 \n"))

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
        hex_data = ["%02x" % b for b in data[446:510]]
        finish = True
        i = 0
        j = 0
        int_lba = 0
        partition = []
        select_lba = 0
        lba_list = []
        print("partition 정보\n")
        while finish:
            if not partition:
                partition.append(hex_data[i*16:i*16+16])
            else:
                partition.append(hex_data[i*16:i*16+16])
                if partition[j][4] == '05':
                    partition.remove(partition[j])
                    start_lba = hex_data[i*16+8:i*16+12]
                    start_lba.reverse()
                    if int_lba == 0:
                        int_lba = int("".join(start_lba), 16)
                        mbr.seek(int_lba*512, 0)
                        lba_list.append(int_lba)
                    else:
                        select_lba = int_lba + int("".join(start_lba), 16)
                        mbr.seek(select_lba*512, 0)
                        lba_list.append(select_lba)
                    data = mbr.read(512)
                    hex_data = ["%02x" % b for b in data[446:510]]
                    i = 0
                    partition.append(hex_data[i*16:i*16+16])
                else:
                    if ''.join(partition[j][0:16]) == '00000000000000000000000000000000':
                        finish = False
                        partition.remove(partition[j])
                        break
            i = i + 1
            j = j + 1
        for i in range(0, len(partition)):
            print("partition ["+str(i+1)+"]", *partition[i][0:16])
            print("Boot Flag", int(partition[i][0]))
            CHS_start = partition[i][1:4]
            CHS_start.reverse()
            print("CHS start", ''.join(CHS_start))
            print("type", partition[i][4])
            CHS_end = partition[i][5:8]
            CHS_end.reverse()
            print("CHS end", ''.join(CHS_end))
            if i < 3:
                LBA_start = partition[i][8:12]
                LBA_start.reverse()
                LBA_start = int(''.join(LBA_start), 16)
            else:
                LBA_start = partition[i][8:12]
                LBA_start.reverse()
                LBA_start = lba_list[i-3] + int(''.join(LBA_start), 16)
            print("LBA start", LBA_start)
            print("size", int(''.join(reversed(partition[i][12:16])), 16) // 2 // 1024)
            print("\n")
    elif mode == 4:
        pass
    elif mode == 0:
        sys.exit()
    else:
        print("잘못된 메뉴 입력입니다.")