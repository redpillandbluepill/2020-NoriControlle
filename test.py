if __name__ == '__main__':
    """
    num = int(input('문제: '))
    if num < 100:
        print('정답:', num)
    else:
        count = 99
        for i in range(100, num + 1):
            i = str(i)
            hundred = int(i[0])
            ten = int(i[1])
            one = int(i[2])
            if hundred - ten == ten - one:
                print(hundred, ten, one)
                count += 1
        print('정답:', count)
    """
    a = [1, 2, 3, 4]
    b = a.copy()
    b[0] = 2
    print(b)
    print(a)





