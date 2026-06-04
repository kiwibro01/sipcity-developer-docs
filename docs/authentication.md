# Authentication

All API requests across both the CDR and SMS services require the same two headers. We recommend storing your credentials in a secrets manager or environment variable — never hardcode them in your application.

| Header | How to get it |
|--------|---------------|
| `X-Api-Key` | The API Key shown on the CDR integrations page in the portal (Tools → Integrations → CDR) |
| `Authorization` | Basic auth — encode `api_key:api_secret` in base64 and prefix with `Basic ` |

---

## Base64 Encoding Example

If your API key is `cdr_abc123` and your secret is `mysecret`, encode the combined string `cdr_abc123:mysecret`:

```
Input:          cdr_abc123:mysecret
Authorization:  Basic Y2RyX2FiYzEyMzpteXNlY3JldA==
```

### JavaScript

```javascript
const token = btoa('cdr_abc123:mysecret');
const authHeader = `Basic ${token}`;
```

### Python

```python
import base64
token = base64.b64encode(b'cdr_abc123:mysecret').decode()
auth_header = f'Basic {token}'
```

---

> **⚠️ Keep credentials secure**
> Treat your API key and secret like a password. Do not commit them to source control. If a key is compromised, delete it in the portal immediately and create a new one.

> **⚠️ Your API Secret is only shown once**
> The API Secret is displayed in the confirmation dialog only. Once you close it, the secret cannot be retrieved. Download your credentials immediately and store them in a secrets manager or secure vault.
