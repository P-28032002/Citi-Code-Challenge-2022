import pickle


def read_pickle():
    dbfile = open(r'../map.pkl', 'rb')
    data = pickle.load(dbfile)
    dbfile.close()
    return data


data = read_pickle()
print(type(list(data.keys())[0]))

print(data[('AAXJ', 'DIA')])

