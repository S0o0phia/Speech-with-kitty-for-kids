def getChars():
    chars = []

    with open ('./k_chars.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:
            line = line.replace('\n', '')
            temp = line.split(' ')
            for chr in temp:
                chars.append(chr)

    return chars