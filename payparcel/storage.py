from django.contrib.staticfiles.storage import ManifestStaticFilesStorage


class SilentCollectstaticStorage(ManifestStaticFilesStorage):
    def post_process(self, *args, **kwargs):
        for name, hashed_name, processed in super().post_process(*args, **kwargs):
            if isinstance(processed, Exception):
                print(f"Warning: skipping static post-process error for {name}: {processed}")
                continue
            yield name, hashed_name, processed

