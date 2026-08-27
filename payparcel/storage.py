from django.contrib.staticfiles.storage import ManifestStaticFilesStorage


class SilentCollectstaticStorage(ManifestStaticFilesStorage):
    manifest_strict = False