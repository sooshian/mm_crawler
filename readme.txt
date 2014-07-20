思路

我一开始就想了构建一种结构化的程序，
通过分析网站得到，应该有两类爬数据任务，一类是找到不同主题图片的页面，另一类是从特定主题图片页面里找出所有图片的URL。

网站的层次结构比较简单，导航栏给出了各个大分类的页面，每个分类页面里有很多的主题。

比如 清凉美女 第三页的URL如下
http://www.22mm.cc/mm/qingliang/index_3.html

分析这个页面的HTML（使用BeautifulSoup）得到了各个主题的URL。这个是PageFinder的工作，也就是解决第一类任务，即发现不同主题图片页面的工作。

直接爬下来的数据和用浏览器打开看到的是不一样的，因为有一些JS在加载时被执行了。开始打算用Ghost.py来动态加载页面，后来发现在id=imgString
那个div下面有一个<script>标签，里面存有图片的URL。

于是就从这里面提取了。这个是ResourcesAnalysiser的工作，解决第二类任务。

PS：对于-l（图片数量限制）的设定表示很不能理解，于是没有实现。（这点图根本不够看……不想限制）

程序结构

crawler -> PageFinder -> urls_of_pages -> ResourcesAnalysis -> urls_of_resources -> Downloader

多线程是用Queue来分配任务的，Downloader这个类作为线程worker来不断的读出task，下载，并保存。

复用的话，重写PageFinder和ResourcesAnalysis就行了。可能针对不同类型的网站还需要大改一下，但是多数静态页面应该是不用改了。