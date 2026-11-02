import json, random, sys
random.seed(7)
edge = ["", "61", "ff", "c0af", "e282", "e282ac", "eda080", "f09f9880", "f09f98", "f4908080", "f5", "c2", "80", "e0809f", "efbfbd", "edbfbf", "f0908080", "dfbf", "e0a080", "ee8080"]
cases = list(edge)
for _ in range(20000):
    n = random.randint(1, 12)
    pool = [random.choice([random.randint(0, 0x7f), random.randint(0x80, 0xff), random.choice([0xc2,0xdf,0xe0,0xed,0xef,0xf0,0xf4,0xf5,0x80,0xbf,0x9f,0xa0])]) for _ in range(n)]
    cases.append(bytes(pool).hex())
json.dump(cases, open(sys.argv[1], "w"))
json.dump([[ord(c) for c in bytes.fromhex(h).decode("utf-8", "surrogateescape")] for h in cases], open(sys.argv[2], "w"))
