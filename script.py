import html
import gradio as gr
import translators as ts
import os
import re
import uuid
import pandas as pd

i18n_data = pd.read_csv(
    "./extensions/more_translators/i18n.csv", encoding="utf-8", header=0, index_col=0
)
supported_language_map_data = pd.read_csv(
    "./extensions/more_translators/supported_language_map.csv",
    encoding="utf-8",
    header=0,
    index_col=0,
)


# Translate from i18n.csv to translator_codes and language_codes
def read_i18n(i18n_value, i18n_lang):
    if i18n_value not in i18n_data.index or i18n_lang not in i18n_data.columns:
        return i18n_value
    return i18n_data.loc[i18n_value, i18n_lang]


def value_to_language_code(value, translator):
    if (
        value not in supported_language_map_data.index
        or translator not in supported_language_map_data.columns
    ):
        raise ValueError("value or translator is not in supported_language_map_data")
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


params = {
    "activate": True,
    "user lang": "zh",  # todo
    "target lang": "en",  # todo
    "i18n lang": "zh-cn",
    "translator string": "alibaba",
}

translator_codes = {
    read_i18n("alibaba", params["i18n lang"]): "alibaba",
    read_i18n("apertium", params["i18n lang"]): "apertium",
    read_i18n("argos", params["i18n lang"]): "argos",
    read_i18n("baidu", params["i18n lang"]): "baidu",
    read_i18n("bing", params["i18n lang"]): "bing",
    read_i18n("caiyun", params["i18n lang"]): "caiyun",
    read_i18n("cloudTranslation", params["i18n lang"]): "cloudTranslation",
    read_i18n("deepl", params["i18n lang"]): "deepl",
    read_i18n("elia", params["i18n lang"]): "elia",
    read_i18n("google", params["i18n lang"]): "google",
    read_i18n("iflyrec", params["i18n lang"]): "iflyrec",
    read_i18n("itranslate", params["i18n lang"]): "itranslate",
    read_i18n("languageWire", params["i18n lang"]): "languageWire",
    read_i18n("lingvanex", params["i18n lang"]): "lingvanex",
    read_i18n("mglip", params["i18n lang"]): "mglip",
    read_i18n("modernMt", params["i18n lang"]): "modernMt",
    read_i18n("papago", params["i18n lang"]): "papago",
    read_i18n("qqFanyi", params["i18n lang"]): "qqFanyi",
    read_i18n("qqTranSmart", params["i18n lang"]): "qqTranSmart",
    read_i18n("reverso", params["i18n lang"]): "reverso",
    read_i18n("sogou", params["i18n lang"]): "sogou",
    read_i18n("translateCom", params["i18n lang"]): "translateCom",
    read_i18n("utibet", params["i18n lang"]): "utibet",
}

language_codes = get_languages(params["translator string"])


def modify_string(string, selected_translator, source, target):
    pattern = re.compile(r"```(.*?)\n(.*?)```", re.DOTALL)  # find all code blocks
    blocks = [
        (str(uuid.uuid4()), m.group(1), m.group(2))
        for m in re.finditer(pattern, string)
    ]
    string_without_blocks = string  # remove all code blocks
    for uuid_str, _, _ in blocks:
        string_without_blocks = re.sub(
            pattern, uuid_str, string_without_blocks, count=1
        )  # replace all code blocks with uuid
    translated_str = ts.translate_text(
        html.unescape(string),
        translator=selected_translator,
        from_language=source,
        to_language=target,
    )  # translate the string without code blocks
    for uuid_str, lang, block in blocks:
        # Remove leading and trailing whitespaces from each block
        block = block.strip()
        translated_str = translated_str.replace(
            uuid_str, "```" + lang + "\n" + block + "\n```"
        )  # replace the uuid with the translated code block
    return translated_str


def input_modifier(string):
    if not params["activate"] or string == "":
        return string
    return modify_string(string, params["translator string"], "auto", "en")


def output_modifier(string):
    if not params["activate"]:
        return string
    translated_str = modify_string(
        html.unescape(string),
        params["translator string"],
        "en",
        params["user lang"],
    )
    return translated_str


def ui():
    params["user lang"] = read_language_code()

    # Finding the language and translator name from the language and translator code to use as the default value
    language_name = list(language_codes.keys())[
        list(language_codes.values()).index(params["user lang"])
    ]
    translator_name = list(translator_codes.keys())[
        list(translator_codes.values()).index(params["translator string"])
    ]

    # Gradio elements
    with gr.Row():
        activate = gr.Checkbox(value=params["activate"], label="启用翻译")

    with gr.Row():
        language = gr.Dropdown(
            value=language_name, choices=[k for k in language_codes], label="AI的语言"
        )

    with gr.Row():
        translator = gr.Dropdown(
            value=translator_name, choices=[k for k in translator_codes], label="翻译器"
        )

    # Event functions to update the parameters in the backend
    activate.change(lambda x: params.update({"activate": x}), activate, None)
    translator.change(update_languages, inputs=[translator], outputs=[language])
    language.change(
        lambda x: (
            new_language_code := language_codes[x],
            params.update({"user lang": new_language_code}),
            write_language_code(new_language_code),
        ),
        language,
        None,
    )


def update_languages(x):
    params["translator string"] = translator_codes[x]
    language_codes = get_languages(params["translator string"])
    language = gr.Dropdown.update(choices=[k for k in language_codes], label="AI的语言")
    return language


def read_language_code(
    filename="./extensions/more_translators/setting/latest_use_language.txt",
):
    try:
        with open(filename, "r") as file:
            language_code = file.read().strip()
        return language_code
    except FileNotFoundError:
        print(f"找不到{filename}。故使用默认的中文。")
        return "zh"


def write_language_code(
    language_code,
    filename="./extensions/more_translators/setting/latest_use_language.txt",
):
    # Check if the directory exists, if not, create it
    directory = os.path.dirname(filename)
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(filename, "w") as file:
        file.write(language_code)
