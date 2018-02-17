# -*- coding: utf-8 -*-
import re

f = open('./urls.txt', 'r')

known = 0
unknown = 0
all = 0
before_2000 = 0
after_2000 = 0
for line in f:
    sp = line.split("=>")
    find = 0
    year = ""
    if (len(sp) == 2):
        line_num = sp[0].split(",")
        for el in line_num:
            year = str(el)

            if (find == 0):
                if (re.findall(r'\d\d\d\d[-]\d\d\d\d', year)):
                    year_sp = year.split("-")
                    if (int(str(year_sp[0])) < 2018):
                        known += 1
                        find = 1
                        if (int(str(year_sp[0])) < 2000):
                            before_2000 += 1
                        else:
                            after_2000 += 1
            if (find == 0):
                if (re.findall(r'\d\d\d\d', year)):
                    if (int(str(year)) < 2018):
                        known += 1
                        find = 1
                        if (int(str(year)) < 2000):
                            before_2000 += 1
                        else:
                            after_2000 += 1
            if (find == 0):
                if (re.findall(r'\d\d[-]\d\d', year)):
                    known += 1
                    find = 1
                    before_2000 += 1

    all += 1

    if (find == 0):
        unknown += 1

    if (year != ""):
        print year

print "Все товары:", all
print "С неизвестным годом:", unknown
print "С известным годом:", known
print " До 2000-го года:", before_2000
print " После 2000-го года включительно:", after_2000


