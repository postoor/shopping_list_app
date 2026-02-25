"""
SMTP 郵件服務：非同步發送邀請信
"""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings


def _render_invitation_html(inviter_name: str, token: str) -> str:
    register_url = f"{settings.FRONTEND_URL}/register?token={token}"
    return f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head><meta charset="UTF-8"><title>購物清單邀請</title></head>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
  <div style="background: linear-gradient(135deg, #667eea, #764ba2); padding: 30px; border-radius: 12px; text-align: center; color: white;">
    <h1 style="margin:0; font-size:28px;">🛒 家庭購物清單</h1>
    <p style="margin:8px 0 0; opacity:.9;">協作管理您的家庭採購</p>
  </div>

  <div style="background: #f9f9f9; padding: 30px; border-radius: 8px; margin: 20px 0;">
    <h2 style="color: #333;">您收到了一封邀請！</h2>
    <p style="color: #555; line-height: 1.6;">
      <strong>{inviter_name}</strong> 邀請您加入「家庭購物清單」，一起協作管理家庭採購計畫。
    </p>
    <div style="text-align: center; margin: 30px 0;">
      <a href="{register_url}"
         style="background: #667eea; color: white; padding: 14px 32px; border-radius: 8px;
                text-decoration: none; font-size: 16px; font-weight: bold; display: inline-block;">
        立即加入 →
      </a>
    </div>
    <p style="color: #999; font-size: 13px; text-align: center;">
      此邀請連結將於 {settings.INVITATION_EXPIRE_HOURS} 小時後失效。<br>
      若非本人操作，請忽略此郵件。
    </p>
  </div>

  <p style="color: #bbb; font-size: 12px; text-align: center;">
    © 家庭購物清單系統 | 此為系統自動發送郵件，請勿回覆
  </p>
</body>
</html>
"""


def send_invitation_email(to_email: str, inviter_name: str, token: str) -> None:
    """同步發信（FastAPI BackgroundTask 呼叫）"""
    if not settings.SMTP_USERNAME:
        # 開發環境：印出連結即可
        register_url = f"{settings.FRONTEND_URL}/register?token={token}"
        print(f"[DEV] 邀請連結 → {register_url}")
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"{inviter_name} 邀請您加入家庭購物清單"
    msg["From"]    = settings.SMTP_FROM
    msg["To"]      = to_email

    html_part = MIMEText(_render_invitation_html(inviter_name, token), "html", "utf-8")
    msg.attach(html_part)

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.ehlo()
        server.starttls()
        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        server.sendmail(settings.SMTP_FROM, [to_email], msg.as_string())
