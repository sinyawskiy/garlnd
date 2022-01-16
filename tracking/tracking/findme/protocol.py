import datetime

AUTH_PACKET = 0x10
WORK_PACKET = 0x11
BLACK_BOX_PACKET = 0x12


def crc(dec):
    r = 0x3B
    for d in dec[:-1]:
        r += 0x56 ^ d
        r += 1
        r ^= 0xC5 + d
        r -= 1
    return int(hex(r)[-2:], 16) == dec[-1] and True or False

# def print_byte(dec):
#     print(dec, bin(dec), bin(dec)[2:].zfill(8), int(bin(dec)[2:].zfill(8)[:4], 2), int(bin(dec)[2:].zfill(8)[4:], 2))

def get_parameters(dec):
    def parameter_int(int_dec):
        return str(int(int_dec, 2))
    # print(dec)
    result = ['0']*18+['*']*(25-18)
    bin_dec = [bin(item)[2:].zfill(8) for item in dec]
    result[0] = bin_dec[0][-8]  #7 - режим работы маяка
    result[1] = bin_dec[0][-7]  #6 - язык интерфейса
    result[6] = bin_dec[0][-6]  #5 - наличие AGPs
    result[18] = bin_dec[0][-5]  #4 - наличие черного ящика
    result[2] = parameter_int(bin_dec[0][4:])  #0-3 - время ожидания смс после регистрации GSM модуля в минутах
    result[3] = parameter_int(bin_dec[1][:4])  # 4-7 - время ожидания смс после выполнения всех режимов будильников или после корректной команды перед уходом в сон в минутах (от 2 до 9)
    result[4] = parameter_int(bin_dec[1][4:])  # 0-3 - максимальное время аудиоконтроля в минутах (от 1 до 9)
    result[5] = parameter_int(bin_dec[2][:4])  # 4-7 - максимальное время поиска спутников в минутах (от 1 до 9)
    result[7] = parameter_int(bin_dec[2][4:])  # 0-3 - тип смс режима G (от 0 до 9)
    result[8] = parameter_int(bin_dec[3][:4])  # 0-3 - реакция на подбор пароля (0 – нет реакции, от 1 до 9 – количество подряд смс с неправильным паролем и корректным содержанием)
    result[17] = bin_dec[3][-4]  # 3 - отсылка смс с координатами после срабатывания любого ТРЕВОЖНОГО события (НЕ УВЕДОМЛЕНИЯ) (0 - нет, 1 - есть)
    result[9] = bin_dec[3][-3]  # 2 - наличие смс-уведомления о разряде батареи (0 - нет, 1 - есть)
    # print(bin_dec[3][-2], bin_dec[3][-1])  # 0 - ?
    result[10] = parameter_int(bin_dec[4][:4])  # 4-7 - внешнее питание (0 - нет реакции, 1 - тревога при вкл., 2 - тревога при вЫкл., 3 - тревога при вкл. и вЫкл., 4 - онлайн при вкл., 5 - онлайн при вкл. + уведомление при вкл., 6 - онлайн при вкл. + уведомление при вЫкл., 7 - онлайн при вкл. + уведомление при вкл. и вЫкл.)
    result[11] = parameter_int(bin_dec[4][4:6])  # 2-3 - внешний вход (0 - нет реакции, 1 - тревога при активации (замыкание на "массу"), 2 - онлайн при активации, 3 - онлайн при активации + уведомление)
    result[12] = parameter_int(bin_dec[4][6:])  # 0-1 - режим работы кнопки (0 - нет реакции, 1 - тревога при нажатии, 2 - онлайн при нажатии, 3 - онлайн при нажатии + уведомление)
    result[13] = parameter_int(bin_dec[5][:4])  # 4-7 - акселерометр (0-выключен, 1 - фиксация движения, 2 - "удержание на парковке", 3 - фиксация движения + "удержание на парковке", 4 - фиксация поворота, 5 - фиксация удара, 6 - фиксация падения (временно недоступно))
    result[14] = parameter_int(bin_dec[5][4:6])  # 2-3 - акселерометр (0 - нет действий, 1 - тревога при событии, 2 - онлайн при событии, 3 - онлайн при событии + уведомление
    # print(bin_dec[5][-2], bin_dec[5][-1])
    result[15] = parameter_int(bin_dec[6][:4])  # 4-7 - акселерометр: чувствительность (от 1(мин) до 9(макс))
    result[16] = parameter_int(bin_dec[6][4:])  # 0-3 - акселерометр: время непрерывного покоя для начала фиксации начала движения (от 1 до 9, минуты x10)
    return ''.join(result)


