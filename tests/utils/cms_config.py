from cms.app_base import CMSAppConfig


class UtilCMSAppConfig(CMSAppConfig):
    djangocms_link_enabled = True
    djangocms_link_models = ["utils.thirdpartymodel"]
