import json
import requests
from odoo import models, fields, api

class VirtualUser(models.Model):
    _name = 'virtual.user'
    _description = 'Virtual User'

    name = fields.Char('Name', required=True)
    password = fields.Char('Password', required=True)

    @api.model
    def generate_user_password(self):
        try:
            for i in range(10):
                endpoint_url = 'https://www.marlonfalcon.com/api/password/21'

                response = requests.get(endpoint_url)

                if response.status_code == 200:
                    data = response.json()
                    new_password = data.get('password', '')

                    user_name = self.env['ir.sequence'].next_by_code('virtual.user') or 'New'
                    
                    user_vals = {
                        'name': user_name,
                        'login': user_name,
                        'password': new_password,
                    }
                    print(user_vals)
                    existing_user = self.env['res.users'].search([('login', '=', user_vals['login'])])
                    if not existing_user:
                        self.env['res.users'].create(user_vals)
                    else:
                        print(f'User with login {user_vals["login"]} already exists. Duplicate not created.')
                else:
                    print(f'Error fetching the new password. Status code: {response.status_code}')

        except Exception as e:
            print(f'Connection error: {str(e)}')