def convert_work(dec):
    print([hex(item) for item in dec])
    ## status 11
    # 0 bit -1
    # 1 bit -2
    # 2 bit -3
    status_bin = bin(dec[10])[2:].zfill(8)
    print('Status', status_bin)
    power = status_bin[-4] == '0' and 'no' or 'yes'  # 0 - bit
    motion = status_bin[-3] == '0' and 'no' or 'yes'  # 3 - bit
    packForFixCoord = status_bin[-7] == '1' and 'yes' or 'no'  # 6 - bit
    realGPSData = status_bin[-8] == '0' and 'yes' or 'no'  # 7 - bit

    #parameters 3 - 10
    parameters_bin = get_parameters(dec[2:10])

    print('Parameters', parameters_bin)

    rtcTime = datetime.datetime(
        dec[16] + 2000,  # год
        dec[15],  # месяц
        dec[14],  # день
        dec[17],  # час
        dec[18],  # мин.
        dec[19]  # сек.
    ).strftime('%s')



    ## battery Volt
    battery = dec[13]*0.05

    ## temperature C.
    oCtemp = dec[44]

    ## GSM -dB
    GSMdB = dec[45]

    ## GPS status
    gpsStatus = int(bin(dec[54])[2:][0:2], 2) # 6-7 - bit
    gpsValid = (gpsStatus==2 and 'yes' or 'no')
    gpsSputnikQuan, gpsTime, gpsLat, gpsLong = 0, 0, 0.0000, 0.0000
    if gpsValid=='yes' and dec[57]!=0 and dec[56]!=0 and dec[55]!=0:
        gpsSputnikQuan = int(bin(dec[54])[2:][2:8], 2) # 0-5 - bit

        gpsTime = datetime.datetime(
            dec[57]+2000, # год
            dec[56], # месяц
            dec[55], # день
            dec[58], # час
            dec[59], # мин.
            dec[60]  # сек.
        ).strftime('%s')

        gpsLat = int( hex(dec[61])[2:].zfill(2) + hex(dec[62])[2:].zfill(2) + hex(dec[63])[2:].zfill(2) + hex(dec[64])[2:].zfill(2) , 16)
        gpsLatMinus = (bin(gpsLat)[2:][0]=='0' and '-' or '') # bits[0] - bit is set => north
        gpsLat = gpsLatMinus+str(gpsLat)[0:2]+'.'+str(float( str(gpsLat)[2:4]+'.'+str(gpsLat)[4:] )/60)[2:6] # convert DD MM.MMMM => DD (MM.MMMM)/60 => DD.DDDD

        gpsLong = int( hex(dec[65])[2:].zfill(2) + hex(dec[66])[2:].zfill(2) + hex(dec[67])[2:].zfill(2) + hex(dec[68])[2:].zfill(2) , 16)
        gpsLongMinus = (bin(gpsLong)[2:][0]=='0' and '-' or '') # bits[0] - bit is set => east
        gpsLong = gpsLongMinus+str(gpsLong)[0:2]+'.'+str(float( str(gpsLong)[2:4]+'.'+str(gpsLong)[4:] )/60)[2:6] # convert DD MM.MMMM => DD (MM.MMMM)/60 => DD.DDDD
    else:
        gpsValid = 'no'

    ## GPS altitude meter
    gpsAltMeter = dec[69]+dec[70]

    ## GPS speed km/h
    gpsSpeedKm = dec[71]*1.852  # 1 uzel = 1.852 km

    ## GPS rate degrees
    gpsRateDegrees = dec[72]*2

    ## GPS HDOP - Снижение точности в горизонтальной плоскости.
    gpsHDOP = float(dec[73]+dec[74])/10

    return [{
        'rtcTime': rtcTime,
        'battery': battery,
        'GSMdB': GSMdB,
        'oCtemp': oCtemp,
        'power': power,
        'motion': motion,
        'gpsValid': gpsValid,
        'gpsSputnikQuan': gpsSputnikQuan,
        'gpsTime': gpsTime,
        'gpsLat': gpsLat,
        'gpsLong': gpsLong,
        'gpsAltMeter': gpsAltMeter,
        'gpsSpeedKm': gpsSpeedKm,
        'gpsRateDegrees': gpsRateDegrees,
        'gpsHDOP': gpsHDOP
    }]


