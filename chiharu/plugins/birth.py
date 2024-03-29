# coding=utf-8
from collections import UserDict
from string import Formatter
import requests
import re
import json
import datetime
import asyncio
import chiharu.plugins.config as config
from nonebot import on_command, CommandSession, CommandGroup, scheduler, get_bot

seiyuu = CommandGroup('seiyuu', only_to_me=False)

@seiyuu.command('today')
@config.ErrorHandle
async def GetSeiyuuToday(session: CommandSession):
    strout = await _GetSeiyuuToday()
    await session.send(strout, auto_escape=True)

@seiyuu.command('check')
@config.ErrorHandle
async def CheckSeiyuu(session: CommandSession):
    name = session.get('name')
    count = session.get('count')
    loop = asyncio.get_event_loop()
    url = await loop.run_in_executor(None, requests.get, "https://sakuhindb.com/anime/search.asp?S_iC=%E6%96%87%E5%AD%97&ocs=euc&key=" + name + "&todo=%E6%83%85%E5%A0%B1DB")
    seiyuu = url.text.encode(url.encoding).decode("utf-8")
    pos = re.search("検索時間", seiyuu).span()[1]
    match = re.search("<a href\\=\"(https://sakuhindb.com/tj/[A-Za-z0-9_]*/)\">", seiyuu[pos:])
    if match:
        if re.search("<a href\\=\"(https://sakuhindb.com/tj/[A-Za-z0-9_]*/)\">((?!CV|Cv).)*?</a>", seiyuu[pos + match.span()[1]:]):
            if count == -1:
                await session.send("Too Many!")
                return
        if count != -1:
            match = re.search("<hr />" + str(count) + "\\.\\s*<a href\\=\"(https://sakuhindb.com/tj/[A-Za-z0-9_]*/)\">.*?</a>", seiyuu[pos:])
        url = await loop.run_in_executor(None, requests.get, match.group(1))
        seiyuu_this = url.text.encode(url.encoding).decode("utf-8")
        begin_pos = re.search("<b>総合</b>", seiyuu_this).span()[1]
        end_pos = re.search("階位", seiyuu_this).span()[0]
        liststr = []
        while 1:
            match = re.search("<td class\\=\"leftmenu\">(.*?)</td>", seiyuu_this[begin_pos:end_pos], re.S)
            if match and not match.group(1).startswith("作成者") and not match.group(1).startswith("最終変更者"):
                match2 = re.search("<td>(.*?)</td>", seiyuu_this[begin_pos + match.span()[1]:end_pos], re.S)
                str1 = match.group(1) + "\t"
                match3 = re.search("<a href\\=\"(.*?)\" target\\=_blank>(.*?)</a>", match2.group(1), re.S)
                if match3:
                    if "サイト" in match.group(1):
                        str1 += match3.group(1)
                    else:
                        str1 += match3.group(2)
                else:
                    str2 = re.sub("<a href\\=\"(.*?)\">(.*?)</a>", "\\2", match2.group(1), re.S)
                    str2 = str2.replace("</b>", "").replace("<b>", "").replace("<br>", "\n").replace("\n\n", "\n").replace("</span>", "").replace("<span class=\"no_exist_attr\">", "")
                    str1 += str2
                liststr.append(str1)
                begin_pos += match.span()[1] + match2.span()[1]
            else:
                break
        await session.send("\n".join(liststr), auto_escape=True)
    else:
        await session.send("Not Found!")

@seiyuu.command('list')
@config.ErrorHandle
async def ListSeiyuu(session: CommandSession):
    name = session.get('name')
    count = session.get('count')
    loop = asyncio.get_event_loop()
    url = await loop.run_in_executor(None, requests.get, "https://sakuhindb.com/anime/search.asp?S_iC=%E6%96%87%E5%AD%97&ocs=euc&key=" + name + "&todo=%E6%83%85%E5%A0%B1DB")
    seiyuu = url.text.encode(url.encoding).decode("utf-8")
    begin_pos = re.search("検索時間", seiyuu).span()[1]
    list_seiyuu = []
    while 1:
        match = re.search("<hr />(\\d+\\.)\\s*<a href\\=\"https://sakuhindb.com/tj/[A-Za-z0-9_]*/\">(.*?)</a>", seiyuu[begin_pos:])
        if match:
            list_seiyuu.append(match.group(1) + "\t" + re.sub("<.*?>", "", match.group(2)))
            begin_pos += match.span()[1]
        else:
            break
    if count == -1 and len(list_seiyuu) > 15:
        await session.send("Too Many! These are first 15:\n" + "\n".join(list_seiyuu[0:15]), auto_escape=True)
    elif count != -1 and len(list_seiyuu) > count:
        await session.send("Too Many! These are first %s:\n" % count + "\n".join(list_seiyuu[0:count]), auto_escape=True)
    elif len(list_seiyuu) == 0:
        await session.send("Not Found!")
    else:
        await session.send("\n".join(list_seiyuu), auto_escape=True)

@CheckSeiyuu.args_parser
@ListSeiyuu.args_parser
async def _(session: CommandSession):
    t = list(map(lambda x: x.strip(), session.current_arg_text.split(',')))
    session.args['name'] = t[0]
    if len(t) == 1:
        session.args['count'] = -1
    else:
        session.args['count'] = int(t[1])

