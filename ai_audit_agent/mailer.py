"""
Email Service for sending AI Audit Reports
Supports SMTP (Gmail) for sending PDF attachments
"""

import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails with PDF attachments"""
    
    def __init__(self):
        """Initialize email service with SMTP configuration"""
        self.sender_email = os.getenv("SENDER_EMAIL")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "465"))
        
        if not self.sender_email or not self.smtp_password:
            logger.warning("Email credentials not configured. Email sending will be disabled.")
            self.enabled = False
        else:
            self.enabled = True
            logger.info(f"Email service initialized with sender: {self.sender_email}")
    
    def send_report(
        self,
        recipient_email: str,
        recipient_name: str,
        company_name: str,
        personalized_summary: str,
        pdf_path: str
    ) -> bool:
        """
        Send AI audit report via email.
        
        Args:
            recipient_email: Email address of recipient
            recipient_name: Name of recipient
            company_name: Name of company being audited
            personalized_summary: Summary text from LLM analysis
            pdf_path: Path to generated PDF report
            
        Returns:
            True if email sent successfully, False otherwise
        """
        if not self.enabled:
            logger.warning("Email service is not enabled. Skipping email send.")
            return False
        
        try:
            # Create message
            message = self._create_email_message(
                recipient_email,
                recipient_name,
                company_name,
                personalized_summary
            )
            
            # Attach PDF
            if not self._attach_pdf(message, pdf_path, company_name):
                logger.error("Failed to attach PDF to email")
                return False
            
            # Send email
            success = self._send_email(message, recipient_email)
            
            if success:
                logger.info(f"Email sent successfully to {recipient_email}")
            else:
                logger.error(f"Failed to send email to {recipient_email}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}", exc_info=True)
            return False
    
    def _create_email_message(
        self,
        recipient_email: str,
        recipient_name: str,
        company_name: str,
        personalized_summary: str
    ) -> MIMEMultipart:
        """
        Create email message with HTML body.
        
        Args:
            recipient_email: Recipient's email address
            recipient_name: Recipient's name
            company_name: Company name
            personalized_summary: Summary from LLM
            
        Returns:
            MIMEMultipart message object
        """
        message = MIMEMultipart('mixed')
        message['From'] = self.sender_email
        message['To'] = recipient_email
        message['Subject'] = f"AI Audit Report — {company_name}"
        
        # Create HTML body
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background-color: #3498db;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 5px 5px 0 0;
                }}
                .content {{
                    background-color: #f9f9f9;
                    padding: 30px;
                    border: 1px solid #dddddd;
                }}
                .summary-box {{
                    background-color: #ecf0f1;
                    border-left: 4px solid #3498db;
                    padding: 15px;
                    margin: 20px 0;
                }}
                .footer {{
                    background-color: #2c3e50;
                    color: #ecf0f1;
                    padding: 20px;
                    text-align: center;
                    border-radius: 0 0 5px 5px;
                    font-size: 12px;
                }}
                .button {{
                    display: inline-block;
                    padding: 10px 20px;
                    background-color: #27ae60;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 10px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>AI Audit Report</h1>
                </div>
                
                <div class="content">
                    <p>Dear {recipient_name},</p>
                    
                    <p>Please find attached the comprehensive <strong>AI Audit Report</strong> for <strong>{company_name}</strong>.</p>
                    
                    <div class="summary-box">
                        <h3>Executive Summary</h3>
                        <p>{personalized_summary}</p>
                    </div>
                    
                    <p>This report includes:</p>
                    <ul>
                        <li>Detailed department-wise AI readiness analysis</li>
                        <li>Identified gaps and limitations</li>
                        <li>AI maturity visualizations and charts</li>
                        <li>Overall risk assessment</li>
                    </ul>
                    
                    <p>The attached PDF contains comprehensive insights to help understand your organization's current AI maturity level and areas requiring attention.</p>
                    
                    <p>If you have any questions or need further clarification, please don't hesitate to reach out.</p>
                    
                    <p>Best regards,<br>
                    <strong>AI Audit Agent</strong><br>
                    Automated Audit & Analysis System</p>
                </div>
                
                <div class="footer">
                    <p><strong>AI Audit Agent</strong></p>
                    <p>This is an automated report generated by our AI-powered audit system.</p>
                    <p>Confidential Document | For Internal Use Only</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Create plain text alternative
        text_body = f"""
Hi {recipient_name},

Please find attached the AI Audit Report for {company_name}.

Summary:
{personalized_summary}

This report includes detailed department-wise gaps and AI readiness visualizations.

Best regards,
AI Audit Agent
Automated Audit & Analysis System

---
Confidential Document | For Internal Use Only
        """
        
        # Attach both HTML and plain text versions
        part_text = MIMEText(text_body, 'plain')
        part_html = MIMEText(html_body, 'html')
        
        message.attach(part_text)
        message.attach(part_html)
        
        return message
    
    def _attach_pdf(
        self,
        message: MIMEMultipart,
        pdf_path: str,
        company_name: str
    ) -> bool:
        """
        Attach PDF file to email message.
        
        Args:
            message: Email message object
            pdf_path: Path to PDF file
            company_name: Company name for filename
            
        Returns:
            True if attachment successful, False otherwise
        """
        try:
            if not os.path.exists(pdf_path):
                logger.error(f"PDF file not found: {pdf_path}")
                return False
            
            with open(pdf_path, 'rb') as pdf_file:
                pdf_data = pdf_file.read()
            
            # Create attachment
            pdf_attachment = MIMEApplication(pdf_data, _subtype='pdf')
            
            # Generate filename
            safe_company_name = company_name.replace(' ', '_')[:30]
            filename = f"AI_Audit_Report_{safe_company_name}.pdf"
            
            pdf_attachment.add_header(
                'Content-Disposition',
                'attachment',
                filename=filename
            )
            
            message.attach(pdf_attachment)
            
            logger.info(f"PDF attached successfully: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error attaching PDF: {str(e)}", exc_info=True)
            return False
    
    def _send_email(self, message: MIMEMultipart, recipient_email: str) -> bool:
        """
        Send email via SMTP.
        
        Args:
            message: Prepared email message
            recipient_email: Recipient's email address
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Connect to SMTP server
            if self.smtp_port == 465:
                # SSL connection
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)
            else:
                # TLS connection
                server = smtplib.SMTP(self.smtp_host, self.smtp_port)
                server.starttls()
            
            # Login
            server.login(self.sender_email, self.smtp_password)
            
            # Send email
            server.send_message(message)
            
            # Close connection
            server.quit()
            
            logger.info(f"Email sent successfully via {self.smtp_host}:{self.smtp_port}")
            return True
            
        except smtplib.SMTPAuthenticationError:
            logger.error("SMTP authentication failed. Check email credentials.")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error sending email via SMTP: {str(e)}", exc_info=True)
            return False
    
    def test_connection(self) -> bool:
        """
        Test SMTP connection and authentication.
        
        Returns:
            True if connection successful, False otherwise
        """
        if not self.enabled:
            logger.warning("Email service is not enabled")
            return False
        
        try:
            if self.smtp_port == 465:
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)
            else:
                server = smtplib.SMTP(self.smtp_host, self.smtp_port)
                server.starttls()
            
            server.login(self.sender_email, self.smtp_password)
            server.quit()
            
            logger.info("Email service connection test successful")
            return True
            
        except Exception as e:
            logger.error(f"Email service connection test failed: {str(e)}")
            return False
