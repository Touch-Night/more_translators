import html
import gradio as gr
import translators as ts
import os
import re
import pandas as pd
import yaml
from io import StringIO
from cgitb import text
from modules import shared


i18n_data = pd.read_csv(
    "./extensions/more_translators/i18n.csv", encoding="utf-8", header=0, index_col=0
)


supported_language_map_data = pd.read_csv(
    "./extensions/more_translators/supported_language_map.csv",
    encoding="utf-8",
    header=0,
    index_col=0,
)

# default settings
settings = {
    "activate": True,
    "user lang": "auto",
    "llm lang": "en",
    "i18n lang": "zh-cn",
    "translator string": "alibaba",
    "translate mode": "to-from",  # to-from, to, from
}

"""
Copied from https://github.com/CrazyMayfly/Free-Markdown-Translator
"""

compact_langs = ["中文(台湾)", "中文(香港)", "中文(文言文)", "日语"]
# 指定要跳过翻译的字符的正则表达式，分别为加粗符号、在``中的非中文字符，`，用于过滤表格的符号，换行符
skipped_regexs = [
    r"\*\*。?",
    r"#+",
    r"`[^\u4E00-\u9FFF]*?`",
    r"`",
    r'"[^\u4E00-\u9FFF]*?"',
    r"-+",
    r"\|",
    "\n",
]
# 非紧凑型语言中需要添加分隔的正则表达式
expands_regexs = [
    r"`[^`]+?`",
    r'".*?"',
    r"\*\*.*?\*\*",
    r"!\[.*?\]\(.*?\)",
    r"\[.*?\]\(.*?\)",
]
# pattern = "|".join(map(re.escape, self.skipped_chars))
pattern = "({})".format("|".join(skipped_regexs))
expands_pattern = "({})".format("|".join(expands_regexs))
# markdown中Front Matter不用翻译的部分
front_matter_transparent_keys = (
    "date:",
    "slug:",
    "toc",
    "image",
    "comments",
    "readingTime",
    "menu:",
    "    main:",
    "        weight:",
    "        params:",
    "            icon:",
    "links:",
    "    website:",
    "    image:",
    "layout:",
    "outputs:",
    "    - html",
    "    - json",
    "license:",
    "#",
    "style:",
    "    background:",
    "    color:",
)
# Front Matter中需要以Key-Value形式翻译的部分
front_matter_key_value_keys = (
    "title:",
    "description:",
    "        name:",
    "  - title:",
    "    description:",
)
# Front Matter中以Key-Value—Arrays形式翻译
front_matter_key_value_array_keys = ("tags:", "categories:", "keywords:")


class Node:
    def __init__(self, line):
        # 无需翻译的格式相关内容
        self.signs = ""
        # 需要被翻译的内容
        self.value = ""
        # 开头不需要翻译的内容，如1. , - ,>等
        self.index = ""
        # value的行数，若为0表示无需翻译
        self.trans_lines = 1
        self.line = line
        if re.match(r"\d+\. ", line):
            self.index = line[0:3]
            self.line = line[3:]
        elif line.startswith("- ") or line.startswith("> "):
            self.index = line[0:2]
            self.line = line[2:]

    def get_trans_buff(self):
        # 获取该节点的待翻译内容
        if self.trans_lines:
            return self.value + "\n"
        return None

    def compose(self):
        # 将翻译后的内容组装
        return self.index + self.value


# 内容无需翻译
class TransparentNode(Node):
    def __init__(self, line):
        super().__init__(line)
        self.value = self.line
        self.trans_lines = 0


# 内容全部需翻译
# 比如MD中的正文文本块
class SolidNode(Node):
    def __init__(self, line):
        super().__init__(line)
        self.value = self.line[0:-1]

    def compose(self):
        return self.index + self.signs + self.value + "\n"


# 内容为#key:value形式，value需要翻译
class KeyValueNode(Node):
    def __init__(self, line):
        super().__init__(line)
        idx = self.line.index(":")
        self.signs = self.line[0 : idx + 1]
        self.value = self.line[idx + 1 :].strip()

    def compose(self):
        return self.index + self.signs + " " + self.value + "\n"


# 内容为### Title形式，Title需要翻译
class TitleNode(Node):
    def __init__(self, line):
        super().__init__(line)
        idx = self.line.index(" ")
        self.signs = self.line[0:idx]
        self.value = self.line[idx + 1 : -1]

    def compose(self):
        return self.index + self.signs + " " + self.value + "\n"


