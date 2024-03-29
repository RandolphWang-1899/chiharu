from nonebot import on_command, CommandSession, get_bot, permission, plugin, command
import nonebot
import importlib
import chiharu.plugins.config as config
from os import path

_dict = {"asc": "使用格式：\n-asc check str：转换str的所有字符到ascii码\n-asc trans numbers：转换数字到字符",
    "mbf": "使用格式：-mbf.run instructions \\n console_in\n\n脚本语言modified brainf**k帮助：\n有一个由整数组成的堆栈。从左到右依次读取instruction。堆栈为空时欲取出任何数均为0。\n.\t向堆栈中塞入一个0\n0-9\t堆栈顶数乘以10加输入数。即比如输入一个十进制数135可以使用.135\n+-*/%\t弹出堆栈顶两个数并塞入计算后的数。除法取整数除\n&|^\t按位运算\n><=\t比较栈顶两个数，true视为1，false视为0\n_\t栈顶数取负，即比如输入一个数-120可以使用.120_\n!\t0变为1，非0变为0\n(\t栈顶数+1\n)\t栈顶数-1\n:\t输入stdin的char至栈顶\n;\t输出栈顶的char至stdout，并消耗，超出范围则弹出后不做任何事\n[\t如果堆栈顶数为0则跳转至配对的]，并消耗掉栈顶数\n{\t与[相反，堆栈顶数非0则跳转至配对的}，并消耗掉栈顶数\n]\t如果堆栈顶数非0则跳转回匹配的[，并消耗掉栈顶数\n}\t与]相反，堆栈顶数为0则跳转回配对的{，并消耗掉栈顶数\n\\\t交换栈顶两数\n,\t弹出栈顶数n，并复制栈顶下数第n个数塞回栈顶，n超出范围则弹出n后不做任何事\n$\t塞入当前栈包含的整数总数\n~\tpop掉栈顶数\n\"\t弹出栈顶数n，删除栈顶下数第n个数，n超出范围则弹出n后不做任何事\n@\t弹出栈顶数n1之后n2，将输入序列的第n1个字符修改成n2对应的char，n1或n2超出范围则弹出两数后不做任何事\n?\t弹出栈顶数n，生成一个0至n-1的随机整数塞回堆栈，n非正则弹出n后不做任何事\n#\t复制栈顶数\n`\t弹出栈顶数，执行栈顶数对应的char对应的指令。超出范围则弹出后不做任何事\n'\t弹出栈顶数n，将输入序列第n个字符对应的ascii塞入堆栈\n字母为子程序，使用：\n-mbf.sub alpha string 存入子程序，大写字母的只可存入一次。\n-mbf.str Alpha string 可以给大写字母增加一条描述字符串。\n-mbf.check alpha 查询字母所存内容。\n-mbf.ls 列出所有子程序以及描述\n-mbf.time ins stdin 检查运行时间\n",
    #"eclins": "使用格式：-eclins ins_num\n检索ecl的ins。",
    "birth": "使用格式：-birth.today bandori或LL或imas：查询今天生日的角色",
    "seiyuu": "使用格式：\n-seiyuu.today：查询今天生日的声优列表\n-seiyuu.check seiyuu_name[, count]：返回声优的基本信息，找到多个时可以使用count指明第几个。声优名以日语原文键入，允许假名甚至罗马音。\n-seiyuu.list string[, bound=15]：查询包含string的声优名列表，超过bound时返回前bound个，顺序未指定",
    "game": "欢迎使用-game 指令访问七海千春游戏大厅~",
    "tools": "-tools.Julia [c的x坐标] [c的y坐标]：绘制Julia集\n-tools.oeis：查询oeis（整数序列在线百科全书），支持查询数列前几项（只返回第一个结果），或oeis的编号如A036057",
    "misc": "-misc.asc.check str：转换str的所有字符到ascii码\n-misc.asc.trans numbers：转换数字到字符\n-misc.bandori.news：查询bandori新闻\n-misc.maj.ten：日麻算点器\n-misc.maj.train：麻将训练\n-misc.maj.ting：听牌计算器\n-misc.maj.voice：雀魂报番语音，第一行番种，换行后为指定角色名\n-misc.token：将输入文本中大括号包含的token转换成latex中包含的unicode字符，使用https://github.com/joom/latex-unicoder.vim/blob/master/autoload/unicoder.vim, https://pastebin.com/jxHsjQK0\n  例：-misc.token f(0)={\\aleph}_0,f({\\alpha}+1)={\\aleph}_{\\alpha}\n-misc.latex：渲染latex公式\n-misc.money：面基算钱小助手 请单独-help misc.money\n-misc.roll.lyric：随机抽歌词，默认从全歌单中抽取，支持参数：vocalo kon imas ml cgss sphere aki bandori ll mu's Aqours starlight mh\n-event year month day [max_note=100]：按日期在eventernote.com查询该日发生的event，筛选条件为eventernote登录数大于max_note，默认为100，调低时请一定要注意避免刷屏！",
    "misc.money": "每行为一条指令。指令：\nclear: 清除所有数据。\nadd [人名]: 增加一个人。\nbill [人名] [金额] [可选：需付费的人名列表]: 增加一个需付费账单，人名列表为空则默认【包括自己的】所有人。\noutput [策略] [参数]: 输出金额交换。策略目前有：\n\toneman [参数：人名]: 所有金额交换全部支付给此人/由此人支付。",
    #"event": "使用格式：\n-event year month day [max_note = 100]：按日期在eventernote.com查询该日发生的event，筛选条件为eventernote登录数大于max_note，默认为100，调低时请一定要注意避免刷屏！",
    "thwiki": "使用格式：-thwiki.list：显示五天以内的预定直播列表，使用-thwiki.list all查询全部\n-thwiki.check：查询thbwiki bilibili账户的直播状态\n-thwiki.time 可以@别人 查看自己或别人的直播总时长（2019年8月至今）\n-thwiki.timezone UTC时区 调整自己的时区，只支持整数时区。影响list与apply\n-thwiki.timezone 空或者@别人 查询时区信息\n-thwiki.leaderboard 查看直播排行榜",
    "code": "脚本语言解释器：\nmbf：modified brainf**k\nesulang\n使用如-mbf.run 指令 运行脚本\n使用如-help mbf查看语言解释",
    "esulang": "还在开发中，敬请期待！~",
    "card": """指令列表：-card.draw 卡池id/名字 抽卡次数 可以抽卡！！次数不填默认为单抽
-card.draw5 卡池id/名字 直接进行五连抽卡
-card.check 卡池id/名字 查询卡池具体信息，包含具体卡牌（刷屏预警，建议私聊~）
-card.check 不带参数 查询卡池列表与介绍
-card.check_card 卡片名 查询卡片余量
-card.add 卡片名字 张数 就可以创造卡片加入卡池 张数不填默认为1张 可以换行后加描述文本
-card.add_des 卡片名字 换行后写描述文本 为自己首次创造的卡牌增加描述文本，会在单抽时显示
-card.userinfo 查看个人信息，包含en数，剩余免费抽卡次数等等
-card.storage 查看库存卡片
-card.discard 卡片名 数量 分解卡片获得en，张数不填默认为1张
-card.wishlist 查看愿望单
-card.message 手动查看消息箱
-card.set.属性 改变用户设置，可以使用-help card.set查询可以改变的设置
-card.fav 卡片名 将卡片加入特别喜欢
-card.wish 卡片名 将卡片加入愿望单
-card.comment 给维护者留言~想说的话，想更新的功能，想开启的活动卡池都可以哦~""",
    "card.set": """-card.set.unconfirm 取消今日确认使用en抽卡
-card.set.message 参数 设置消息箱提醒，支持参数：-card.set.message 0：立即私聊
-card.set.message 1：手动收取
-card.set.message 2：凌晨定时发送私聊
-card.set.guide on或off：开启或关闭全部指令引导。指令引导会在使用一次该指令后自动关闭""",
    "me": "こんにちは～七海千春です～\n维护者：小大圣\n鸣谢：Python®  酷Q®  nonebot®  阿里云®",
    "default": "指令："
        #"\n-eclins：查询ecl的instruction"
        "\n-seiyuu：查询声优信息"
        "\n-game：\U0001F6AA七海千春游戏大厅\U0001F6AA"
        "\n-tools：数理小工具"
        "\n-code：语言解释器"
        #"\n-event：按日期查询event"
        "\n-misc：隐藏指令"
        "\n-help：展示本帮助\n-help 指令名：查看该命令帮助\n例：-help tools：查看tools指令的帮助\n欢迎加入测试群947279366避免刷屏"}

