# trails-game-tools  
## 中文简介  
  
各类抓包，读取，批处理代码文件  

使用前先```pip install -r requirements.txt```

部分包含```sys.argv```的文件需使用命令行 python *.py 图片文件相对，或完整路径  
对于这些文件，可使用命令行批处理 ```for %f in (*.*) do python *.py %f```

### 关于轨迹游戏文件包处理文件

```models``` 文件夹中包含了所有闪轨与黎轨模型，图片素材的提取及处理代码。

```unpackpka.py```可以根据package_name从闪3，闪4，创的pka中提取所需的pkg文件。可能需要对line 32-33进行适当的修改。

```mdlToGlb.py```为提取黎之轨迹模型的基础文件。暂不可单独使用。  

```pkgtoglb.py```可以从pkg文件中直接提取png，dds图片素材及glb模型文件  
如果要将dds的编码从BC7转换至DXT1，或将dds转换为png，可使用 [TexConv](https://github.com/Microsoft/DirectXTex/wiki/Texconv)，具体方式查看```pkgtoglb.py```中的comments  

```parseSenModel.py```可以根据闪3，闪4的ops文件（需替换目录，具体可直接查看代码文件），读取一个地图所需的所有pkg文件，并进行解码，解出glb，dds以及一个存有object transformation的数据的json，之后需使用Blender加载```buildScene.py```，并替换其中的文件路径，即可让Blender处理模型。  

```parseKuroModel.py```可以根据黎1，黎2的地图json文件（需替换目录，具体可直接查看代码文件），读取一个地图所需的所有mdl及dds文件，并进行解码，解出gltf，png以及一个存有object transformation的数据的json，之后需使用Blender加载```buildScene.py```，并替换其中的文件路径，即可让Blender处理模型。  

[其他工具内容](https://github.com/trails-game)  

## EN intro  

```pip install -r requirements.txt``` before using any of the code  
For code in ```imageProcessing``` or any code that requires ```sys.argv```, can use ```for %f in (*.*) do python *.py %f``` for batch processing  

### models  

```models``` contains code for extracting and processing images, models from Trails of Cold Steel series

```unpackpka.py``` can extract pkg files from pka for Trails of cold steel 3, 4, Hajimari no Kiseki. You will probably need to modify line 32-33 of the code  

```mdlToGlb.py``` extracts models from Kuro no Kiseki 1 and 2. Temporarily, it cannot be used alone and must be used with ```parseKuroModel.py```  

```pkgtoglb.py``` can extract png, dds and glb files from pkg file  
If you want to convert BC7 encoding to DXT1 or convert dds to png, check [TexConv](https://github.com/Microsoft/DirectXTex/wiki/Texconv) and follow the comments in ```pkgtoglb.py```.  

```parseSenModel.py``` can parse files in ops folder of Trails of cold steel 3 and 4. It will then unpack all related pkg files from pka and export glb, dds files with a json file recording the object transformation data. You will then need to run ```buildScene.py``` in Blender to build the complete model. (You will need to modify the file paths in the code file)  

```parseKuroModel.py``` can parse json files in scene folder. It will then unpack and decode all related mdl files and dds files and export gltf, png files with a json file recording the object transformation data. You will then need to run ```buildScene.py``` in Blender to build the complete model. (You will need to modify the file paths in the code file)  

## credits
Trails of cold steel, kuro no kiseki model processing code: [uyjulian](https://gist.github.com/uyjulian/6c590476819bf3bfde6fc78aa3765698)