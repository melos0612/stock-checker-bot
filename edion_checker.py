import time
import schedule
import requests
from bs4 import BeautifulSoup
import re
import smtplib
from email.mime.text import MIMEText

def send_email_notification(subject, body, from_email, to_email, app_password):
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email

    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.starttls()
        smtp.login(from_email, app_password)
        smtp.send_message(msg)

def check_stock_edion(url):
    from_email = "koshi061215@gmail.com"
    to_email   = "koshi061214@gmail.com"
    app_password = "meqv xhfz jexo zznm"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        page_text = soup.get_text()

        if ("在庫数0台" in page_text) or ("売り切れ" in page_text) or ("在庫なし" in page_text):
            print("❌ 売り切れです...")
            return

        match = re.search(r"在庫数(\d+)台", page_text)
        if match:
            count = int(match.group(1))
            if count > 0:
                print(f"✅ 在庫あります！（在庫数{count}台）")
                subject = "【在庫通知】商品が入荷しました"
                body = f"以下の商品が在庫数{count}台で購入可能！\n{url}"
                send_email_notification(subject, body, from_email, to_email, app_password)
                return
            else:
                print("❌ 売り切れです...")
                return

        if ("在庫あり" in page_text) or ("在庫わずか" in page_text) or ("お取り寄せ" in page_text):
            print("✅ 在庫あります！（在庫数不明）")
            subject = "【在庫通知】商品が入荷しました"
            body = f"以下の商品が在庫ありになりました（在庫数は不明）。\n{url}"
            send_email_notification(subject, body, from_email, to_email, app_password)
            return

        print("⚠️ 在庫状態が判別できませんでした")

    except requests.exceptions.RequestException as e:
        print(f"⚠️ ネットワークエラー: {e}")


def job():
    url = "https://www.edion.com/detail.html?p_cd=00057858326&_keyword=%E3%83%81%E3%82%A7%E3%82%AD"
    check_stock_edion(url)

if __name__ == "__main__":
    schedule.every(5).minutes.do(job)
    print("定期実行を開始します... (Ctrl+Cで停止)")

    while True:
        schedule.run_pending()
        time.sleep(1)
