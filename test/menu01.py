menu_str = " 서귀포 어묵탕 17,900 | 도새기 고추장볶음 18,900 | 낚지볶음 15,900 | 뼈없는 매운닭발 14,900 "
menus = menu_str.split('|')

for m in menus :
    m = m.strip()
    m_arr = m.rsplit(' ', 1)
    print (m_arr)
