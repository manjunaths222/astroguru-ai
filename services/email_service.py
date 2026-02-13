"""Email service for sending astrology analysis reports using Resend"""

import os
import re
from typing import Optional
from config import logger
import resend
from config import AstroConfig


def format_markdown_to_html(text: str) -> str:
    """Convert markdown text to HTML for email with proper formatting"""
    if not text:
        return ""
    
    lines = text.split("\n")
    html_lines = []
    in_list = False
    in_paragraph = False
    current_paragraph = []
    
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        stripped = line.strip()
        
        # Skip empty lines (close current structures)
        if not stripped:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            if in_paragraph:
                html_lines.append("</p>")
                in_paragraph = False
            i += 1
            continue
        
        # Headers
        if stripped.startswith("#### "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            if in_paragraph:
                html_lines.append("</p>")
                in_paragraph = False
            html_lines.append(f"<h4>{stripped[5:]}</h4>")
        elif stripped.startswith("### "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            if in_paragraph:
                html_lines.append("</p>")
                in_paragraph = False
            html_lines.append(f"<h3>{stripped[4:]}</h3>")
        elif stripped.startswith("## "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            if in_paragraph:
                html_lines.append("</p>")
                in_paragraph = False
            html_lines.append(f"<h2>{stripped[3:]}</h2>")
        elif stripped.startswith("# "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            if in_paragraph:
                html_lines.append("</p>")
                in_paragraph = False
            html_lines.append(f"<h1>{stripped[2:]}</h1>")
        # Horizontal rule
        elif stripped.startswith("---") or stripped == "---":
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            if in_paragraph:
                html_lines.append("</p>")
                in_paragraph = False
            html_lines.append("<hr>")
        # List items
        elif stripped.startswith("- ") or stripped.startswith("* ") or (stripped[0].isdigit() and ". " in stripped[:5]):
            if in_paragraph:
                html_lines.append("</p>")
                in_paragraph = False
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            # Remove list marker
            content = stripped
            if content.startswith("- "):
                content = content[2:]
            elif content.startswith("* "):
                content = content[2:]
            elif ". " in content[:5]:
                idx = content.find(". ")
                if idx > 0:
                    content = content[idx + 2:]
            html_lines.append(f"<li>{process_inline_markdown(content)}</li>")
        # Regular paragraph text
        else:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            if not in_paragraph:
                html_lines.append("<p>")
                in_paragraph = True
            else:
                html_lines.append("<br>")
            html_lines.append(process_inline_markdown(stripped))
        
        i += 1
    
    # Close any open structures
    if in_list:
        html_lines.append("</ul>")
    if in_paragraph:
        html_lines.append("</p>")
    
    return "".join(html_lines)


def process_inline_markdown(text: str) -> str:
    """Process inline markdown formatting (bold, italic, etc.)"""
    if not text:
        return ""
    
    # Escape HTML special characters first
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    
    # Bold (**text** or __text__)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'__(.+?)__', r'<strong>\1</strong>', text)
    
    # Italic (*text* or _text_)
    text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<em>\1</em>', text)
    text = re.sub(r'(?<!_)_(?!_)(.+?)(?<!_)_(?!_)', r'<em>\1</em>', text)
    
    # Code (`text`)
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    
    return text


def create_email_html(
    name: str,
    summary: str,
    chart_analysis: Optional[str] = None,
    dasha_analysis: Optional[str] = None,
    goal_analysis: Optional[str] = None,
    recommendations: Optional[str] = None
) -> str:
    """Create beautifully formatted HTML email content"""
    
    summary_html = format_markdown_to_html(summary)
    chart_html = format_markdown_to_html(chart_analysis) if chart_analysis else None
    dasha_html = format_markdown_to_html(dasha_analysis) if dasha_analysis else None
    goal_html = format_markdown_to_html(goal_analysis) if goal_analysis else None
    recommendations_html = format_markdown_to_html(recommendations) if recommendations else None
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Your AstroGuru AI Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333333;
            background-color: #f5f5f5;
            padding: 20px;
        }}
        .email-container {{
            max-width: 700px;
            margin: 0 auto;
            background-color: #ffffff;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        .email-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #ffffff;
            padding: 40px 30px;
            text-align: center;
        }}
        .email-header h1 {{
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 10px;
            color: #ffffff;
        }}
        .email-header p {{
            font-size: 16px;
            opacity: 0.95;
            margin: 0;
        }}
        .email-content {{
            padding: 40px 30px;
        }}
        .greeting {{
            font-size: 18px;
            color: #333333;
            margin-bottom: 30px;
            line-height: 1.8;
        }}
        .section {{
            margin-bottom: 35px;
            padding: 25px;
            background-color: #f9f9f9;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        .section h2 {{
            color: #667eea;
            font-size: 24px;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e0e0e0;
        }}
        .section h3 {{
            color: #555555;
            font-size: 20px;
            margin-top: 20px;
            margin-bottom: 12px;
        }}
        .section h4 {{
            color: #666666;
            font-size: 18px;
            margin-top: 15px;
            margin-bottom: 10px;
        }}
        .section p {{
            margin-bottom: 12px;
            color: #444444;
            line-height: 1.8;
        }}
        .section ul {{
            margin-left: 20px;
            margin-bottom: 15px;
        }}
        .section li {{
            margin-bottom: 8px;
            color: #444444;
            line-height: 1.7;
        }}
        .section strong {{
            color: #333333;
            font-weight: 600;
        }}
        .section hr {{
            border: none;
            border-top: 1px solid #e0e0e0;
            margin: 20px 0;
        }}
        .email-footer {{
            background-color: #f9f9f9;
            padding: 30px;
            text-align: center;
            border-top: 1px solid #e0e0e0;
        }}
        .email-footer p {{
            color: #666666;
            font-size: 14px;
            margin: 5px 0;
        }}
        .divider {{
            height: 1px;
            background: linear-gradient(to right, transparent, #e0e0e0, transparent);
            margin: 30px 0;
        }}
        @media only screen and (max-width: 600px) {{
            .email-container {{
                width: 100% !important;
            }}
            .email-header {{
                padding: 30px 20px;
            }}
            .email-header h1 {{
                font-size: 26px;
            }}
            .email-content {{
                padding: 30px 20px;
            }}
            .section {{
                padding: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="email-header">
            <h1>✨ AstroGuru AI</h1>
            <p>Your Personal Vedic Astrology Report</p>
        </div>
        
        <div class="email-content">
            <div class="greeting">
                <p>Dear <strong>{name}</strong>,</p>
                <p>Thank you for using AstroGuru AI! Your personalized astrology analysis is ready. We hope this report provides valuable insights into your life's journey.</p>
            </div>
            
            <div class="section">
                <h2>📋 Your Astrology Report</h2>
                <div>{summary_html}</div>
            </div>
"""
    
    if chart_html:
        html_content += f"""
            <div class="divider"></div>
            
            <div class="section">
                <h2>📊 Birth Chart Analysis</h2>
                <div>{chart_html}</div>
            </div>
"""
    
    if dasha_html:
        html_content += f"""
            <div class="divider"></div>
            
            <div class="section">
                <h2>⏰ Current Life Period (Dasha)</h2>
                <div>{dasha_html}</div>
            </div>
"""
    
    if goal_html:
        html_content += f"""
            <div class="divider"></div>
            
            <div class="section">
                <h2>🎯 Goal-Specific Analysis</h2>
                <div>{goal_html}</div>
            </div>
"""
    
    if recommendations_html:
        html_content += f"""
            <div class="divider"></div>
            
            <div class="section">
                <h2>💡 Recommendations & Remedies</h2>
                <div>{recommendations_html}</div>
            </div>
"""
    
    html_content += """
        </div>
        
        <div class="email-footer">
            <p><strong>AstroGuru AI</strong></p>
            <p>Your Personal Vedic Astrology Guide</p>
            <p style="margin-top: 15px; font-size: 12px; color: #999999;">
                This report was generated using advanced AI and Vedic astrology principles.<br>
                For questions or follow-up analysis, please visit our website.
            </p>
        </div>
    </div>
</body>
</html>
"""
    
    return html_content


async def send_analysis_email(
    email: str,
    name: str,
    summary: str,
    chart_analysis: Optional[str] = None,
    dasha_analysis: Optional[str] = None,
    goal_analysis: Optional[str] = None,
    recommendations: Optional[str] = None
) -> bool:
    """Send astrology analysis report via email using Resend API"""
    try:
        # Get Resend API key from environment
        resend_api_key = AstroConfig.AppSettings.RESEND_API_KEY
        from_email = AstroConfig.AppSettings.RESEND_FROM_EMAIL
        from_name = AstroConfig.AppSettings.RESEND_FROM_NAME

        if not resend_api_key:
            logger.error("RESEND_API_KEY not configured. Please set RESEND_API_KEY environment variable.")
            logger.error("Get your API key from: https://resend.com/api-keys")
            return False
        
        # Initialize Resend with API key
        resend.api_key = resend_api_key
        
        # Create email content
        html_content = create_email_html(
            name=name,
            summary=summary,
            chart_analysis=chart_analysis,
            dasha_analysis=dasha_analysis,
            goal_analysis=goal_analysis,
            recommendations=recommendations
        )
        
        # Create plain text version (simplified)
        plain_text = f"""Dear {name},

Thank you for using AstroGuru AI! Your personalized astrology analysis is ready.

{summary}
"""
        if chart_analysis:
            plain_text += f"\n\nBirth Chart Analysis:\n{chart_analysis}\n"
        if dasha_analysis:
            plain_text += f"\n\nCurrent Life Period:\n{dasha_analysis}\n"
        if goal_analysis:
            plain_text += f"\n\nGoal Analysis:\n{goal_analysis}\n"
        if recommendations:
            plain_text += f"\n\nRecommendations:\n{recommendations}\n"
        
        plain_text += "\n\n---\nAstroGuru AI - Your Personal Vedic Astrology Guide"
        
        # Prepare email parameters for Resend
        params = {
            "from": f"{from_name} <{from_email}>",
            "to": [email],
            "subject": f"✨ Your Astrology Report - {name}",
            "html": html_content,
            "text": plain_text,
        }
        
        # Send email using Resend API (synchronous call, wrapped in async for proper execution)
        import asyncio
        email_response = await asyncio.to_thread(resend.Emails.send, params)
        
        if email_response:
            # Resend returns a dict with 'id' key on success
            email_id = email_response.get('id') if isinstance(email_response, dict) else getattr(email_response, 'id', None)
            if email_id:
                logger.info(f"Analysis email sent successfully to {email} for {name} (Resend ID: {email_id})")
            else:
                logger.info(f"Analysis email sent successfully to {email} for {name}")
            return True
        else:
            logger.warning(f"Email sent but no response received for {email}")
            return True  # Still return True as email was likely sent
        
    except Exception as e:
        # Catch all exceptions (Resend SDK may raise various exceptions)
        error_type = type(e).__name__
        logger.error(f"Failed to send email to {email} ({error_type}): {e}", exc_info=True)
        return False

