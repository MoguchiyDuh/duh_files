# translate

Live translate-shell (`trans`) provider. Query text is translated to
`target_lang` (default `en`) as you type, with the result streamed back
asynchronously (no blocking, no chained dialogs).

Activate with the `copy` action to copy the translated text to the
clipboard via `wl-copy`.
