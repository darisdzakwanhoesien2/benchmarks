# Streamlit Upload Limits

The Bulk OCR page accepts large PDF files. Two layers can reject uploads before Python code runs:

1. Streamlit upload settings.
2. The reverse proxy in front of Streamlit, usually Nginx.

This repository includes:

```toml
[server]
maxUploadSize = 1024
maxMessageSize = 1024
```

in `.streamlit/config.toml`, which raises the Streamlit limit to 1024 MB.

If the browser still shows HTTP 413, raise the proxy limit too. For Nginx, add this inside the relevant `server` or `location` block:

```nginx
client_max_body_size 1024M;
proxy_read_timeout 600s;
proxy_send_timeout 600s;
```

Then reload Nginx:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

If proxy upload limits are inconvenient, use the Bulk OCR page's **Use existing files on server** mode:

```bash
scp *.pdf ubuntu@YOUR_VPS_IP:/path/to/new_page/data/thesis_pdf/
```

Then select those files from the Streamlit page. This avoids browser upload entirely.
