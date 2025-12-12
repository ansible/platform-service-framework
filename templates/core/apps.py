from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"

    def ready(self):
        from ansible_base.rbac.triggers import dab_post_migrate

        dab_post_migrate.connect(
            self._create_managed_roles,
            dispatch_uid="core.create_managed_roles",
        )

    @staticmethod
    def _create_managed_roles(sender, **kwargs):
        from ansible_base.rbac import permission_registry
        from django.apps import apps

        permission_registry.create_managed_roles(apps)