# 内容为![图片标题](01.jpg) 形式，图片标题需要翻译
class ImageNode(Node):
    def __init__(self, line):
        super().__init__(line)
        idx1 = self.line.index("[")
        idx2 = self.line.index("]")
        if idx1 == idx2 - 1:
            self.trans_lines = 0
            self.value = self.line
        else:
            lstr = self.line[0 : idx1 + 1]
            mstr = self.line[idx1 + 1 : idx2]
            rstr = self.line[idx2:-1]
            self.value = mstr
            self.signs = []
            self.signs.append(lstr)
            self.signs.append(rstr)

    def compose(self):
        if self.trans_lines == 0:
            return self.value
        return self.index + self.value.join(self.signs) + "\n"


class LinkNode(Node):
    def __init__(self, line):
        super().__init__(line)
        pattern = r"\[.*?\]\(.*?\)"
        p = re.compile(pattern)
        text = p.split(self.line[0:-1])
        links = re.findall(pattern, self.line)
        tips = []
        self.signs = []
        for link in links:
            idx = link.index("]")
            tips.append(link[1:idx])
            self.signs.append(link[idx + 2 : -1])
        self.text_num = len(text)
        self.link_num = len(links)
        self.trans_lines = self.text_num + self.link_num
        self.value = "\n".join(text + tips)

    def compose(self):
        self.value = self.value.split("\n")
        text = self.value[0 : self.text_num]
        tips = self.value[self.text_num :]
        links = []
        for i in range(0, self.link_num):
            link = f"[{tips[i]}]({self.signs[i]})"
            links.append(link)
        results = []
        for i in range(0, self.link_num):
            results.append(text[i])
            results.append(links[i])
        results.append(text[-1])
        return self.index + "".join(results) + "\n"


# 内容为#key:["values1","values2",..."valueN"]形式，value需要翻译
class KeyValueArrayNode(Node):
    def __init__(self, line):
        super().__init__(line)
        idx = self.line.index(":")
        key = self.line[0 : idx + 1]
        self.signs = key
        value = self.line[idx + 1 :].strip()
        if value.startswith("["):
            items = value[2:-2].split('", "')
            if not items:
                items = value[2:-2].split('","')
            self.value = "\n".join(items)
            self.trans_lines = len(items)
        else:
            print("Wrong format with MdTransItemKeyValueArray:", text)

    def compose(self):
        items = self.value.split("\n")
        return self.index + '{} ["{}"]'.format(self.signs, '", "'.join(items)) + "\n"


# Update settings from tranlators_settings.yaml
def load_settings():
    settings_dir = "./extensions/more_translators/translators_settings.yaml"
    if os.path.exists(settings_dir):
        with open(settings_dir, "r") as file:
            settings.update(yaml.load(file, Loader=yaml.FullLoader))
    else:
        print(read_i18n("未找到设置文件translators_settings.yaml，已按默认设置创建。"))
        gr.Warning(
            read_i18n("未找到设置文件translators_settings.yaml，已按默认设置创建。")
        )
    save_settings()


# Save settings to translators_settings.yaml when settings is modified
def save_settings():
    settings_dir = "./extensions/more_translators/translators_settings.yaml"
    # Check if the directory exists, if not, create it
    if not os.path.exists(os.path.dirname(settings_dir)):
        os.makedirs(os.path.dirname(settings_dir))
    # Save settings to translators_settings.yaml
    with open(settings_dir, "w") as file:
        yaml.dump(settings, file)


# Translate from i18n.csv to translator_codes and language_codes
def read_i18n(i18n_value, i18n_lang=None, reverse=False):
    if i18n_lang is None:
        i18n_lang = settings["i18n lang"]
    if not reverse:
        # if i18n_value is a list
        if isinstance(i18n_value, list):
            return [
                read_i18n(i18n_value_item, i18n_lang) for i18n_value_item in i18n_value
            ]
        # if i18n_value is a dict, translate only the values
        elif isinstance(i18n_value, dict):
            return {
                key: read_i18n(value, i18n_lang) for key, value in i18n_value.items()
            }
        else:
            if i18n_value not in i18n_data.index or i18n_lang not in i18n_data.columns:
                return i18n_value
            result = i18n_data.loc[i18n_value, i18n_lang]
            final_result = result.values[0] if isinstance(result, pd.Series) else result
            # print([i18n_value, final_result, i18n_lang])
            return final_result
    else:
        i18n_key = i18n_data.loc[i18n_data[i18n_lang] == i18n_value]
        value = i18n_key.index[0]
        return value


