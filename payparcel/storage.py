from whitenoise.storage import CompressedManifestStaticFilesStorage


class SilentCollectstaticStorage(CompressedManifestStaticFilesStorage):
    manifest_strict = False