def convert_black_box(dec):
    result = []

    packAll = dec[1]
    packValid = int(bin(dec[1])[2:].zfill(8)[4:8], 2)  # 0-4 - bits
    print([hex(item) for item in dec])
    #print('+ all in black box packed: '+str(packAll)+' / at this pack valid: '+str(packValid))

    for i in range(packValid):
        if i == 0:
            offsetByte = 4  # first block
        else:
            offsetByte += 42  # next block

        # more security
        if offsetByte+2 > len(dec):
            break

        ## status
        status_bin = bin(dec[1+offsetByte])[2:].zfill(8)

        power = status_bin[-1]=='0' and 'no' or 'yes' # 0 - bit
        motion = status_bin[-4]=='0' and 'no' or 'yes' # 3 - bit
        packForFixCoord = status_bin[-7]=='1' and 'yes' or 'no' # 6 - bit
        realGPSData = status_bin[-8]=='0' and 'yes' or 'no' # 7 - bit

        ## battery Volt
        battery = dec[1+offsetByte]*0.05

        rtcTime = None
        try:
            rtcTime = datetime.datetime(
                dec[4 + offsetByte] + 2000,  # год
                dec[3 + offsetByte],  # месяц
                dec[2 + offsetByte],  # день
                dec[5 + offsetByte],  # час
                dec[6 + offsetByte],  # мин.
                dec[7 + offsetByte]  # сек.
            ).strftime('%s')
        except Exception:
            pass

        ## temperature C.
        oCtemp = dec[8+offsetByte]

        ## GSM -dB
        GSMdB = dec[9+offsetByte]

        ## GPS status
        gpsStatus = int(bin(dec[18+offsetByte])[2:][0:2], 2) # 6-7 - bit
        gpsValid = (gpsStatus in [1, 2, 3] and 'yes' or 'no')
        gpsSputnikQuan, gpsTime, gpsLat, gpsLong = 0, 0, 0.0000, 0.0000
        if gpsValid=='yes' and dec[21+offsetByte]!=0 and dec[20+offsetByte]!=0 and dec[19+offsetByte]!=0:
            gpsSputnikQuan = int(bin(dec[18+offsetByte])[2:][2:8], 2) # 0-5 - bit

            gpsTime = datetime.datetime(
                dec[21+offsetByte]+2000, # год
                dec[20+offsetByte], # месяц
                dec[19+offsetByte], # день
                dec[22+offsetByte], # час
                dec[23+offsetByte], # мин.
                dec[24+offsetByte]  # сек.
            ).strftime('%s')

            gpsLat = int( hex(dec[25+offsetByte])[2:].zfill(2) + hex(dec[26+offsetByte])[2:].zfill(2) + hex(dec[27+offsetByte])[2:].zfill(2) + hex(dec[28+offsetByte])[2:] , 16)
            gpsLatMinus = (bin(gpsLat)[2:][0]=='0' and '-' or '') # bits[0] - bit is set => north
            gpsLat = gpsLatMinus+str(gpsLat)[0:2]+'.'+str(float( str(gpsLat)[2:4]+'.'+str(gpsLat)[4:] )/60)[2:6] # convert DD MM.MMMM => DD (MM.MMMM)/60 => DD.DDDD

            gpsLong = int( hex(dec[29+offsetByte])[2:].zfill(2) + hex(dec[30+offsetByte])[2:].zfill(2) + hex(dec[31+offsetByte])[2:].zfill(2) + hex(dec[32+offsetByte])[2:] , 16)
            gpsLongMinus = (bin(gpsLong)[2:][0]=='0' and '-' or '') # bits[0] - bit is set => east
            gpsLong = gpsLongMinus+str(gpsLong)[0:2]+'.'+str(float( str(gpsLong)[2:4]+'.'+str(gpsLong)[4:] )/60)[2:6] # convert DD MM.MMMM => DD (MM.MMMM)/60 => DD.DDDD
        else:
            gpsValid = 'no'


        ## GPS altitude meter
        gpsAltMeter = dec[33+offsetByte]+dec[34+offsetByte]

        ## GPS speed km/h
        gpsSpeedKm = dec[35+offsetByte]*1.852 # 1 uzel = 1.852 km

        ## GPS rate degrees
        gpsRateDegrees = dec[36+offsetByte]*2

        ## GPS HDOP - Снижение точности в горизонтальной плоскости.
        gpsHDOP = float(dec[37+offsetByte]+dec[38+offsetByte])/10

        block = {
            'battery': battery,
            'rtcTime': rtcTime,
            'GSMdB': GSMdB,
            'oCtemp': oCtemp,
            'power': power,
            'motion': motion,
            'gpsValid': gpsValid,
            'gpsSputnikQuan': gpsSputnikQuan,
            'gpsTime': gpsTime,
            'gpsLat': gpsLat,
            'gpsLong': gpsLong,
            'gpsAltMeter': gpsAltMeter,
            'gpsSpeedKm': gpsSpeedKm,
            'gpsRateDegrees': gpsRateDegrees,
            'gpsHDOP': gpsHDOP
        }
        result.append(block)

    return result

