import os
import requests
import feedparser
from datetime import datetime
import time
import random
import re

def send_to_serverchan(title, content, sendkey):
    """发送消息到Server酱"""
    url = f"https://sctapi.ftqq.com/{sendkey}.send"
    
    # 构建消息内容
    data = {
        "title": title,
        "desp": content
    }
    
    try:
        response = requests.post(url, data=data, timeout=10)
        result = response.json()
        if result.get("code") == 0:
            print(f"✅ 推送成功！消息ID: {result.get('data', {}).get('pushid')}")
            return True
        else:
            print(f"❌ 推送失败: {result.get('message')}")
            return False
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def get_zhihu_hot():
    """获取知乎热榜"""
    news_items = []
    try:
        print("🔍 获取知乎热榜...")
        # 知乎热榜API
        response = requests.get(
            'https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total?limit=5', 
            headers={'User-Agent': 'Mozilla/5.0'}, 
            timeout=10
        )
        data = response.json()
        
        for item in data.get('data', [])[:5]:
            target = item.get('target', {})
            title = target.get('title', '')
            url = f"https://www.zhihu.com/question/{target.get('id', '')}"
            detail_text = item.get('detail_text', '')
            
            if title and url:
                # 清理描述
                excerpt = target.get('excerpt', '')
                if excerpt and len(excerpt) > 0:
                    description = excerpt[:80] + '...' if len(excerpt) > 80 else excerpt
                else:
                    description = f"知乎热议话题，热度：{detail_text}"
                
                news_items.append({
                    "title": f"❓ {title}",
                    "desc": description,
                    "link": url
                })
    except Exception as e:
        print(f"⚠️ 知乎热榜获取失败: {e}")
        news_items.append({
            "title": "⚠️ 知乎热榜暂时不可用",
            "desc": "可能由于API限制，请稍后重试",
            "link": "https://www.zhihu.com/hot"
        })
    
    return news_items

def get_tech_news_cn():
    """获取中文科技新闻"""
    news_items = []
    
    # 1. 36氪快讯
    try:
        print("🔍 获取36氪快讯...")
        feed = feedparser.parse('https://rsshub.app/36kr/newsflashes')
        for entry in feed.entries[:3]:
            title = entry.title
            link = entry.link
            # 提取描述中的前100字作为简述
            description = entry.get('description', '')
            if description:
                # 清理HTML标签
                description = re.sub('<[^<]+?>', '', description)
                description = description[:100] + '...' if len(description) > 100 else description
            else:
                description = "点击查看详情"
            
            news_items.append({
                "title": f"🚀 {title}",
                "desc": description,
                "link": link
            })
    except Exception as e:
        print(f"⚠️ 36氪获取失败: {e}")
    
    # 2. 虎嗅网
    try:
        print("🔍 获取虎嗅网科技新闻...")
        feed = feedparser.parse('https://rsshub.app/huxiu/tag/1')
        for entry in feed.entries[:2]:
            title = entry.title
            link = entry.link
            description = entry.get('summary', '')
            if description:
                description = re.sub('<[^<]+?>', '', description)
                description = description[:80] + '...' if len(description) > 80 else description
            else:
                description = "虎嗅深度科技报道"
            
            news_items.append({
                "title": f"🐯 {title}",
                "desc": description,
                "link": link
            })
    except Exception as e:
        print(f"⚠️ 虎嗅网获取失败: {e}")
    
    # 3. 少数派（优质数字生活内容）
    try:
        print("🔍 获取少数派...")
        feed = feedparser.parse('https://sspai.com/feed')
        for entry in feed.entries[:2]:
            title = entry.title
            link = entry.link
            description = "少数派精选文章"
            
            news_items.append({
                "title": f"📱 {title}",
                "desc": description,
                "link": link
            })
    except Exception as e:
        print(f"⚠️ 少数派获取失败: {e}")
    
    return news_items[:5]  # 最多返回5条

def get_finance_news_cn():
    """获取中文财经新闻"""
    news_items = []
    
    # 1. 新浪财经
    try:
        print("🔍 获取新浪财经...")
        feed = feedparser.parse('https://rsshub.app/sina/finance')
        for entry in feed.entries[:3]:
            title = entry.title
            link = entry.link
            
            # 从描述中提取内容
            description = entry.get('description', '')
            if description and len(description) > 20:
                # 清理HTML和特殊字符
                description = re.sub('<[^<]+?>', '', description)
                description = description[:80] + '...' if len(description) > 80 else description
            else:
                description = "财经快讯详情"
            
            news_items.append({
                "title": f"💰 {title}",
                "desc": description,
                "link": link
            })
    except Exception as e:
        print(f"⚠️ 新浪财经获取失败: {e}")
    
    # 2. 华尔街见闻
    try:
        print("🔍 获取华尔街见闻...")
        feed = feedparser.parse('https://rsshub.app/wallstreetcn/news/global')
        for entry in feed.entries[:2]:
            title = entry.title
            link = entry.link
            description = entry.get('summary', '华尔街见闻全球财经资讯')
            if description:
                description = description[:60] if description else "全球市场动态"
            
            news_items.append({
                "title": f"🌍 {title}",
                "desc": description,
                "link": link
            })
    except Exception as e:
        print(f"⚠️ 华尔街见闻获取失败: {e}")
    
    # 3. 财联社电报（快讯）
    try:
        print("🔍 获取财联社快讯...")
        feed = feedparser.parse('https://rsshub.app/cls/depth')
        for entry in feed.entries[:2]:
            title = entry.title
            link = entry.link
            # 财联社的快讯通常标题就是完整内容
            if len(title) > 40:
                description = title[:60] + "..."
            else:
                description = "财联社深度报道"
            
            news_items.append({
                "title": f"📈 {title[:40]}" + ("..." if len(title) > 40 else ""),
                "desc": description,
                "link": link
            })
    except Exception as e:
        print(f"⚠️ 财联社获取失败: {e}")
    
    return news_items[:5]  # 最多返回5条

