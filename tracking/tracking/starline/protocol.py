# https://help.starline.ru/ru/protokol-obmena-dlya-mayakov-starline-m15-m17-24053340.html#id-%D0%9F%D1%80%D0%BE%D1%82%D0%BE%D0%BA%D0%BE%D0%BB%D0%BE%D0%B1%D0%BC%D0%B5%D0%BD%D0%B0%D0%B4%D0%BB%D1%8F%D0%BC%D0%B0%D1%8F%D0%BA%D0%BE%D0%B2StarLineM15/M17-%D0%9F%D0%B0%D0%BA%D0%B5%D1%82%D0%B7%D0%B0%D0%BF%D1%80%D0%BE%D1%81%D0%B0%D0%B0%D0%B2%D1%82%D0%BE%D1%80%D0%B8%D0%B7%D0%B0%D1%86%D0%B8%D0%B8%D1%83%D1%81%D1%82%D1%80%D0%BE%D0%B9%D1%81%D1%82%D0%B2%D0%BE%D0%BC

from datetime import datetime


def split_every_n(line, n):
    return [line[i:i + n] for i in range(0, len(line), n)]

def parse_ide(dec):
    imei = ''.join(str(hex(x)[2:].zfill(2)) for x in dec[0:8]).strip('0')
    dev_bin = bin(dec[8])[2:].zfill(8)
    dev_arr = list(map(lambda x: str(int(x, 2)), split_every_n(dev_bin, 4)))
    dev_type = dev_arr[0]
    hw_ver = dev_arr[1]
    sw_ver = dec[9]
    phone = ''.join(str(hex(x)[2:].zfill(2)) for x in dec[10:15]).strip('0')
    code = ''.join(str(hex(x)[2:].zfill(2)) for x in dec[15:17]).strip('0')
    return {
        'imei': imei,
        'phone': phone,
        'code': code,
        'dev_type': dev_type,
        'hw_ver': hw_ver,
        'sw_ver': sw_ver
    }


def parse_stat(dec): #14 byte
    # print(len(dec))
    bat = int(bin(dec[0])[2:].zfill(8)[:-1], 2)
    power = bat == 100
    return {
        'CID': str(hex(dec[-2])[2:].rjust(2, '0') + hex(dec[-1])[2:].rjust(2, '0')),
        'LAC': str(hex(dec[-4])[2:].rjust(2, '0') + hex(dec[-3])[2:].rjust(2, '0')),
        'GPRSInterval': dec[7],
        'MCC': str(dec[8]).rjust(3, '0'),
        'MNC': str(dec[9]).rjust(2, '0'),
        'Temp': dec[4],
        'Bat': bat,
        'Power': power,
    }


def minutes_to_degree(degree, minutes):
    minutes_arr = minutes.split('.')
    minutes = minutes_arr[0]
    return float(int(degree))+float('%s.%s' % (minutes, minutes_arr[1]))/60.0


def parse_coord(dec, lat=False): #1 byte degree 3 bytes
    # bin(dec[8])[2:].zfill(8)
    # print(dec)
    # dec = [0x6c, 0x29, 0x61]
    # dec = [0x0f, 0x26, 0xb0]
    # print(bin(dec[1])[2:].zfill(8), bin(dec[2])[2:].zfill(8))
    # print(dec)
    degree = int(dec[0])
    l_arr = bin(dec[3])[2:].zfill(8)
    h = str(int(bin(dec[1])[2:].zfill(8) + bin(dec[2])[2:].zfill(8) + l_arr[:-4], 2))

    # minutes = str(int(coord_bin[:-4], 2))  # 0–59 59 99 минуты и доли минут

    sides = ['W', 'E']
    if lat:
        sides = ['S', 'N']
    side = int(l_arr[-1:], 2)
    minus = ''
    if side == 0:
        minus = '-'
    minutes = f'{h[:-4]}.{h[-4:]}'
    return {
        'min': minutes,
        'side': sides[side],
        'coords': minus + str(minutes_to_degree(degree, minutes))
    }