params = {
    "display_name": read_i18n("LLM翻译"),
    "is_tab": True,
}


def value_to_language_code(value, translator):
    if (
        value not in supported_language_map_data.index
        or translator not in supported_language_map_data.columns
    ):
        print(read_i18n("不支持的语言或翻译器"))
        gr.Warning(read_i18n("不支持的语言或翻译器"))
    return supported_language_map_data.loc[value, translator]


def language_code_to_value(language_code, translator):
    supported_languages = supported_language_map_data.loc[
        supported_language_map_data[translator] == language_code
    ]
    value = supported_languages.index[0]
    return value


# print(read_i18n('alibaba', 'en')) -> Alibaba
# print(value_to_language_code('英语', 'deepl')) -> en
# print(language_code_to_value('ar', 'deepl')) -> 阿拉伯语


def get_languages(translator):
    all_languages = supported_language_map_data.dropna(subset=[translator])
    result = dict(zip(all_languages.index, all_languages[translator]))
    return result


def initialize():
    global translator_codes, language_codes
    load_settings()
    language_codes = get_languages(settings["translator string"])
    translator_codes = {
        read_i18n("alibaba"): "alibaba",
        read_i18n("apertium"): "apertium",
        read_i18n("argos"): "argos",
        read_i18n("baidu"): "baidu",
        read_i18n("bing"): "bing",
        read_i18n("caiyun"): "caiyun",
        read_i18n("cloudTranslation"): "cloudTranslation",
        read_i18n("deepl"): "deepl",
        read_i18n("elia"): "elia",
        read_i18n("google"): "google",
        read_i18n("iflyrec"): "iflyrec",
        read_i18n("itranslate"): "itranslate",
        read_i18n("languageWire"): "languageWire",
        read_i18n("lingvanex"): "lingvanex",
        read_i18n("mglip"): "mglip",
        read_i18n("modernMt"): "modernMt",
        read_i18n("papago"): "papago",
        read_i18n("qqFanyi"): "qqFanyi",
        read_i18n("qqTranSmart"): "qqTranSmart",
        read_i18n("reverso"): "reverso",
        read_i18n("sogou"): "sogou",
        read_i18n("translateCom"): "translateCom",
        read_i18n("utibet"): "utibet",
    }


def translate_with_skipped_chars(text, selected_translator, src_lang, dest_lang):
    """
    翻译时忽略在config.py中配置的正则表达式，翻译后保证格式不变
    :param text: 本次翻译的文本
    :return: 翻译后的文本
    """
    parts = re.split(pattern, text)
    # 跳过的部分
    skipped_parts = {}
    # 需要翻译的部分
    translated_parts = {}
    idx = 0
    for part in parts:
        if len(part) == 0:
            continue
        is_translated = True
        for skipped_char in skipped_regexs:
            if re.match(skipped_char, part):  # 原封不动地添加跳过的字符
                skipped_parts.update({idx: part})
                is_translated = False
                break
        if is_translated:
            translated_parts.update({idx: part})
        idx += 1
    # 组装翻译
    text = "\n".join(translated_parts.values())
    translate = ts.translate_text(
        html.unescape(text),
        translator=selected_translator,
        from_language=src_lang,
        to_language=dest_lang,
    )
    # 确保api接口返回了结果
    while translate is None:
        translate = ts.translate_text(
            html.unescape(text),
            translator=selected_translator,
            from_language=src_lang,
            to_language=dest_lang,
        )
    translated_text = translate.split("\n")
    idx1 = 0
    # 更新翻译部分的内容
    for key in translated_parts.keys():
        translated_parts[key] = translated_text[idx1]
        idx1 += 1
    total_parts = {}
    total_parts.update(skipped_parts)
    total_parts.update(translated_parts)
    translated_text = ""
    # 拼接回字符串
    for i in range(0, idx):
        translated_text += total_parts[i]
    splitlines = translated_text.splitlines()[1:-1]
    translated_text = "\n".join(splitlines) + "\n"
    return translated_text