sp = {"thwiki_live": {"default": "%s\n-thwiki：thwiki直播申请相关",
    "thwiki": """%s
-thwiki.apply [开始时间] [结束时间] [直播项目名称]或者-申请 [开始时间] [结束时间] [直播项目名称]；时间格式：x年x月x日x点x分或者xx:xx，今日或今年可以省，开始可以用now，结束可以用float
例：-thwiki.apply 19:00 21:00 东方STG
-thwiki.cancel [直播项目名称或id]或者-取消 [直播项目名称或id]
-thwiki.get 获取rtmp与流密码，会以私聊形式发送，若直播间未开启则会自动开启，可以后跟想开启的直播分区如绘画，演奏，户外，vtb等，不指定则默认是单机·其他
-thwiki.change 更改当前直播标题，只可在自己直播时间段内，同样会修改列表里的名字
-thwiki.term 提前下播
-thwiki.grant @别人 可多个@ 可加false 推荐别人进入推荐列表，请慎重推荐！结尾加false代表撤回推荐，撤回推荐会一同撤回被推荐人推荐的所有人
apply cancel get term grant change只能用于群内"""},
    "thwiki_supervise": {"thwiki": """%s
-thwiki.deprive @别人 剥夺别人的推荐/转正，管理员在直播群使用
-thwiki.supervise id号 可加false 监视别人的直播申请，结尾加false代表撤回监视
-thwiki.grantlist 输出推荐树"""}}

