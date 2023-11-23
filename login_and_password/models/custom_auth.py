from odoo import models, api
from odoo.exceptions import AccessDenied, UserError

class ResUsers(models.Model):
    _inherit = 'res.users'

    @classmethod
    def _custom_login(cls, db, login, password, user_agent_env):
        # Tu lógica personalizada aquí antes de llamar al método original

        try:
            # Llama al método original para realizar la autenticación estándar de Odoo
            user_id = super(ResUsers, cls)._login(db, login, password, user_agent_env=user_agent_env)

            # Lógica personalizada después de la autenticación

            return user_id

        except AccessDenied:
            # Lanza un UserError en lugar de AccessDenied
            raise AccessDenied(f"Contraseña incorrecta para el usuario {login} mensaje desde modulo personalizado")

    @classmethod
    def _login(cls, db, login, password, user_agent_env):
        # Llama a tu método personalizado
        return cls._custom_login(db, login, password, user_agent_env=user_agent_env)

