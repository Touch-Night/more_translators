[中文](#anchorZH) / [EN](#anchorEN)

-------------------------

<a name="anchorZH"></a>
## 猫翻插件
供text-generation-webui使用的插件，为其提供多种翻译器支持。
### 安装  
1. 根据你使用的操作系统双击对应的批处理文件`cmd_xxx.bat`。
2. 输入`pip install --upgrade translators`，然后按<kbd>Enter</kbd>键来安装这个插件的依赖。
<details>
  <summary>3. 把这个代码仓库下载到你text-generation-webui的插件文件夹。你可以通过以下方式<strong>之一</strong>来完成：</summary>
  <details>
    <summary>①. 手动下载zip压缩包</summary>
      &emsp;&emsp;3.1. 点击 <img src="https://github.com/Touch-Night/more_translators/assets/102669562/8682492b-7930-4ff4-a930-e35b174956fc" height = "30" alt="<>Code" align=center /><br>
      &emsp;&emsp;3.2. 然后点击 <a href="https://codeload.github.com/Touch-Night/more_translators/zip/refs/heads/main"><img src="https://github.com/Touch-Night/more_translators/assets/102669562/f0f6ad5c-1671-4f41-92a2-3caaebd8232c" height = "50" alt="[]Download ZIP" align=center /></a>以下载zip压缩包<br>
      &emsp;&emsp;3.3. 之后把<code>more_translators-main.zip</code>解压到你的<code>extensions</code>文件夹，并将其重命名为<code>more_translators</code>。之后，你的文件结构应该像这样：
    <pre>
    text-generation-webui  
     ├─extensions  
     │  ├─more_translators  
     │  │  │  script.py  
    ... ...
    </pre>
  </details>
  <details>
    <summary>②. 使用Git</summary>
      &emsp;&emsp;3.1. 确保你已经正确安装Git，并且确保你的Git代理设置能让你的Git连接到Github<br>
      &emsp;&emsp;3.2. 在步骤一打开的命令行窗口中，输入<code>cd extensions</code>并按下<kbd>Enter</kbd>键<br>
      &emsp;&emsp;3.3. 随后输入<code>git clone https://github.com/Touch-Night/more_translators.git</code>并按下<kbd>Enter</kbd>键。之后，你的文件结构应该像这样：
    <pre>
    text-generation-webui  
     ├─extensions  
     │  ├─more_translators  
     │  │  │  script.py  
    ... ...
    </pre>
  </details>
</details>
<details>
  <summary>4. 这样，插件就安装好了。你可以在你的text-generation-webui的`Session`一栏中启用它。</summary>
  <img src="https://github.com/Touch-Night/more_translators/assets/102669562/8000ff33-82aa-4c98-bc03-ca5e2f15fe69" height = "343" alt="Session" align=center />
</details>

### 使用说明
- 如果你正确地启动了这个插件，那么你将可以在`Chat`、`Default`、`Notebook`下看到新增了如下面板：
![image](https://github.com/Touch-Night/more_translators/assets/102669562/694e12a7-926e-4fda-bbbf-b40be6fe89ac)
- 这个插件在`☑ 启用翻译`勾选上时才会起作用。
- 它在`to-from`模式下，会使用你选择的`翻译器`将你的输入从`用户语言`翻译成`LLM的语言`之后再提交给模型，并把模型生成的结果从`LLM的语言`翻译成`用户语言`之后再输出给你。
- 而在`to`模式下，它就只会翻译你的输入，不翻译模型输出；在`from`模式下，只翻译模型输出，不翻译你的输入。
- 设置项`插件语言`是指这个插件界面的显示语言，不对输入输出造成影响。内容由文件`i18n.csv`控制。
- 如果你发现某个`翻译器`不起作用，可以在[translators](https://github.com/UlionTse/translators)模块的仓库的[Issues](https://github.com/UlionTse/translators/issues)一栏中查找该问题是否已被报告，并在**没有人报告**此`翻译器`问题时[提交Issue](https://github.com/UlionTse/translators/issues/new?assignees=UlionTse&labels=&projects=&template=bug_report.yml&title=%5BBug%5D%3A+)
  
------------------------------------

<a name="anchorEN"></a>
## More_translators extension
Extension for text-generation-webui, added a lot more translators.
### Install  
1. Double click `cmd_xxx.bat`.
2. Type `pip install --upgrade translators` and then press <kbd>Enter</kbd> to install dependency for this extension.
<details>
  <summary>3. Download this repo to your webui extension folder. You can do that by <strong>either</strong>:</summary>
  <details>
    <summary>①. Download zip mannually</summary>
      &emsp;&emsp;3.1. Click <img src="https://github.com/Touch-Night/more_translators/assets/102669562/8682492b-7930-4ff4-a930-e35b174956fc" height = "30" alt="<>Code" align=center /><br>
      &emsp;&emsp;3.2. Then click <a href="https://codeload.github.com/Touch-Night/more_translators/zip/refs/heads/main"><img src="https://github.com/Touch-Night/more_translators/assets/102669562/f0f6ad5c-1671-4f41-92a2-3caaebd8232c" height = "50" alt="[]Download ZIP" align=center /></a> to download this repository<br>
      &emsp;&emsp;3.3. And then extract <code>more_translators-main.zip</code> to your <code>extensions</code> folder, rename <code>more_translators-main</code> folder to <code>more_translators</code>. After that, your file structure should be like:
    <pre>
    text-generation-webui  
     ├─extensions  
     │  ├─more_translators  
     │  │  │  script.py  
    ... ...
    </pre>
  </details>
  <details>
    <summary>②. Git</summary>
      &emsp;&emsp;3.1. Make sure you have installed Git, and have set the proxy correctly if your connection to GitHub is blocked by local government<br>
      &emsp;&emsp;3.2. In the terminal opened in step 1, type <code>cd extensions</code> and then press <kbd>Enter</kbd><br>
      &emsp;&emsp;3.3. Type <code>git clone https://github.com/Touch-Night/more_translators.git</code> and then press <kbd>Enter</kbd>. After that, your file structure should be like:
    <pre>
    text-generation-webui  
     ├─extensions  
     │  ├─more_translators  
     │  │  │  script.py  
    ... ...
    </pre>
  </details>
</details>
<details>
  <summary>4. Installation is completed, you can enable it in the `Session` section of your webui.</summary>
  <img src="https://github.com/Touch-Night/more_translators/assets/102669562/8000ff33-82aa-4c98-bc03-ca5e2f15fe69" height = "343" alt="Session" align=center />
</details>

### Tips
- If you applied this extension correctly, you should see this block is added in `Chat`, `Default` and `Notebook` tabs:
![image](https://github.com/Touch-Night/more_translators/assets/102669562/694e12a7-926e-4fda-bbbf-b40be6fe89ac)
- More_translators will take effect only when `☑ Activate` is checked.
- In `to-from` mode, it will translate both your input from `User's language` to `LLM's language` using the `Translator` selected, and LLM's output from `LLM's language` to `User's language`.
- In `to` mode, it will only translate your input, and in `from` mode, it will only translate LLM's output.
- `Plugin's language` refers to the language of this plugin's UI, all the contents is in `i18n.csv`.
- If you found a `Translator` is not working, you can search for similar issue in [translators](https://github.com/UlionTse/translators)'s [Issues page](https://github.com/UlionTse/translators/issues), and [submit new issue](https://github.com/UlionTse/translators/issues/new?assignees=UlionTse&labels=&projects=&template=bug_report.yml&title=%5BBug%5D%3A+) if there's **no** similar issues.
