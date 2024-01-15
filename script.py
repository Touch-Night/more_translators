import html
import gradio as gr
import translators as ts
import os
import re
import uuid
import pandas as pd
import yaml

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
    "user lang": "zh",  # todo
    "llm lang": "en",  # todo
    "i18n lang": "zh-cn",
    "translator string": "alibaba",
    "translate mode": "to-from",  # todo, to-from, to, from
}

# Update settings from settings.yaml
def load_settings():
    settings_dir = "./extensions/more_translators/settings.yaml"
    if os.path.exists(settings_dir):
        with open(settings_dir, "r") as file:
            settings.update(yaml.load(file, Loader=yaml.FullLoader))
    else:
        save_settings()
        print("未找到设置文件settings.yaml，已按默认设置创建。")

# Save settings to settings.yaml when settings is modified
def save_settings():
    settings_dir = "./extensions/more_translators/settings.yaml"
    # Check if the directory exists, if not, create it
    if not os.path.exists(os.path.dirname(settings_dir)):
        os.makedirs(os.path.dirname(settings_dir))
    # Save settings to settings.yaml
    with open(settings_dir, "w") as file:
        yaml.dump(settings, file)


# Translate from i18n.csv to translator_codes and language_codes
def read_i18n(i18n_value, i18n_lang=settings["i18n lang"]):
    if i18n_value not in i18n_data.index or i18n_lang not in i18n_data.columns:
        return i18n_value
    return i18n_data.loc[i18n_value, i18n_lang]


def value_to_language_code(value, translator):
    if (
        value not in supported_language_map_data.index
        or translator not in supported_language_map_data.columns
    ):
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

load_settings()

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

language_codes = get_languages(settings["translator string"])


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
    if not settings["activate"] or string == "":
        return string
    return modify_string(
        string, settings["translator string"], "auto", settings["llm lang"]
    )


def output_modifier(string):
    if not settings["activate"]:
        return string
    translated_str = modify_string(
        html.unescape(string),
        settings["translator string"],
        settings["llm lang"],
        settings["user lang"],
    )
    return translated_str


def ui():
    # Finding the language and translator name from the language and translator code to use as the default value
    language_name = list(language_codes.keys())[
        list(language_codes.values()).index(settings["user lang"])
    ]
    translator_name = list(translator_codes.keys())[
        list(translator_codes.values()).index(settings["translator string"])
    ]

    # Gradio elements
    with gr.Row():
        activate = gr.Checkbox(value=settings["activate"], label="启用翻译")

    with gr.Row():
        language = gr.Dropdown(
            value=language_name, choices=[k for k in language_codes], label="AI的语言"
        )

    with gr.Row():
        translator = gr.Dropdown(
            value=translator_name, choices=[k for k in translator_codes], label="翻译器"
        )

    # Event functions to update the parameters in the backend
    activate.change(lambda x: (settings.update({"activate": x}), save_settings()), activate, None)
    translator.change(update_languages, inputs=[translator], outputs=[language])
    language.change(
        lambda x: (
            new_language_code := language_codes[x],
            settings.update({"user lang": new_language_code}),
            save_settings(),
        ),
        language,
        None,
    )


def update_languages(x):
    settings["translator string"] = translator_codes[x]
    save_settings()
    language_codes = get_languages(settings["translator string"])
    language = gr.Dropdown.update(choices=[k for k in language_codes], label="AI的语言")
    return language