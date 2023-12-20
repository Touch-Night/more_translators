[中文](#anchorZH) / [EN](#anchorEN)

-------------------------

<a name="anchorZH"></a>
## 更多翻译引擎插件
供text-generation-webui使用的插件，为其提供多种翻译器支持。
### 安装  
1. 根据你使用的操作系统双击对应的批处理文件`cmd_xxx.bat`。
2. 输入`pip install --upgrade translators`，然后按<kbd>Enter</kbd>键来安装这个插件的依赖。
3. 把这个代码仓库下载到你text-generation-webui的插件文件夹。你可以通过以下方式之一来完成：
<details>
  <summary>手动下载zip压缩包</summary>
    3.1. 点击 <img src="https://github.com/Touch-Night/more_translators/assets/102669562/8682492b-7930-4ff4-a930-e35b174956fc" height = "30" alt="<>Code" align=center /><br>
    3.2. 然后点击 <a href="https://codeload.github.com/Touch-Night/more_translators/zip/refs/heads/main"><img src="https://github.com/Touch-Night/more_translators/assets/102669562/f0f6ad5c-1671-4f41-92a2-3caaebd8232c" height = "50" alt="[]Download ZIP" align=center /></a>以下载zip压缩包<br>
    3.3. 之后把<code>more_translators-main.zip</code>解压到你的<code>extensions</code>文件夹，并将其重命名为<code>more_translators</code>。之后，你的文件结构应该像这样：
  <pre>
  text-generation-webui  
   ├─extensions  
   │  ├─more_translators  
   │  │  │  script.py  
  ... ...
  </pre>
</details>
<details>
  <summary>使用Git</summary>
    3.1. 确保你已经正确安装Git，并且确保你的Git代理设置能让你的Git连接到Github<br>
    3.2. 在步骤一打开的命令行窗口中，输入<code>cd extensions</code>并按下<kbd>Enter</kbd>键<br>
    3.3. 随后输入<code>git clone https://github.com/Touch-Night/more_translators.git</code>并按下<kbd>Enter</kbd>键。之后，你的文件结构应该像这样：
  <pre>
  text-generation-webui  
   ├─extensions  
   │  ├─more_translators  
   │  │  │  script.py  
  ... ...
  </pre>
</details>

4. 这样，插件就安装好了。你可以在你的text-generation-webui的`Session`一栏中启用它。
  
------------------------------------

<a name="anchorEN"></a>
## More_translators extension
Extension for text-generation-webui, added a lot more translators.
### Install  
1. Double click `cmd_xxx.bat`.
2. Type `pip install --upgrade translators` and then press <kbd>Enter</kbd> to install dependency for this extension.
3. Download this repo to your webui extension folder. You can do that by:
<details>
  <summary>Download zip mannually</summary>
    3.1. Click <img src="https://github.com/Touch-Night/more_translators/assets/102669562/8682492b-7930-4ff4-a930-e35b174956fc" height = "30" alt="<>Code" align=center /><br>
    3.2. Then click <a href="https://codeload.github.com/Touch-Night/more_translators/zip/refs/heads/main"><img src="https://github.com/Touch-Night/more_translators/assets/102669562/f0f6ad5c-1671-4f41-92a2-3caaebd8232c" height = "50" alt="[]Download ZIP" align=center /></a> to download this repository<br>
    3.3. And then extract <code>more_translators-main.zip</code> to your <code>extensions</code> folder, rename <code>more_translators-main</code> folder to <code>more_translators</code>. After that, your file structure should be like:
  <pre>
  text-generation-webui  
   ├─extensions  
   │  ├─more_translators  
   │  │  │  script.py  
  ... ...
  </pre>
</details>
<details>
  <summary>Git</summary>
    3.1. Make sure you have installed Git, and have set the proxy correctly if your connection to GitHub is blocked by local government<br>
    3.2. In the terminal opened in step 1, type <code>cd extensions</code> and then press <kbd>Enter</kbd><br>
    3.3. Type <code>git clone https://github.com/Touch-Night/more_translators.git</code> and then press <kbd>Enter</kbd>. After that, your file structure should be like:
  <pre>
  text-generation-webui  
   ├─extensions  
   │  ├─more_translators  
   │  │  │  script.py  
  ... ...
  </pre>
</details>

4. Installation is completed, you can enable it in the `Session` section of your webui.