@on_command(('birth', 'today'), only_to_me=False)
@config.ErrorHandle
async def BirthToday(session: CommandSession):
    which = session.current_arg_text.strip()
    dictout = _GetBirth(which)
    if len(dictout[which]) != 0:
        await session.send("今天是：\n%s的生日\nお誕生日おめでとう~" % u"，\n".join(dictout[which]), auto_escape=True)
    else:
        await session.send("今天没有%s的角色过生日哦~" % which, auto_escape=True)

@scheduler.scheduled_job('cron', hour='23', minute='01')
async def DailySeiyuu():
    bot = get_bot()
    strout = await _GetSeiyuuToday()
    for id in config.group_id_dict['seiyuu']:
        await bot.send_group_msg(group_id=id, message=strout)

@scheduler.scheduled_job('cron', hour='23', minute='01')
async def DailyBirth():
    bot = get_bot()
    l = ['imas', 'lovelive', 'bandori']
    dictout = _GetBirth(*l)
    for s in l:
        if len(dictout[s]) != 0:
            for group_id in config.group_id_dict[s]:
                await bot.send_group_msg(group_id=group_id, message="今天是：\n%s的生日\nお誕生日おめでとう~" % u"，\n".join(dictout[s]))

class myFormatter(Formatter):
    def parse(self, format_string):
        literal_text, field_name = '', ''
        field_depth = 0
        for t in format_string:
            if t == '{':
                if field_depth != 0:
                    field_name += t
                field_depth += 1
            elif t == '}':
                if field_depth == 0:
                    raise KeyError(format_string)
                field_depth -= 1
                if field_depth == 0:
                    yield (literal_text, field_name, '', None)
                    literal_text, field_name = '', ''
                else:
                    field_name += t
            else:
                if field_depth == 0:
                    literal_text += t
                else:
                    field_name += t
        if field_name == '' and literal_text != '':
            yield (literal_text, None, None, None)

class Birth(UserDict):
    def __getitem__(self, key):
        try:
            if '/' in key:
                keyl = key.split('/')
                try:
                    if self.__getitem__(keyl[0]) == "":
                        return ""
                except KeyError:
                    return ""
                key = '/'.join(keyl[1:])
        except:
            pass
        try:
            if '{' in key and '}' in key:
                return myFormatter().vformat(key, (), self)
                #return key.format_map(self)
        except:
            pass
        if key in self.data:
            return self.data[key]
        if '@zh' in key:
            return ""
        raise KeyError(key)
    def __getattr__(self, attr):
        return self.data[attr]

def _GetBirth(*args):
    with open(config.rel("birth.json"), encoding='utf-8') as birth_file:
        birth = json.load(birth_file)
    today = datetime.datetime.now()
    today += datetime.timedelta(hours=1)
    month = str(today.month)
    day = str(today.day)
    f = myFormatter()
    dict_ret = {}
    for group in args:
        dict_ret[group] = []
    if day in birth[month]:
        for obj2 in birth[month][day]:
            obj = Birth(obj2)
            if obj.group in args:
                if obj.group == "bandori":
                    dict_ret["bandori"].append(f.vformat(
                        '{band}的{part}{name}{name@zh/（{name@zh}）}'
                        '【CV：{cv}{cv@zh/（{cv@zh}）}】'
                        #.format_map(obj))
                        , (), obj))
                elif obj.group == "lovelive":
                    dict_ret["lovelive"].append(f.vformat(
                        '{team/{team}的成员，}{school}{grade}年生{name}{name@zh/（{name@zh}）}'
                        '{cv/【CV：{cv}{cv@zh/（{cv@zh}）}】}'
                        #.format_map(obj))
                        , (), obj))
                elif obj.group == "imas":
                    dict_ret["imas"].append(f.vformat(
                        '{office}事务所的{name}{name@zh/（{name@zh}）}'
                        '{cv/【CV：{cv}{cv@zh/（{cv@zh}）}】}'
                        #.format_map(obj))
                        , (), obj))
    return dict_ret

async def _GetSeiyuuToday():
    loop = asyncio.get_event_loop()
    seiyuu_url = await loop.run_in_executor(None, requests.get, 'https://sakuhindb.com/')
    seiyuu = seiyuu_url.text.encode(seiyuu_url.encoding).decode(errors='ignore')
    begin_pos = re.search("本日が誕生日", seiyuu).span()[1]
    end_pos = re.search("論客目録", seiyuu).span()[0]
    seiyuu_list = []
    while 1:
        match = re.search("<a href\\=(/tj/[A-Za-z0-9_]*/)><span class\\=(man|female)>([^<]*)</span></a>\\(([^\\)]*)\\)", seiyuu[begin_pos:end_pos])
        if match:
            if "声優" in match.group(4):
                url = await loop.run_in_executor(None, requests.get, "https://sakuhindb.com" + match.group(1))
                seiyuu_this = url.text.encode(url.encoding).decode("utf-8")
                match2 = re.search("出生国", seiyuu_this)
                if match2:
                    match2_pos = match2.span()[1]
                    seiyuu_kuni = re.search("<td>([^<]*)</td>", seiyuu_this[match2_pos:]).group(1)
                    if seiyuu_kuni == "日本":
                        seiyuu_list.append(("男" if match.group(2) == "man" else "女") + "\t" + match.group(3))
            begin_pos += match.span()[1]
        else:
            break
    return "今天过生日的声优有：\n  %s\nお誕生日おめでとう！" % "\n  ".join(seiyuu_list)
