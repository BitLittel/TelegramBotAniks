from database import Session, Citys

db = Session()

with open('city.txt', 'r', encoding='utf-8') as file:
    i = 0
    for line in file:
        if i % 6 == 0:
            print(line.replace('\n', '').replace(' ', '').upper())
            new_city = Citys(name_city=line.replace('\n', '').replace(' ', '').upper())
            db.add(new_city)
        i += 1
    db.commit()