@on_command('code', only_to_me=False)
@config.ErrorHandle
async def help_code(session: CommandSession):
    await command.call_command(get_bot(), session.ctx, 'help', current_arg='code')

@on_command(name='help', only_to_me=False)
@config.ErrorHandle
async def help(session: CommandSession):
    global _dict, sp
    name = session.get('name')
    try:
        group_id = session.ctx['group_id']
    except KeyError:
        group_id = 0
    def _f():
        for key, val in sp.items():
            if group_id in config.group_id_dict[key] and name in val:
                yield val[name]
    str_tail = ''.join(_f())
    if name in _dict:
        if str_tail != "":
            strout = str_tail % _dict[name]
        else:
            strout = _dict[name]
    else:
        strout = str_tail
    if name == 'thwiki' and str_tail != '' and group_id in config.group_id_dict['thwiki_live']:
        await session.send(strout, auto_escape=True, ensure_private=True)
    else:
        await session.send(strout, auto_escape=True)

@help.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    if stripped_arg:
        session.args['name'] = stripped_arg
    else:
        session.args['name'] = 'default'

@on_command('reload', only_to_me=False)
@config.ErrorHandle
async def reload_plugin(session: CommandSession):
    name = 'chiharu.plugins.' + session.current_arg_text
    l = list(filter(lambda x: x.module.__name__ == name, plugin._plugins))
    print(list(map(lambda x: x.module.__name__, plugin._plugins)))
    if len(l) == 0:
        await session.send('no plugin named ' + session.current_arg_text, auto_escape=True)
    else:
        l[0].module = importlib.reload(l[0].module)
        await session.send('Successfully reloaded ' + session.current_arg_text, auto_escape=True)