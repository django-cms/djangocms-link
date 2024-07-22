def get_queryset_manager(base):
    if hasattr(base, "drafts"):
        return base.drafts()
    return base
