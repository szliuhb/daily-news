import os
import requests
import feedparser
from datetime import datetime
import time

def send_to_serverchan(title, content, sendkey):
    """发送消息到Server酱"""
    url = f"https://sctapi.ftqq.com/{sendkey}.send"
    
    # 构建消息内容
    data = {
        "title": title,
        "desp": content
    }
    
    try:
        response = requests.post(url, data=data)
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

def get_tech_news():
    """获取科技新闻"""
    news_items = []
    
    # 1. Hacker News (顶级科技新闻)
    try:
        print("🔍 获取 Hacker News...")
        top_ids = requests.get('https://hacker-news.firebaseio.com/v0/topstories.json?print=pretty', timeout=10).json()[:5]
        for story_id in top_ids:
            story = requests.get(f'https://hacker-news.firebaseio.com/v0/item/{story_id}.json', timeout=10).json()
            title = story.get('title', '无标题')
            url = story.get('url', f'https://news.ycombinator.com/item?id={story_id}')
            score = story.get('score', 0)
            if score > 100:  # 只取热门内容
                news_items.append(f"🔥 [{score}分] {title}\n   {url}")
            time.sleep(0.1)  # 避免请求过快
    except Exception as e:
        print(f"⚠️  Hacker News获取失败: {e}")
        news_items.append("⚠️ Hacker News 暂时不可用")
    
    # 2. Product Hunt (新产品)
    try:
        print("🔍 获取 Product Hunt...")
        feed = feedparser.parse('https://www.producthunt.com/feed')
        for entry in feed.entries[:3]:
            title = entry.title
            link = entry.link
            news_items.append(f"🆕 {title}\n   {link}")
    except Exception as e:
        print(f"⚠️  Product Hunt获取失败: {e}")
    
    return news_items[:5]  # 最多返回5条

def get_finance_news():
    """获取财经新闻"""
    news_items = []
    
    # 1. Reuters Business (路透社财经)
    try:
        print("🔍 获取 Reuters 财经新闻...")
        feed = feedparser.parse('https://www.reuters.com/arc/outboundfeeds/businessNews/?outputType=rss')
        for entry in feed.entries[:5]:
            title = entry.title
            link = entry.link
            # 清理标题中的HTML标签
            if '<' in title:
                title = title.split('<')[0]
            news_items.append(f"📈 {title}\n   {link}")
    except Exception as e:
        print(f"⚠️  Reuters获取失败: {e}")
        news_items.append("⚠️ 路透财经新闻暂时不可用")
    
    # 2. 新浪财经RSS (备用源)
    if len(news_items) < 3:
        try:
            print("🔍 获取新浪财经...")
            feed = feedparser.parse('https://rsshub.app/sina/finance')
            for entry in feed.entries[:3]:
                title = entry.title
                link = entry.link
                news_items.append(f"💰 {title}\n   {link}")
        except Exception as e:
            print(f"⚠️  新浪财经获取失败: {e}")
    
    return news_items[:5]  # 最多返回5条

def main():
    """主函数"""
    sendkey = os.getenv('SENDKEY')
    
    if not sendkey:
        print("❌ 未设置SENDKEY环境变量")
        return
    
    print("📰 开始获取今日新闻...")
    
    # 获取新闻
    tech_news = get_tech_news()
    finance_news = get_finance_news()
    
    # 构建推送内容
    today = datetime.now().strftime('%Y年%m月%d日')
    
    content = f"# 📊 每日科技财经简报\n**更新日期：{today}**\n\n"
    
    content += "## 🚀 科技前沿\n"
    if tech_news:
        for news in tech_news:
            content += f"- {news}\n\n"
    else:
        content += "暂无科技新闻\n\n"
    
    content += "---\n\n"
    
    content += "## 💰 财经要闻\n"
    if finance_news:
        for news in finance_news:
            content += f"- {news}\n\n"
    else:
        content += "暂无财经新闻\n\n"
    
    content += "---\n\n"
    content += "📌 本推送由 GitHub Actions 自动生成\n"
    content += "⏰ 每天上午8点准时送达\n"
    content += "🔧 新闻源：Hacker News + Product Hunt + Reuters"
    
    # 发送推送
    title = f"📰 每日科技财经简报 {datetime.now().strftime('%m-%d')}"
    print(f"📤 正在发送推送，标题: {title}")
    
    success = send_to_serverchan(title, content, sendkey)
    
    if success:
        print("🎉 今日新闻推送任务完成！")
    else:
        print("❌ 推送任务失败")

if __name__ == "__main__":
    main()