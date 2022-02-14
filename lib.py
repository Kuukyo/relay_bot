import json
import discord
import os
from shutil import copyfile


def load_mem(x):
    file = open(x, "r", encoding="utf-8")
    memory = json.load(file)
    file.close()

    return memory


def dump_mem(x, y):
    file = open(y, "w", encoding="utf-8")
    json.dump(x, file, ensure_ascii=False, indent="\n")
    file.close()


def backup():
    memory = load_mem("memory.json")
    file = open("memory_backup.json", "w", encoding="utf8")
    dump_mem(memory, "memory_backup.json")
    file.close()


def load_backup():
    copyfile("memory_backup.json", "memory.json")


def load_data():
    i = 0
    b = {}
    memory = load_mem("memory.json")
    for t in memory:
        i += 1
        b[i] = memory[t]
    dump_mem(b, "memory.json")

    return i


def getID(tag):
    userid = tag.replace("<", "").replace(">", "").replace("@", "")
    if "!" in userid:
        userid = userid.replace("!", "")

    return int(userid)


def getUser(ctx, user):
    userid = user.replace("<", "").replace(">", "").replace("@", "")
    if "!" in userid:
        userid = int(userid.replace("!", ""))
    user = None
    for x in ctx.message.guild.members:
        if x.id == userid:
            user = x

    return user


def listToString(list):
    str = ""
    for i in list:
        str += i + " "
    str = str[:-1]
    return str

def read_file(file):
    file = open(file, "r", encoding="utf8")
    x = file.read().split("\n")
    file.close()

    return x


def append_file(content, file):
    old_content = read_file(file)
    str = ""
    for i in old_content:
        if i == "":
            str += i
        else:
            str += i + "\n"
    str += content + "\n"
    file = open(file, "w", encoding="utf8")
    file.write(str)
    file.close()


def overwrite_file(list, file):
    str = ""
    for i in list:
        str += i + "\n"
    file = open(file, "w", encoding="utf8")
    file.write(str)
    file.close()