def get_daily_tip():
    """获取每日小贴士/名言"""
    tips = [
        "📊 投资有风险，入市需谨慎",
        "💡 科技改变生活，创新驱动未来",
        "📈 市场永远是对的，错的只有你的判断",
        "🚀 保持学习，与时俱进",
        "💼 理财就是理生活，规划让未来更清晰",
        "🌱 种一棵树最好的时间是十年前，其次是现在",
        "🎯 专注产生复利，时间见证成长",
        "🔍 独立思考，谨慎决策"
    ]
    return random.choice(tips)

def main():
    """主函数"""
    sendkey = os.getenv('SENDKEY')
    
    if not sendkey:
        print("❌ 未设置SENDKEY环境变量")
        print("💡 请在环境中设置SENDKEY，或在代码中直接赋值")
        return
    
    print("📰 开始获取今日中文新闻...")
    
    # 获取新闻
    tech_news = get_tech_news_cn()
    finance_news = get_finance_news_cn()
    daily_tip = get_daily_tip()
    
    # 构建推送内容
    today = datetime.now().strftime('%Y年%m月%d日')
    weekday = ["一", "二", "三", "四", "五", "六", "日"][datetime.now().weekday()]
    
    # 使用Markdown格式
    content = f"# 📰 每日科技财经简报  \n"
    content += f"**{today} 星期{weekday}**  \n\n"
    
    # 科技新闻部分
    content += "## 🚀 科技前沿  \n"
    if tech_news:
        for i, news in enumerate(tech_news, 1):
            content += f"**{i}. {news['title']}**  \n"
            content += f"{news['desc']}  \n"
            content += f"[查看详情]({news['link']})  \n\n"
    else:
        content += "暂未获取到科技新闻  \n\n"
    
    content += "---  \n\n"
    
    # 财经新闻部分
    content += "## 💰 财经要闻  \n"
    if finance_news:
        for i, news in enumerate(finance_news, 1):
            content += f"**{i}. {news['title']}**  \n"
            content += f"{news['desc']}  \n"
            content += f"[查看详情]({news['link']})  \n\n"
    else:
        content += "暂未获取到财经新闻  \n\n"
    
    content += "---  \n\n"
    
    # 每日小贴士
    content += f"## 💡 每日一语  \n{daily_tip}  \n\n"
    
    # 底部信息
    content += "---  \n"
    content += "**✨ 推送信息**  \n"
    content += f"📅 生成时间：{datetime.now().strftime('%H:%M:%S')}  \n"
    content += "🔧 自动化生成 | 点击链接查看全文  \n"
    content += "⏰ 每日上午8点自动推送  \n"
    content += "⚙️ 新闻源：36氪/虎嗅/新浪财经/华尔街见闻  \n"
    
    # 发送推送
    emojis = ["📰", "📊", "🚀", "💼", "🌅", "📈", "💡"]
    title = f"{random.choice(emojis)} 每日简报 {datetime.now().strftime('%m-%d')}"
    
    print(f"📤 正在发送推送，标题: {title}")
    print(f"📄 内容长度: {len(content)} 字符")
    
    success = send_to_serverchan(title, content, sendkey)
    
    if success:
        print("🎉 今日新闻推送任务完成！")
    else:
        print("❌ 推送任务失败")

def test_local():
    """本地测试函数（不发送推送）"""
    print("🧪 开始本地测试...")
    
    # 测试新闻获取功能
    print("\n1. 测试科技新闻获取...")
    tech_news = get_tech_news_cn()
    print(f"   获取到 {len(tech_news)} 条科技新闻")
    
    print("\n2. 测试财经新闻获取...")
    finance_news = get_finance_news_cn()
    print(f"   获取到 {len(finance_news)} 条财经新闻")
    
    print("\n3. 测试知乎热榜获取...")
    zhihu_news = get_zhihu_hot()
    print(f"   获取到 {len(zhihu_news)} 条知乎热榜")
    
    print("\n4. 测试每日小贴士...")
    tip = get_daily_tip()
    print(f"   今日小贴士: {tip}")
    
    print("\n✅ 本地测试完成！")
    return True

if __name__ == "__main__":
    # 判断是否在测试环境
    if os.getenv('TEST_MODE') == '1' or not os.getenv('SENDKEY'):
        print("🛠️ 进入测试模式（不发送实际推送）")
        test_local()
    else:
        # 正常执行推送
        main()
