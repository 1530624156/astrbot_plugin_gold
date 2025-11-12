from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from bs4 import BeautifulSoup
import requests

@register("GoldSearchPlugins", "Mavis", "国内首饰金价查询插件", "1.0.0")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""

    # 注册指令的装饰器。指令名为 helloworld。注册成功后，发送 `/helloworld` 就会触发这个指令，并回复 `你好, {user_name}!`
    @filter.command("gold")
    async def gold(self, event: AstrMessageEvent):
        """gold指令查询金价""" 
        print("GoldSearchPlugins: GoldSearchPlugins.gold()")
        result = self.fetch_gold_prices()
        yield event.plain_result(f"{result}")
        # yield event.plain_result(f"Hello, {user_name}, 你发了 {message_str}!") # 发送一条纯文本消息

    def fetch_gold_prices(self):
        url = "https://www.jinziyinzi.com"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0 Safari/537.36"
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')

            table = soup.find('table')
            if not table:
                return "❌ 未找到黄金价格表格，请稍后再试。"

            rows = table.find_all('tr')
            prices = []

            for row in rows:
                cols = row.find_all('td')
                if len(cols) < 4:
                    continue

                brand = cols[0].get_text(strip=True)
                retail_price = cols[1].get_text(strip=True)
                trade_in_price = cols[2].get_text(strip=True)
                update_time = cols[3].get_text(strip=True)

                # 处理换购价
                if trade_in_price == "-":
                    trade_in_price = "无"

                prices.append({
                    "brand": brand,
                    "retailPrice": retail_price,
                    "tradeInPrice": trade_in_price,
                    "updateTime": update_time
                })

            if not prices:
                return "⚠️ 未解析到任何黄金价格数据。"

            # 美化输出
            lines = ["💰【今日黄金价格】"]
            lines.append("—" * 30)
            for item in prices:
                line = (
                    f"🔹 品牌：{item['brand']}\n"
                    f"   零售价(元/克)：{item['retailPrice']} \n"
                    f"   换购价(元/克)：{item['tradeInPrice']} \n"
                    f"   更新时间：{item['updateTime']}"
                )
                lines.append(line)
            lines.append("—" * 30)
            lines.append("📊 数据来源：金子银子网")

            return "\n\n".join(lines)

        except Exception as e:
            return f"❌ 获取黄金价格失败：{str(e)}"
        
    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""

