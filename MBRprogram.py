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

def partition_Info():
    mbr = openFile()
    data = mbr.read(512)
    hex_data = ["%02x" % b for b in data[446:510]]
    finish = True
    i = j = int_lba = select_lba = 0
    partition = []
    lba_list = []
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
    return partition, lba_list

def fat32_Info():
    partition, lba_list = partition_Info()
    Reversed_Sector_Count = []
    FAT_size = []
    FAT1_start = []
    FAT2_start = []
    Root_Directory_Start = []
    Sector_Per_Cluster = []
    for i in range(0, len(partition)):
        mbr = openFile()
        if partition[i][4] == "0c":
            LBA_start = lba_Start(i)
            
            mbr.seek(LBA_start*512, 0)
            data = mbr.read(512)
            hex_data = ["%02x" % b for b in data]
            
            Reversed_Sector_Count.append(int(''.join(reversed(hex_data[14:16])), 16))
            FAT_size.append(int(''.join(reversed(hex_data[36:40])), 16))
            FAT1_start.append(LBA_start+Reversed_Sector_Count[i])
            FAT2_start.append(FAT1_start[i] + FAT_size[i])
            Root_Directory_Start.append(FAT2_start[i] + FAT_size[i])
            Sector_Per_Cluster.append(int(''.join(hex_data[13])))
    return Reversed_Sector_Count, FAT1_start, FAT2_start, FAT_size, Root_Directory_Start, Sector_Per_Cluster

def lba_Start(i):
    partition, lba_list = partition_Info()
    if i < 3:
        LBA_start = partition[i][8:12]
        LBA_start.reverse()
        LBA_start = int(''.join(LBA_start), 16)
    else:
        LBA_start = partition[i][8:12]
        LBA_start.reverse()
        LBA_start = lba_list[i-3] + int(''.join(LBA_start), 16)
    return LBA_start

def get_Time(byte_array):
    time = "{0:8b}".format(int(''.join(reversed(byte_array[:2])),16))
    if len(time) != 16:
        zero = str(0*(16-len(time)))
        time = zero+time
    time_string = str(int(time[0:5], 2)) + "시" + str(int(time[5:11], 2)) + "분" + str(int(time[11:], 2)*2) + "초"
    return time_string

def get_Date(byte_array):
    date = "{0:8b}".format(int(''.join(reversed(byte_array[:2])), 16))
    if len(date) != 16:
        zero = str(0*(16-len(date)))
        date = zero+date
    date_string = str(int(date[:7], 2)+1980) + "년" + str(int(date[7:11], 2)) + "월" + str(int(date[11:], 2)) + "일"
    return date_string

while True:
    mode = int(input("메뉴 선택 : \n 0.종료 \n 1.파일 경로 \n 2.섹터 정보 \n 3.파티션 정보 \n 4.FAT32 정보 \n 5.파일정보 보기\n"))

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
        partition, lba_list = partition_Info()
        print("partition 정보\n")

        for i in range(0, len(partition)):
            CHS_start = reversed(partition[i][1:4])
            CHS_end = reversed(partition[i][5:8])
            LBA_start = lba_Start(i)

            print("partition ["+str(i+1)+"]", *partition[i][0:16])
            print("Boot Flag", int(partition[i][0]))
            print("CHS start", ''.join(CHS_start))
            print("type", partition[i][4])
            print("CHS end", ''.join(CHS_end))
            print("LBA start", LBA_start)
            print("size", int(''.join(reversed(partition[i][12:16])), 16) // 2 // 1024)
            print("\n")

    elif mode == 4:
        partition, lba_list = partition_Info()
        Reversed_Sector_Count, FAT1_start, FAT2_start, FAT_size, Root_Directory_Start, Sector_Per_Cluster = fat32_Info()
        for i in range(0, len(partition)):
            mbr = openFile()
            if partition[i][4] == "0c":
                LBA_start = lba_Start(i)
                
                mbr.seek(LBA_start*512, 0)
                data = mbr.read(512)
                hex_data = ["%02x" % b for b in data]
                
                print("Partition ["+str(i+1)+"]--------------------")
                print("Byte Per Sector", int(''.join(reversed(hex_data[11:13])), 16))
                print("Sector Per Cluster", Sector_Per_Cluster[i])
                print("Reversed Sector Count", Reversed_Sector_Count[i])
                print("Total sector FAT32", int(''.join(reversed(hex_data[32:36])), 16))
                print("FAT Size 32", FAT_size[i], "\n")
                print("VBR start", LBA_start)
                print("FAT#1 start", FAT1_start[i])
                print("FAT#2 start", FAT2_start[i])
                print("Root Directory Start", Root_Directory_Start[i], "\n")

    elif mode == 5:
        mbr = openFile()
        Reversed_Sector_Count, FAT1_start, FAT2_start, FAT_size, Root_Directory_Start, Sector_Per_Cluster = fat32_Info()
        partition, lba_list = partition_Info()
        j = 1
        for i in Root_Directory_Start:
            mbr.seek(i*512, 0)
            data = mbr.read(512)
            hex_data = ["%02x" % b for b in data]

            print("Partition [", j,"]-----------------")

            for i in range(0, 15):
                file_data = hex_data[i*32:i*32+32]
                if file_data[11] == '08':
                    print("Volum Label")
                    print(" Volum name:", bytes.fromhex(''.join(file_data[0:11])).decode('euc-kr'))
                    print(" Last Written Time:", get_Time(file_data[22:24]))
                    print(" Last Written Date:", get_Date(file_data[24:26]))
                    print("\n")

                elif file_data[11] == '20' or file_data[11] == "16":
                    if file_data[11] == '20':
                        delete = ""
                        if file_data[0] == 'e5':
                            delete = "Delete "
                        print(delete + "Archive")
                    elif file_data[11] == '16':
                        print("Directory")
                    print(" name:", ''.join(list(chr(x) for x in list(int(x, 16) for x in file_data[0:11]))))
                    print(" Create Time:", get_Time(file_data[14:16]))
                    print(" Create Date:", get_Date(file_data[16:18]))
                    print(" Last Written Time:", get_Time(file_data[22:24]))
                    print(" Last Written Date:", get_Date(file_data[24:26]))
                    print(" Last Accessed Date:", get_Date(file_data[18:20]))
                    print(" Size:", int(''.join(reversed(file_data[28:])), 16))
                    print(" 파일 데이터 섹터 위치:", (int(''.join(reversed(file_data[20:22])), 16) + int(''.join(reversed(file_data[26:28])), 16) - 2) * Sector_Per_Cluster[j-1] + Root_Directory_Start[j-1])
                    print("\n")

                elif file_data[11] == '0f':
                    delete = ""
                    if file_data[0] == 'e5':
                        delete = "Delete "
                    print(delete + "Long File Name")
                    print("\n")
            j = j + 1

    elif mode == 0:
        sys.exit()

    else:
        print("잘못된 메뉴 입력입니다.")