# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly:

1. **Do not** open a public GitHub issue
2. Email [maanik.p.garg@gmail.com](mailto:maanik.p.garg@gmail.com) with:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
3. Allow 48 hours for an initial response

## Security Considerations

- **API Keys**: Never commit API keys. Use `.env` files (excluded via `.gitignore`) or environment variables
- **Redis**: The semantic cache stores query embeddings in Redis. Deploy Redis with authentication enabled in production
- **Input Validation**: All API inputs are validated via Pydantic models with field constraints
- **Dependencies**: Regularly update dependencies to patch known vulnerabilities