def parse_time(dec): # 3 bytes hhmmss or hmmss
    time_str = str(int(bin(dec[0])[2:].zfill(8) + bin(dec[1])[2:].zfill(8) + bin(dec[2])[2:].zfill(8), 2))
    return {
        'second': int(time_str[4:]),
        'minute': int(time_str[2:4]),
        'hour': int(time_str[:-4])
    }

def parse_date(dec): # 3 bytes ddmmyy or dmmyy
    date_str = str(int(bin(dec[0])[2:].zfill(8) + bin(dec[1])[2:].zfill(8) + bin(dec[2])[2:].zfill(8), 2))
    return {
        'year': int(date_str[4:]),
        'month': int(date_str[2:4]),
        'day': int(date_str[:-4]),
    }

def get_status(state):
    result = 'No gps data'
    if state == 1:
        result = 'Black box'
    elif state == 2:
        result = 'Real coordinates'
    return result

def parse_gps(dec):
    # print(len(dec), dec)
    gps_status_bin = bin(dec[0])[2:].zfill(8)
    gps_status = get_status(int(gps_status_bin[:2].zfill(8), 2))
    sat_quantity = int(gps_status_bin[2:].zfill(8), 2)
    time_dict = parse_time(dec[1:4])
    date_dict = parse_date(dec[4:7])
    return {
        'gps_status': gps_status,
        'sat_quantity': sat_quantity,
        'date': datetime(
            year=2000+date_dict['year'],
            month=date_dict['month'],
            day=date_dict['day'],
            hour=time_dict['hour'],
            minute=time_dict['minute'],
            second=time_dict['second']
        ).strftime('%s'),
        'lat': parse_coord(dec[7:11], True),
        'long': parse_coord(dec[11:15]),
        'velocity': dec[15]*1.852,
        'course': int(bin(dec[16])[2:].zfill(8) + bin(dec[17])[2:].zfill(8), 2)
    }


def parse_work(dec): # without type(first) and crc (last)
    result = {}
    result.update(parse_stat(dec[:14]))
    result.update(parse_gps(dec[14:]))
    return result


if __name__ == '__main__':
    data = b'A\x03S\x170iU$6A"\x98\x11H\x89\x81\x125\x05'
    dec = [item for item in bytearray(data)]
    # bin_dec = [bin(item)[2:].zfill(8) for item in dec]
    ide = parse_ide(dec[1:18])
    print(ide)

    # print(dec[10], ' ', bin_dec[10])
    data = b'\x02\x00\xff\xff\x1c\x18HG<\xfa\x01\x00\xcc1/\x85\x02y\xac\x02Jj;~@\x01\x1e7!\x91\x00\x00\xab\xe2'
    data = b'\x02\x00\xff\xff\x1b\x18HG<\xfa\x01\x00\xcc12\x85\x02\xd4\xb0\x02Jj;~@\x01\x1e7!\x91\x00\x00\xab\x96'
    data = b'\x02\x00\xff\xff\x1a\x18HG<\xfa\x01\x00\xcc1/\x82\x01:t\x02qz;~J\xb1\x1e7\x1da\x00\x01?\x82\x02\x00\xff\xff\x1a\x18HG<\xfa\x01\x00\xcc1/\x82\x01:\xd8\x02qz;~J\xb1\x1e7\x1da\x00\x01?*\x02\x00\xff\xff\x1a\x18HG<\xfa\x01\x00\xcc1/\x82\x01;<\x02qz;~J\xb1\x1e7\x1da\x00\x01?\x12\x02\x00\xff\xff\x1a\x18HG<\xfa\x01\x00\xcc1/\x82\x01;\xa0\x02qz;~J\xb1\x1e7\x1da\x00\x01?\xaa'
    dec = [item for item in bytearray(data)]
    # bin_dec = [bin(item)[2:].zfill(8) for item in dec]
    result = parse_work(dec[1:33]) # 0-type, 33-crc
    print(result)
