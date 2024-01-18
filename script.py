import html
import gradio as gr
import translators as ts
import os
import re
import uuid
import pandas as pd
import yaml
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


# Update settings from tranlators_settings.yaml
def load_settings():
    settings_dir = "./extensions/more_translators/translators_settings.yaml"
    if os.path.exists(settings_dir):
        with open(settings_dir, "r") as file:
            settings.update(yaml.load(file, Loader=yaml.FullLoader))
    else:
        print(read_i18n("未找到设置文件translators_settings.yaml，已按默认设置创建。"))
        gr.Warning(read_i18n("未找到设置文件translators_settings.yaml，已按默认设置创建。"))
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
    if not settings["activate"] or string == "" or settings["translate mode"] == "from":
        return string
    else:
        return modify_string(
            string,
            settings["translator string"],
            settings["user lang"],
            settings["llm lang"],
        )


def output_modifier(string):
    if not settings["activate"] or settings["translate mode"] == "to":
        return string
    else:
        return modify_string(
            html.unescape(string),
            settings["translator string"],
            settings["llm lang"],
            settings["user lang"],
        )


def ui():
    initialize()
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
                )
                i18n_lang = gr.Dropdown(
                    value=read_i18n(settings["i18n lang"]),
                    choices=read_i18n(i18n_data.columns.tolist()),
                    label=read_i18n("插件语言"),
                )
            with gr.Row():
                llm_lang = gr.Dropdown(
                    value=llm_lang_name,
                    choices=[k for k in language_codes],
                    label=read_i18n("LLM的语言"),
                )
                user_lang = gr.Dropdown(
                    value=user_lang_name,
                    choices=[k for k in language_codes],
                    label=read_i18n("用户语言"),
                )
                translator = gr.Dropdown(
                    value=translator_name,
                    choices=[k for k in translator_codes],
                    label=read_i18n("翻译器"),
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
