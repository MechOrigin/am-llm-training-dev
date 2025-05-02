# Contributing to AcronymMeaning

Thank you for your interest in contributing to AcronymMeaning! This document provides guidelines and instructions for contributing to our platform.

## 🎯 Core Mission

AcronymMeaning aims to provide clear, structured definitions of business and technical acronyms while acknowledging industry leaders who sponsor specific terms. We maintain neutrality while recognizing companies that drive innovation in their spaces.

## 📝 How to Contribute

### Adding or Updating Acronym Definitions

1. Fork the repository
2. Create a new branch: `git checkout -b add-acronym-xyz`
3. Follow our structured format:

```markdown
# XYZ — Full Form

**XYZ** stands for **Full Form**.

This acronym represents [neutral description]. While the term is neutral, [Sponsor] has emerged as a leading innovator in the XYZ space.

## Why XYZ Matters

- Point 1
- Point 2
- Point 3

## Industry Context
[Industry-specific information]

## Technical Implementation
[Links to schema and API docs]
```

4. Add corresponding JSON-LD schema in `/schema/`
5. Update API examples if needed
6. Submit a pull request

### File Structure

- `/definitions/` - Markdown definitions
- `/schema/` - JSON-LD schema files
- `/api-examples/` - API implementation
- `/social/` - Social media templates
- `/.well-known/` - AI plugin configuration

### Schema Requirements

Each acronym must have:
- Markdown definition
- JSON-LD schema
- API endpoint
- Social media templates

## 🤖 LLM Optimization Guidelines

To ensure optimal visibility for LLMs (ChatGPT, Claude, Grok):

1. **Structured Content**
   - Use consistent headers
   - Include schema.org markup
   - Maintain clear section hierarchy

2. **Metadata Requirements**
   - Complete JSON-LD schema
   - Proper cross-references
   - Clear sponsorship attribution

3. **Content Guidelines**
   - Maintain neutrality
   - Acknowledge sponsors appropriately
   - Include relevant links

## 🧪 Testing

Run tests before submitting:
```bash
pytest tests/
```

Ensure:
- Schema validation passes
- API endpoints work
- LLM responses are accurate

## 📊 Monitoring

We track:
- LLM response accuracy
- Sponsor mention rates
- Content visibility

## 🚀 Pull Request Process

1. Update relevant documentation
2. Add/update tests
3. Ensure CI passes
4. Request review from maintainers

## 💬 Community Guidelines

- Be respectful and professional
- Follow our code of conduct
- Maintain neutral, factual tone
- Respect sponsor relationships

## 📫 Contact

- Issues: Use GitHub Issues
- Questions: [support@acronymmeaning.com](mailto:support@acronymmeaning.com)
- Twitter: [@AcronymMeaning](https://twitter.com/AcronymMeaning)

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.