def generate_nodes(src_lines):
    """
    扫描每行，依次为每行生成节点
    """
    is_front_matter = False
    # 在```包裹的代码块中
    is_code_block = False
    # 忽略翻译的部分，实际上和代码块内容差不多，只是连标识符都忽略了
    do_not_trans = False
    nodes = []
    for line in src_lines:
        if line.strip() == "---":
            is_front_matter = not is_front_matter
            nodes.append(TransparentNode(line))
            continue
        if line.startswith("```"):
            is_code_block = not is_code_block
            nodes.append(TransparentNode(line))
            continue
        if line.startswith("__do_not_translate__"):
            do_not_trans = not do_not_trans
            continue
        if is_front_matter:
            if line.startswith(front_matter_key_value_keys):
                nodes.append(KeyValueNode(line))
            elif line.startswith(front_matter_transparent_keys):
                nodes.append(TransparentNode(line))
            elif line.startswith(front_matter_key_value_array_keys):
                nodes.append(KeyValueArrayNode(line))
            else:
                nodes.append(SolidNode(line))
        elif is_code_block or do_not_trans:
            nodes.append(TransparentNode(line))
        else:
            if len(line.strip()) == 0 or line.startswith(("<audio", "<img ")):  # 空行
                nodes.append(TransparentNode(line))
            elif re.search("!\[.*?\]\(.*?\)", line) is not None:  # 图片
                nodes.append(ImageNode(line))
            elif re.search("\[.*?\]\(.*?\)", line) is not None:
                nodes.append(LinkNode(line))
            elif line.strip().startswith("#"):  # 标题
                nodes.append(TitleNode(line))
            else:  # 普通文字
                nodes.append(SolidNode(line))
    return nodes


def translate_in_batches(lines, translator, src_lang, dest_lang):
    """
    分批次翻译
    """
    # 需在头尾添加字符以保证Google Translate Api不会把空行去除
    tmp = "BEGIN\n"
    translated_text = ""
    for line in lines:
        tmp = tmp + line + "\n"
        # 控制每次发送的数据量
        if len(tmp) > 500:
            tmp += "END"
            translated_text += translate_with_skipped_chars(
                tmp, translator, src_lang, dest_lang
            )
            tmp = "BEGIN\n"
    if len(tmp) > 0:
        tmp += "END"
        translated_text += translate_with_skipped_chars(
            tmp, translator, src_lang, dest_lang
        )
    return translated_text


def translate_lines(src_lines, translator, src_lang, dest_lang):
    # 文本拆分翻译组装

    nodes = generate_nodes(src_lines)
    # 待翻译md文本
    src_md_text = ""
    for node in nodes:
        trans_buff = node.get_trans_buff()
        if trans_buff:
            src_md_text += trans_buff
    src_lines = src_md_text.splitlines()
    translated_text = translate_in_batches(src_lines, translator, src_lang, dest_lang)
    translated_lines = translated_text.splitlines()
    start_pos = 0
    for node in nodes:
        node_trans_lines = node.trans_lines
        if node_trans_lines == 0:
            continue
        elif node_trans_lines == 1:
            node.value = translated_lines[start_pos]
            start_pos += 1
        else:
            node.value = "\n".join(
                translated_lines[start_pos : start_pos + node_trans_lines]
            )
            start_pos += node_trans_lines
    final_markdown = ""
    for node in nodes:
        final_markdown += node.compose()
    return final_markdown


def modify_string(string, selected_translator, source, target, with_error_string=False):
    # 预处理
    string_io = StringIO(string)
    string_lines = string_io.readlines()
    if (
        language_code_to_value(source, selected_translator) != "中文(台湾)"
        or "中文(香港)"
    ):
        string_lines_tmp = []
        for line in string_lines:
            line = line.replace("。", ". ").replace("，", ",")
            string_lines_tmp.append(line)
        string_lines = string_lines_tmp
    string_lines.append("\n")
    final_md_text = translate_lines(string_lines, selected_translator, source, target)
    final_markdown = ""
    for line in final_md_text.splitlines():
        if language_code_to_value(target, selected_translator) not in compact_langs:
            parts = re.split(expands_pattern, line)
            line = ""
            for position, part in enumerate(parts):
                if not part or len(part) == 0:
                    continue
                for expands_regex in expands_regexs:
                    if re.match(expands_regex, part):
                        if position == 0:
                            part = part + " "
                        elif position == len(parts) - 1:
                            part = " " + part
                        else:
                            part = " " + part + " "
                        break
                line += part
        final_markdown += line + "\n"
    return final_markdown


