# Translation Vendor APIs

!!! abstract "In a nutshell"
    Code written for DeepL, Amazon Translate, LibreTranslate, Azure Translator or Google Cloud Translation can get its translation from your own OVOS translation plugin. Point the SDK at `ovos-translate-server`. The request and the response keep the shape of the vendor API.

## What you can do

`ovos-translate-server` mounts each vendor API under its own prefix. The translation comes from the OVOS plugin that the server runs.

## User stories

The recipes ran against `ovos-translate-server --tx-engine ovos-google-translate-plugin`.

### I have code for the DeepL SDK

Set `server_url` to the `/deepl/` prefix, with the trailing slash. The SDK joins its paths to `server_url` with `urllib.parse.urljoin`. Without the slash, `urljoin` drops `deepl`, and the SDK gets `Not found`. This recipe used `deepl` 1.32.0.

```python
import deepl

translator = deepl.Translator("unused:fx", server_url="http://localhost:9686/deepl/")
print(translator.translate_text("good morning", target_lang="PT-PT").text)
print(translator.translate_text("good morning", source_lang="EN", target_lang="DE").text)
print([r.text for r in translator.translate_text(["good morning", "thank you"], target_lang="FR")])
```

```text
bom dia
Guten Morgen
['bonjour', 'merci']
```

### I have code for Amazon Translate through boto3

Set `endpoint_url` to the `/amazon` prefix. Any credentials work. `SourceLanguageCode="auto"` also works. This recipe used `boto3` 1.43.115.

```python
import boto3

client = boto3.client("translate", endpoint_url="http://localhost:9686/amazon", region_name="us-east-1",
                      aws_access_key_id="x", aws_secret_access_key="x")
print(client.translate_text(Text="good morning", SourceLanguageCode="en",
                            TargetLanguageCode="pt")["TranslatedText"])
```

```text
bom dia
```

### I have code for another vendor SDK

These clients sent requests to the same server. Each line is what the client returned.

| Client | Setting | Call | Output |
| :--- | :--- | :--- | :--- |
| `libretranslatepy` 2.1.4 | `LibreTranslateAPI("http://localhost:9686/libretranslate/")` | `lt.translate("good morning", "en", "pt")` | `bom dia` |
| `azure-ai-translation-text` 1.0.1 | `TextTranslationClient(endpoint="http://localhost:9686/azure", credential=AzureKeyCredential("x"))` | `client.translate(body=["good morning"], to_language=["de"], from_language="en")` | `Guten Morgen` |
| `google-cloud-translate` 3.28.0 (`translate_v2`) | `client_options={"api_endpoint": "http://localhost:9686/google"}`, `AnonymousCredentials()` | `client.translate("good morning", target_language="pt")` | `bom dia` |

### I want language detection

Start the server with a detection plugin: `--detect-engine <plugin>`. Some translation plugins cannot detect languages. With such a plugin and no detection plugin, the detect calls answer with an error or with the language `und`.

## Endpoint status

| Vendor | Client | Status |
| :--- | :--- | :--- |
| DeepL | `deepl` SDK `translate_text` | Works |
| Amazon Translate | `boto3` `translate_text` | Works |
| LibreTranslate | `libretranslatepy` `translate` | Works |
| Azure Translator | `azure-ai-translation-text` `translate` | Works |
| Google Cloud Translation v2 | `google-cloud-translate` `translate_v2` | Works |
| All vendors | language lists | Works. The list is empty when the translation plugin does not report its languages |

[Server Compatibility Layers](server-compat-layers.md) lists the other translation prefixes.

## Troubleshooting

| Problem | Cause | Fix |
| :--- | :--- | :--- |
| The DeepL SDK gets `Not found` | `server_url` has no trailing slash | Use `http://<host>:9686/deepl/` |
| A detect call fails | No plugin can detect languages | Start the server with `--detect-engine <plugin>` |
| The language list is empty | The translation plugin does not report its languages | Send the language codes that the plugin supports |

---
**Read next:** [Server Compatibility Layers](server-compat-layers.md)
**Related:** [Drop-in Vendor APIs](vendor-apis.md) · [Translate Server](translate-server.md) · [Text-to-speech vendor APIs](vendor-api-tts.md)
