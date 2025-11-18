#!/usr/bin/env python3
"""
webhook_handler.py - Shopify Webhook Integration for FlowPrint

This module handles incoming Shopify webhooks and renders print templates.
Templates are stored in FlowPrint, and Shopify sends order JSON data.
"""

import hmac
import hashlib
import base64
import json
import os
from jinja2 import Template, Environment, FileSystemLoader
from datetime import datetime

class ShopifyWebhookHandler:
    def __init__(self, templates_dir="print_templates"):
        """Initialize webhook handler with template directory."""
        self.templates_dir = templates_dir
        os.makedirs(templates_dir, exist_ok=True)
        
        # Create Jinja2 environment (similar to Liquid)
        self.jinja_env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=True
        )
    
    def verify_webhook(self, request_body, hmac_header, webhook_secret):
        """
        Verify that the webhook came from Shopify.
        
        Args:
            request_body: Raw request body (bytes)
            hmac_header: X-Shopify-Hmac-Sha256 header value
            webhook_secret: Your Shopify webhook secret
        
        Returns:
            bool: True if valid, False otherwise
        """
        if not hmac_header or not webhook_secret:
            return False
        
        # Compute HMAC
        computed_hmac = hmac.new(
            webhook_secret.encode('utf-8'),
            request_body,
            hashlib.sha256
        ).digest()
        
        # Base64 encode
        computed_hmac_b64 = base64.b64encode(computed_hmac).decode()
        
        # Compare
        return hmac.compare_digest(computed_hmac_b64, hmac_header)
    
    def render_template(self, template_name, order_data):
        """
        Render a template with order data.
        
        Args:
            template_name: Name of template file (e.g., "order_packing.html")
            order_data: Order JSON data from Shopify
        
        Returns:
            str: Rendered HTML
        """
        try:
            template = self.jinja_env.get_template(template_name)
            
            # Add helpful filters and functions
            context = {
                'order': order_data,
                'now': datetime.now(),
                'format_currency': self._format_currency,
                'format_date': self._format_date,
            }
            
            return template.render(**context)
        except Exception as e:
            raise Exception(f"Template rendering failed: {str(e)}")
    
    def _format_currency(self, amount, currency='USD'):
        """Format currency for display."""
        try:
            amount = float(amount)
            symbols = {'USD': '$', 'EUR': '€', 'GBP': '£', 'AUD': 'A$'}
            symbol = symbols.get(currency, currency)
            return f"{symbol}{amount:.2f}"
        except:
            return str(amount)
    
    def _format_date(self, date_str, format='%B %d, %Y'):
        """Format date string."""
        try:
            if isinstance(date_str, str):
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                return dt.strftime(format)
            return str(date_str)
        except:
            return str(date_str)
    
    def create_default_template(self):
        """Create a default packing slip template."""
        default_template = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            margin: 40px;
            font-size: 14px;
        }
        
        .header {
            border-bottom: 3px solid #000;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        
        .header h1 {
            margin: 0;
            font-size: 32px;
            font-weight: 600;
        }
        
        .order-info {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }
        
        .info-section h2 {
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 10px;
            color: #333;
        }
        
        .info-section p {
            margin: 5px 0;
            line-height: 1.6;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 30px;
        }
        
        table th {
            background-color: #f5f5f5;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            border-bottom: 2px solid #ddd;
        }
        
        table td {
            padding: 12px;
            border-bottom: 1px solid #eee;
        }
        
        .totals {
            margin-left: auto;
            width: 300px;
        }
        
        .totals table td {
            border: none;
            padding: 8px;
        }
        
        .totals .total-row {
            font-weight: 600;
            font-size: 16px;
            border-top: 2px solid #000;
        }
        
        .footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            text-align: center;
            color: #666;
        }
        
        @media print {
            body { margin: 0; }
            .no-print { display: none; }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>PACKING SLIP</h1>
        <p style="margin: 5px 0 0 0; color: #666;">Order #{{ order.name }}</p>
    </div>
    
    <div class="order-info">
        <div class="info-section">
            <h2>📦 Ship To</h2>
            <p><strong>{{ order.shipping_address.name }}</strong></p>
            <p>{{ order.shipping_address.address1 }}</p>
            {% if order.shipping_address.address2 %}
            <p>{{ order.shipping_address.address2 }}</p>
            {% endif %}
            <p>{{ order.shipping_address.city }}, {{ order.shipping_address.province_code }} {{ order.shipping_address.zip }}</p>
            <p>{{ order.shipping_address.country }}</p>
            {% if order.shipping_address.phone %}
            <p>Phone: {{ order.shipping_address.phone }}</p>
            {% endif %}
        </div>
        
        <div class="info-section">
            <h2>📋 Order Details</h2>
            <p><strong>Order Number:</strong> {{ order.name }}</p>
            <p><strong>Order Date:</strong> {{ format_date(order.created_at) }}</p>
            <p><strong>Payment Status:</strong> {{ order.financial_status|title }}</p>
            <p><strong>Fulfillment Status:</strong> {{ order.fulfillment_status|title if order.fulfillment_status else 'Unfulfilled' }}</p>
            {% if order.note %}
            <p><strong>Customer Note:</strong><br>{{ order.note }}</p>
            {% endif %}
        </div>
    </div>
    
    <h2>Items to Pack</h2>
    <table>
        <thead>
            <tr>
                <th>Item</th>
                <th>SKU</th>
                <th style="text-align: center;">Quantity</th>
                <th style="text-align: right;">Price</th>
                <th style="text-align: right;">Total</th>
            </tr>
        </thead>
        <tbody>
            {% for item in order.line_items %}
            <tr>
                <td>
                    <strong>{{ item.name }}</strong>
                    {% if item.variant_title and item.variant_title != 'Default Title' %}
                    <br><small style="color: #666;">{{ item.variant_title }}</small>
                    {% endif %}
                </td>
                <td>{{ item.sku if item.sku else '-' }}</td>
                <td style="text-align: center;"><strong>{{ item.quantity }}</strong></td>
                <td style="text-align: right;">{{ format_currency(item.price, order.currency) }}</td>
                <td style="text-align: right;"><strong>{{ format_currency(item.price|float * item.quantity, order.currency) }}</strong></td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    
    <div class="totals">
        <table>
            <tr>
                <td>Subtotal:</td>
                <td style="text-align: right;">{{ format_currency(order.subtotal_price, order.currency) }}</td>
            </tr>
            {% if order.total_discounts|float > 0 %}
            <tr>
                <td>Discounts:</td>
                <td style="text-align: right;">-{{ format_currency(order.total_discounts, order.currency) }}</td>
            </tr>
            {% endif %}
            <tr>
                <td>Shipping:</td>
                <td style="text-align: right;">{{ format_currency(order.total_shipping_price_set.shop_money.amount, order.currency) }}</td>
            </tr>
            <tr>
                <td>Tax:</td>
                <td style="text-align: right;">{{ format_currency(order.total_tax, order.currency) }}</td>
            </tr>
            <tr class="total-row">
                <td>TOTAL:</td>
                <td style="text-align: right;">{{ format_currency(order.total_price, order.currency) }}</td>
            </tr>
        </table>
    </div>
    
    <div class="footer">
        <p>Thank you for your order!</p>
        <p style="font-size: 12px;">Printed {{ now.strftime('%B %d, %Y at %I:%M %p') }}</p>
    </div>
</body>
</html>"""
        
        # Save default template
        template_path = os.path.join(self.templates_dir, "default_packing_slip.html")
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(default_template)
        
        return template_path
    
    def get_available_templates(self):
        """Get list of available template files."""
        if not os.path.exists(self.templates_dir):
            return []
        
        templates = []
        for filename in os.listdir(self.templates_dir):
            if filename.endswith('.html'):
                templates.append(filename)
        
        return sorted(templates)
    
    def save_template(self, template_name, template_content):
        """Save a template to disk."""
        if not template_name.endswith('.html'):
            template_name += '.html'
        
        template_path = os.path.join(self.templates_dir, template_name)
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(template_content)
        
        return template_path
    
    def load_template_content(self, template_name):
        """Load template content for editing."""
        template_path = os.path.join(self.templates_dir, template_name)
        if not os.path.exists(template_path):
            return None
        
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()