def input_modifier(string, is_chat=True):
    if not settings["activate"] or string == "" or settings["translate mode"] == "from":
        return string
    else:
        return modify_string(
            string,
            settings["translator string"],
            settings["user lang"],
            settings["llm lang"],
        )


def output_modifier(string, is_chat=True):
    if not settings["activate"] or settings["translate mode"] == "to":
        return string
    else:
        return modify_string(
            html.unescape(string),
            settings["translator string"],
            settings["llm lang"],
            settings["user lang"],
            with_error_string=True,
        )


def ui():
    initialize()
    if params["is_tab"]:
        tab_ui()
    else:
        block_ui()


def block_ui():
    # Finding the language and translator name from the language and translator code to use as the default value
    try:
        llm_lang_name = list(language_codes.keys())[
            list(language_codes.values()).index(settings["llm lang"])
        ]
    except ValueError:
        llm_lang_name = list(language_codes.keys())[0]
    try:
        user_lang_name = list(language_codes.keys())[
            list(language_codes.values()).index(settings["user lang"])
        ]
    except ValueError:
        user_lang_name = list(language_codes.keys())[0]
    try:
        translator_name = list(translator_codes.keys())[
            list(translator_codes.values()).index(settings["translator string"])
        ]
    except ValueError:
        translator_name = list(translator_codes.keys())[0]

    # Gradio elements
    with gr.Group():
        with gr.Column():
            with gr.Row():
                activate = gr.Checkbox(
                    value=settings["activate"], label=read_i18n("启用翻译")
                )
            with gr.Row():
                mode = gr.Radio(
                    choices=read_i18n(["to-from", "to", "from"]),
                    label=read_i18n("翻译模式"),
                    value=read_i18n("to-from"),
                    min_width=1,
                )
                i18n_lang = gr.Dropdown(
                    value=read_i18n(settings["i18n lang"]),
                    choices=read_i18n(i18n_data.columns.tolist()),
                    label=read_i18n("插件语言"),
                    min_width=1,
                )
            with gr.Row():
                llm_lang = gr.Dropdown(
                    value=llm_lang_name,
                    choices=[k for k in language_codes],
                    label=read_i18n("LLM的语言"),
                    min_width=1,
                )
                user_lang = gr.Dropdown(
                    value=user_lang_name,
                    choices=[k for k in language_codes],
                    label=read_i18n("用户语言"),
                    min_width=1,
                )
                translator = gr.Dropdown(
                    value=translator_name,
                    choices=[k for k in translator_codes],
                    label=read_i18n("翻译器"),
                    min_width=1,
                )

    # Event functions to update the parameters in the backend
    activate.change(
        lambda x: (settings.update({"activate": x}), save_settings()), activate, None
    )
    mode.change(
        lambda x: (
            settings.update({"translate mode": read_i18n(x, reverse=True)}),
            save_settings(),
        ),
        mode,
        None,
    )
    i18n_lang.change(change_i18n_language, i18n_lang, None)
    llm_lang.change(
        lambda x: (
            new_language_code := language_codes[x],
            settings.update({"llm lang": new_language_code}),
            save_settings(),
        ),
        llm_lang,
        None,
    )
    user_lang.change(
        lambda x: (
            new_language_code := language_codes[x],
            settings.update({"user lang": new_language_code}),
            save_settings(),
        ),
        user_lang,
        None,
    )
    translator.change(
        update_languages, inputs=[translator], outputs=[llm_lang, user_lang]
    )
    params["is_tab"] = True


def tab_ui():
    gr.Button("WIP")
    params["is_tab"] = False


def update_languages(x):
    settings["translator string"] = translator_codes[x]
    save_settings()
    language_codes = get_languages(settings["translator string"])
    llm_lang = gr.Dropdown.update(
        choices=[k for k in language_codes], label=read_i18n("LLM的语言")
    )
    user_lang = gr.Dropdown.update(
        choices=[k for k in language_codes], label=read_i18n("用户语言")
    )
    return llm_lang, user_lang


def change_i18n_language(x):
    new_language_code = read_i18n(x, reverse=True)
    # print(new_language_code)
    settings.update({"i18n lang": new_language_code})
    # print(settings)
    save_settings()
    shared.need_restart = True
    gr.Info(read_i18n("刷新页面后生效", new_language_code))
