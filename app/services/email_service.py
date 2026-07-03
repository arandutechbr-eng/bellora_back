import logging
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings

logger = logging.getLogger(__name__)


def _smtp_configured() -> bool:
    return bool(settings.SMTP_HOST and settings.SMTP_USER and settings.SMTP_PASSWORD)


def send_email(to: str, subject: str, html: str) -> bool:
    """
    Envia um e-mail via SMTP. Retorna True se enviado, False se SMTP não configurado.
    Lança exceção em caso de falha de envio com SMTP configurado.
    """
    if not _smtp_configured():
        logger.warning("SMTP não configurado. E-mail para %s não enviado: %s", to, subject)
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.EMAIL_FROM
    msg["To"] = to
    msg.attach(MIMEText(html, "html", "utf-8"))

    context = ssl.create_default_context()
    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.ehlo()
        server.starttls(context=context)
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(settings.EMAIL_FROM, to, msg.as_string())

    logger.info("E-mail enviado para %s: %s", to, subject)
    return True


def send_password_reset_email(to: str, name: str, reset_url: str) -> bool:
    subject = "Redefinição de senha — Bellora"
    html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head><meta charset="UTF-8" /></head>
<body style="margin:0;padding:0;background:#F9FAFB;font-family:'DM Sans',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0">
    <tr>
      <td align="center" style="padding:40px 16px;">
        <table width="560" cellpadding="0" cellspacing="0"
               style="background:#ffffff;border-radius:16px;border:1px solid #E5E7EB;overflow:hidden;">

          <!-- Header -->
          <tr>
            <td style="background:#6C63FF;padding:32px 40px;">
              <h1 style="margin:0;font-size:24px;font-weight:700;color:#ffffff;letter-spacing:-0.5px;">
                Bellora
              </h1>
              <p style="margin:4px 0 0;font-size:13px;color:#D4D0FF;">
                Plataforma de beleza e estética
              </p>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding:40px;">
              <h2 style="margin:0 0 16px;font-size:20px;font-weight:700;color:#1f1f2e;">
                Olá, {name} 👋
              </h2>
              <p style="margin:0 0 24px;font-size:15px;color:#4B5563;line-height:1.6;">
                Recebemos uma solicitação para redefinir a senha da sua conta na Bellora.
                Clique no botão abaixo para criar uma nova senha. O link é válido por
                <strong>1 hora</strong>.
              </p>

              <table cellpadding="0" cellspacing="0">
                <tr>
                  <td style="border-radius:12px;background:#6C63FF;">
                    <a href="{reset_url}"
                       style="display:inline-block;padding:14px 32px;font-size:15px;
                              font-weight:700;color:#ffffff;text-decoration:none;">
                      Redefinir minha senha
                    </a>
                  </td>
                </tr>
              </table>

              <p style="margin:24px 0 0;font-size:13px;color:#9CA3AF;line-height:1.6;">
                Se você não solicitou a redefinição, ignore este e-mail. Sua senha
                permanece a mesma e o link expirará automaticamente.
              </p>
              <p style="margin:12px 0 0;font-size:12px;color:#D1D5DB;">
                Ou acesse este link diretamente:<br/>
                <a href="{reset_url}" style="color:#6C63FF;word-break:break-all;">{reset_url}</a>
              </p>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background:#F9FAFB;padding:20px 40px;border-top:1px solid #E5E7EB;">
              <p style="margin:0;font-size:12px;color:#9CA3AF;text-align:center;">
                © 2026 Bellora · privacidade@bellora.com.br
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""
    return send_email(to, subject, html)
