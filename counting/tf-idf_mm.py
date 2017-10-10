names1 = (open('chapt_names.txt', 'r', encoding='utf-8')).read().split('\n')
g = 1
names = []
for name in names1:
    names.append('Глава ' + str(g) + '. ' + name)
    g += 1
names[-1] = 'Эпилог'
print(names)